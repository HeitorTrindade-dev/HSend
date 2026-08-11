import zipfile
import os
import asyncio
from validacao import validar_senha

TAMANHO_MAXIMO_MB = 500
TAMANHO_MAXIMO_BYTES = TAMANHO_MAXIMO_MB * 1024 * 1024


def enviar_texto_service(texto, senha):
    if validar_senha(senha):
        print(f"\033[32mMensagem recebida: {texto}\033[0m")
        return True
    return False


def _confirmar_recebimento(nome, tamanho_kb, content_type):
    print("\n\033[33m--- Novo arquivo recebido ---\033[0m")
    print(f"Nome: {nome}")
    print(f"Tamanho: {tamanho_kb:.2f} KB")
    print(f"Tipo: {content_type}")
    resposta = input("Deseja aceitar este arquivo? (s/n): ").strip().lower()
    return resposta == "s"


async def enviar_arquivo_service(arquivo, senha):
    if not validar_senha(senha):
        return "senha_invalida"

    conteudo = await arquivo.read()

    if len(conteudo) > TAMANHO_MAXIMO_BYTES:
        print(f"\033[31mArquivo recusado: excede o limite de {TAMANHO_MAXIMO_MB}MB.\033[0m")
        return "arquivo_grande"

    tamanho_kb = len(conteudo) / 1024

    aceitar = await asyncio.to_thread(
        _confirmar_recebimento, arquivo.filename, tamanho_kb, arquivo.content_type
    )

    if not aceitar:
        print("\033[31mArquivo recusado.\033[0m")
        return "recusado"

    caminho_zip = "arquivos_recebidos.zip"
    modo = "a" if os.path.exists(caminho_zip) else "w"

    # sanitiza o nome vindo do cliente para evitar zip slip / path traversal
    nome_final = os.path.basename(arquivo.filename or "") or "arquivo_sem_nome"

    with zipfile.ZipFile(caminho_zip, modo, zipfile.ZIP_DEFLATED) as zipf:
        nomes_existentes = zipf.namelist()

        if nome_final in nomes_existentes:
            base, ext = os.path.splitext(nome_final)
            nome_final = f"{base}_novo{ext}"

        zipf.writestr(nome_final, conteudo)

    print(f"\033[32mArquivo salvo no zip: {nome_final}\033[0m")
    return "ok"
