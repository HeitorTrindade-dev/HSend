import argparse
import socket
from pyngrok import ngrok


def obter_ip_local() -> str:
    """Detecta o IP do dispositivo na rede local (Wi-Fi / Ethernet)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def configurar_e_iniciar_ngrok(porta: int):
    """Inicia o túnel ngrok e solicita o token caso não configurado."""
    try:
        tunnel = ngrok.connect(porta)
        return tunnel.public_url

    except Exception:
        print("\n\033[31mToken do ngrok não encontrado nesta máquina.\033[0m")
        print("Entre nesse link para conseguir sua credencial: https://dashboard.ngrok.com/get-started/your-authtoken")
        try:
            token_manual = input("Cole o seu token do ngrok aqui (ou pressione Enter para pular): ").strip()
            if not token_manual:
                return None
            ngrok.set_auth_token(token_manual)
            tunnel = ngrok.connect(porta)
            print("\033[32m\nToken salvo com sucesso!\033[0m")
            return tunnel.public_url
        except Exception as e:
            print(f"\033[31mNão foi possível iniciar o túnel ngrok: {e}\033[0m")
            return None


def encerrar_ngrok():
    """Fecha os túneis ngrok ativos."""
    try:
        ngrok.kill()
    except Exception:
        pass


def configurar_argumentos():
    parser = argparse.ArgumentParser(
        description="HSend - Compartilhamento rápido e seguro de arquivos e mensagens entre dispositivos."
    )
    parser.add_argument(
        '-p', '--port', '--porta',
        type=int,
        default=8000,
        help="Porta local do servidor (padrão: 8000)."
    )
    parser.add_argument(
        '-pw', '-s', '--password', '--senha',
        default=None,
        help="Configurar senha de autenticação para envio e download."
    )
    parser.add_argument(
        '-o', '--output', '--output-dir', '--destino',
        default=None,
        help="Diretório onde os arquivos recebidos serão salvos (padrão: ./recebidos)."
    )
    parser.add_argument(
        '-y', '--yes', '--auto-accept',
        action="store_true",
        help="Aceitar arquivos automaticamente sem confirmação interativa no terminal."
    )
    parser.add_argument(
        '--no-tunnel', '--local',
        action="store_true",
        help="Rodar apenas na rede local (Wi-Fi), sem abrir túnel público ngrok."
    )
    parser.add_argument(
        '--zip',
        action="store_true",
        help="Salvar arquivos recebidos compactados em um arquivo ZIP."
    )

    return parser.parse_args()
