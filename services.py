import os
import re
import shutil
import zipfile
import asyncio
from pathlib import Path
from fastapi import UploadFile

from validacao import validar_senha, esta_bloqueado

TAMANHO_MAXIMO_MB = 500
TAMANHO_MAXIMO_BYTES = TAMANHO_MAXIMO_MB * 1024 * 1024
CHUNK_SIZE = 1024 * 1024  # 1 MB por chunk

# Configurações de serviço
_configuracao = {
    "diretorio_saida": Path("recebidos").resolve(),
    "auto_aceitar": False,
    "salvar_em_zip": False,
}

_confirm_lock = asyncio.Lock()


def configurar_servico(diretorio_saida: Path | str | None = None, auto_aceitar: bool = False, salvar_em_zip: bool = False):
    if diretorio_saida:
        p = Path(diretorio_saida).resolve()
    else:
        p = (Path.cwd() / "recebidos").resolve()

    p.mkdir(parents=True, exist_ok=True)
    _configuracao["diretorio_saida"] = p
    _configuracao["auto_aceitar"] = auto_aceitar
    _configuracao["salvar_em_zip"] = salvar_em_zip


def obter_diretorio_saida() -> Path:
    return _configuracao["diretorio_saida"]


def sanitizar_nome(nome_original: str) -> str:
    """Sanitiza o nome do arquivo para evitar path traversal no Linux e Windows."""
    nome = Path(nome_original or "").name.replace("\\", "/").split("/")[-1].strip()
    nome_limpo = re.sub(r'[^\w\s\.-]', '_', nome).strip()
    return nome_limpo or "arquivo_recebido"


def _gerar_destino_unico(pasta: Path, nome_arquivo: str) -> Path:
    destino = pasta / nome_arquivo
    if not destino.exists():
        return destino

    stem = destino.stem
    suffix = destino.suffix
    i = 1
    while True:
        candidato = pasta / f"{stem}_{i}{suffix}"
        if not candidato.exists():
            return candidato
        i += 1


def _gerar_nome_unico_zip(zipf: zipfile.ZipFile, nome_arquivo: str) -> str:
    nomes_existentes = set(zipf.namelist())
    if nome_arquivo not in nomes_existentes:
        return nome_arquivo

    p = Path(nome_arquivo)
    stem = p.stem
    suffix = p.suffix
    i = 1
    while True:
        candidato = f"{stem}_{i}{suffix}"
        if candidato not in nomes_existentes:
            return candidato
        i += 1


def enviar_texto_service(texto: str, senha: str, ip_cliente: str | None = None) -> str:
    if ip_cliente and esta_bloqueado(ip_cliente):
        return "bloqueado"

    if not validar_senha(senha, ip_cliente):
        return "senha_invalida"

    print("\n\033[1;32m[+] Nova Mensagem Recebida:\033[0m")
    print(f"\033[36m{texto}\033[0m\n")
    return "ok"


def _confirmar_recebimento_terminal(nome: str, tamanho_kb: float, content_type: str) -> bool:
    print("\n\033[1;33m--- Novo arquivo recebido ---\033[0m")
    print(f"Nome: {nome}")
    print(f"Tamanho: {tamanho_kb:.2f} KB")
    print(f"Tipo: {content_type or 'desconhecido'}")
    try:
        resposta = input("Deseja aceitar este arquivo? (s/n): ").strip().lower()
        return resposta in ("s", "sim", "y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


async def enviar_arquivo_service(arquivo: UploadFile, senha: str, ip_cliente: str | None = None) -> dict:
    if ip_cliente and esta_bloqueado(ip_cliente):
        return {"status": "bloqueado"}

    if not validar_senha(senha, ip_cliente):
        return {"status": "senha_invalida"}

    nome_seguro = sanitizar_nome(arquivo.filename)
    pasta_destino = obter_diretorio_saida()
    arquivo_temp = pasta_destino / f".temp_{nome_seguro}"

    # Streaming em chunks para evitar sobrecarga de memória RAM
    total_lido = 0
    try:
        with open(arquivo_temp, "wb") as f_out:
            while True:
                chunk = await arquivo.read(CHUNK_SIZE)
                if not chunk:
                    break
                total_lido += len(chunk)
                if total_lido > TAMANHO_MAXIMO_BYTES:
                    f_out.close()
                    if arquivo_temp.exists():
                        arquivo_temp.unlink()
                    print(f"\033[31m[!] Arquivo recusado: excede o limite de {TAMANHO_MAXIMO_MB}MB.\033[0m")
                    return {"status": "arquivo_grande", "limite_mb": TAMANHO_MAXIMO_MB}
                f_out.write(chunk)
    except Exception as e:
        if arquivo_temp.exists():
            arquivo_temp.unlink()
        return {"status": "erro", "detalhe": str(e)}

    tamanho_kb = total_lido / 1024

    # Confirmação do recebimento (com lock para evitar concorrência no terminal)
    auto_aceitar = _configuracao.get("auto_aceitar", False)
    if auto_aceitar:
        aceitar = True
        print(f"\033[32m[+] Arquivo aceito automaticamente: {nome_seguro} ({tamanho_kb:.2f} KB)\033[0m")
    else:
        async with _confirm_lock:
            try:
                aceitar = await asyncio.wait_for(
                    asyncio.to_thread(
                        _confirmar_recebimento_terminal,
                        nome_seguro,
                        tamanho_kb,
                        arquivo.content_type,
                    ),
                    timeout=60.0
                )
            except asyncio.TimeoutError:
                print(f"\033[31m[!] Tempo esgotado para confirmação de: {nome_seguro}\033[0m")
                if arquivo_temp.exists():
                    arquivo_temp.unlink()
                return {"status": "timeout"}

    if not aceitar:
        if arquivo_temp.exists():
            arquivo_temp.unlink()
        print(f"\033[31m[-] Arquivo recusado: {nome_seguro}\033[0m")
        return {"status": "recusado"}

    salvar_em_zip = _configuracao.get("salvar_em_zip", False)

    if salvar_em_zip:
        caminho_zip = pasta_destino / "arquivos_recebidos.zip"
        modo = "a" if caminho_zip.exists() else "w"

        with zipfile.ZipFile(caminho_zip, modo, zipfile.ZIP_DEFLATED) as zipf:
            nome_final = _gerar_nome_unico_zip(zipf, nome_seguro)
            zipf.write(arquivo_temp, arcname=nome_final)

        if arquivo_temp.exists():
            arquivo_temp.unlink()

        print(f"\033[32m[+] Arquivo salvo no ZIP ({caminho_zip.name}): {nome_final}\033[0m")
        return {"status": "ok", "nome_arquivo": nome_final, "tamanho_kb": round(tamanho_kb, 2), "zip": True}

    else:
        destino_final = _gerar_destino_unico(pasta_destino, nome_seguro)
        shutil.move(str(arquivo_temp), str(destino_final))
        print(f"\033[32m[+] Arquivo salvo com sucesso em: {destino_final}\033[0m")
        return {"status": "ok", "nome_arquivo": destino_final.name, "tamanho_kb": round(tamanho_kb, 2), "zip": False}


def listar_arquivos_disponiveis(senha: str, ip_cliente: str | None = None):
    """Lista os arquivos salvos disponíveis para download."""
    if ip_cliente and esta_bloqueado(ip_cliente):
        return None

    if not validar_senha(senha, ip_cliente):
        return None

    pasta = obter_diretorio_saida()
    arquivos = []
    for item in pasta.iterdir():
        if item.is_file() and not item.name.startswith("."):
            arquivos.append({
                "nome": item.name,
                "tamanho_kb": round(item.stat().st_size / 1024, 2),
                "modificado": int(item.stat().st_mtime)
            })
    return sorted(arquivos, key=lambda x: x["modificado"], reverse=True)


def obter_caminho_para_download(nome_arquivo: str, senha: str, ip_cliente: str | None = None) -> Path | None:
    """Verifica e retorna o caminho absoluto para download, prevenindo path traversal."""
    if ip_cliente and esta_bloqueado(ip_cliente):
        return None

    if not validar_senha(senha, ip_cliente):
        return None

    pasta = obter_diretorio_saida()
    nome_seguro = sanitizar_nome(nome_arquivo)
    caminho = (pasta / nome_seguro).resolve()

    # Prevenção rigorosa de path traversal
    if caminho.is_file() and pasta in caminho.parents:
        return caminho
    return None
