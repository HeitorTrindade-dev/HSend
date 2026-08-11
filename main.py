#!/usr/bin/env python3
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from utils import mostrar_qrcode, imprimir_banner
from configs import configurar_argumentos, configurar_e_iniciar_ngrok
from controller import router
from validacao import passar_senha

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

app.include_router(router)

if __name__ == "__main__":
    args = configurar_argumentos()
    passar_senha(args.password)
    porta = args.port

    url = configurar_e_iniciar_ngrok(porta)
    imprimir_banner()
    mostrar_qrcode(url)
    print(url)
    uvicorn.run("main:app", host="127.0.0.1", port=porta, reload=False)
