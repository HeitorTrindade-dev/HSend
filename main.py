#!/usr/bin/env python3
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Garante que o diretório base do projeto esteja no sys.path, mesmo quando invocado via symlink
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from utils import mostrar_qrcode, imprimir_banner
from configs import (
    configurar_argumentos,
    configurar_e_iniciar_ngrok,
    encerrar_ngrok,
    obter_ip_local,
)
from controller import router
from validacao import passar_senha
from services import configurar_servico


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização da aplicação
    yield
    # Limpeza ao desligar
    encerrar_ngrok()


app = FastAPI(title="HSend", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(router)


def main():
    args = configurar_argumentos()
    passar_senha(args.password)
    porta = args.port

    configurar_servico(
        diretorio_saida=args.output,
        auto_aceitar=args.yes,
        salvar_em_zip=args.zip,
    )

    imprimir_banner()

    ip_local = obter_ip_local()
    url_local = f"http://{ip_local}:{porta}"

    url_publica = None
    if not args.no_tunnel:
        print("[*] Iniciando túnel público via ngrok...")
        url_publica = configurar_e_iniciar_ngrok(porta)

    if url_publica:
        mostrar_qrcode(url_publica, titulo="ACESSO PÚBLICO (NGROK)")
        print(f"\033[1;32m[*] URL Pública (Qualquer lugar):\033[0m {url_publica}")
        print(f"\033[1;34m[*] URL Local (Mesmo Wi-Fi):\033[0m    {url_local}\n")
    else:
        mostrar_qrcode(url_local, titulo="ACESSO LOCAL (MESMO WI-FI)")
        print(f"\033[1;32m[*] URL Local (Mesmo Wi-Fi):\033[0m {url_local}\n")

    if args.password:
        print("\033[33m[*] Autenticação com senha ATIVADA.\033[0m")
    else:
        print("\033[33m[*] Nenhuma senha configurada. Acesso aberto.\033[0m")

    if args.yes:
        print("\033[33m[*] Modo Auto-Accept ativado: arquivos serão aceitos sem confirmação.\033[0m")

    print("\033[2mPressione Ctrl+C para encerrar o servidor.\033[0m\n")

    try:
        # Ouvir em 0.0.0.0 permite conexões locais de outros dispositivos na mesma rede
        uvicorn.run(app, host="0.0.0.0", port=porta, reload=False, log_level="warning")
    except KeyboardInterrupt:
        print("\n\033[33m[*] Encerrando o HSend...\033[0m")
    finally:
        encerrar_ngrok()


if __name__ == "__main__":
    main()
