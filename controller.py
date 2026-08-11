from pathlib import Path

from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from services import enviar_texto_service, enviar_arquivo_service

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent


@router.get("/")
def ler_raiz():
    return FileResponse(BASE_DIR / "static" / "index.html")


class Dados(BaseModel):
    mensagem: str
    senha: str


@router.post("/enviar/texto")
def enviar_texto_controller(dados: Dados):
    if not enviar_texto_service(dados.mensagem, dados.senha):
        raise HTTPException(status_code=401, detail="Senha incorreta")
    return {"status": "ok"}


@router.post("/enviar/arquivo")
async def enviar_arquivo_controller(senha: str = Form(...), arquivo: UploadFile = File(...)):
    resultado = await enviar_arquivo_service(arquivo, senha)

    if resultado == "senha_invalida":
        raise HTTPException(status_code=401, detail="Senha incorreta")

    if resultado != "ok":
        return {"status": "recusado"}

    return {"status": "ok", "nome_arquivo": arquivo.filename}
