from pathlib import Path

from fastapi import APIRouter, Form, UploadFile, File, HTTPException, Request, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from services import (
    enviar_texto_service,
    enviar_arquivo_service,
    listar_arquivos_disponiveis,
    obter_caminho_para_download,
    TAMANHO_MAXIMO_MB,
)
from validacao import senha_configurada

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent


@router.get("/")
def ler_raiz():
    return FileResponse(BASE_DIR / "static" / "index.html")


@router.get("/api/info")
def obter_info():
    return {
        "senha_necessaria": senha_configurada(),
        "limite_mb": TAMANHO_MAXIMO_MB,
    }


class MensagemPayload(BaseModel):
    mensagem: str
    senha: str = ""


@router.post("/enviar/texto")
def enviar_texto_controller(dados: MensagemPayload, request: Request):
    ip_cliente = request.client.host if request.client else None
    resultado = enviar_texto_service(dados.mensagem, dados.senha, ip_cliente)

    if resultado == "bloqueado":
        raise HTTPException(
            status_code=429,
            detail="Muitas tentativas incorretas. Temporariamente bloqueado por 60 segundos."
        )

    if resultado == "senha_invalida":
        raise HTTPException(status_code=401, detail="Senha incorreta")

    return {"status": "ok"}


@router.post("/enviar/arquivo")
async def enviar_arquivo_controller(
    request: Request,
    senha: str = Form(default=""),
    arquivo: UploadFile = File(...)
):
    ip_cliente = request.client.host if request.client else None
    resultado = await enviar_arquivo_service(arquivo, senha, ip_cliente)

    status = resultado.get("status")

    if status == "bloqueado":
        raise HTTPException(
            status_code=429,
            detail="Muitas tentativas incorretas. Temporariamente bloqueado por 60 segundos."
        )

    if status == "senha_invalida":
        raise HTTPException(status_code=401, detail="Senha incorreta")

    if status == "arquivo_grande":
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo excede o limite máximo permitido de {resultado.get('limite_mb', TAMANHO_MAXIMO_MB)}MB."
        )

    if status == "timeout":
        raise HTTPException(
            status_code=408,
            detail="Tempo limite de confirmação esgotado no servidor."
        )

    if status == "recusado":
        return {"status": "recusado", "mensagem": "Arquivo recusado pelo operador no terminal."}

    if status != "ok":
        raise HTTPException(status_code=500, detail=resultado.get("detalhe", "Erro interno no processamento."))

    return {
        "status": "ok",
        "nome_arquivo": resultado.get("nome_arquivo", arquivo.filename),
        "tamanho_kb": resultado.get("tamanho_kb", 0),
        "zip": resultado.get("zip", False)
    }


@router.get("/arquivos")
def listar_arquivos_controller(request: Request, senha: str = Query(default="")):
    ip_cliente = request.client.host if request.client else None
    arquivos = listar_arquivos_disponiveis(senha, ip_cliente)

    if arquivos is None:
        raise HTTPException(status_code=401, detail="Senha incorreta ou acesso bloqueado")

    return {"status": "ok", "arquivos": arquivos}


@router.get("/download/{nome_arquivo}")
def baixar_arquivo_controller(nome_arquivo: str, request: Request, senha: str = Query(default="")):
    ip_cliente = request.client.host if request.client else None
    caminho = obter_caminho_para_download(nome_arquivo, senha, ip_cliente)

    if not caminho:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado ou senha inválida")

    return FileResponse(
        path=caminho,
        filename=caminho.name,
        media_type="application/octet-stream"
    )
