import argparse
from pyngrok import ngrok, conf

def configurar_e_iniciar_ngrok(porta):
    try:
        public_url = ngrok.connect(porta).public_url
        return public_url

    except Exception:
        print("\n\033[31mToken do ngrok não encontrado nesta máquina.\033[0m")
        print("Entre nesse link para conseguir sua credencial: https://dashboard.ngrok.com/get-started/your-authtoken")
        token_manual = input("Cole o seu token do ngrok aqui (apenas na 1ª vez): ").strip()

        ngrok.set_auth_token(token_manual)

        public_url = ngrok.connect(porta).public_url
        print("\033[32m\nToken salvo com sucesso!\033[0m")
        return public_url

def configurar_argumentos():

    parser = argparse.ArgumentParser(description="Uma ferramenta simples de envio de arquivos entre dispositivos.")
    parser.add_argument('-p','--port','--porta', type=int, default=8000, help="Configurar porta de ascesso customizada.")
    parser.add_argument('-pw','-s','--password','--senha', default=None, help="Configurar senha de envio.")

    return parser.parse_args()
