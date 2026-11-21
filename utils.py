import qrcode


def mostrar_qrcode(url: str, titulo: str | None = None):
    if titulo:
        print(f"\n\033[1;34m=== {titulo} ===\033[0m")
    qr = qrcode.QRCode(box_size=1, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    qr.print_ascii(invert=True)
    print(f"\033[1;36m>> Link de acesso: {url}\033[0m\n")


def imprimir_banner():
    banner = '''
\033[34m▄▄▄   ▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄ ▄▄▄    ▄▄▄ ▄▄▄▄▄▄
███   ███ █████▀▀▀ ███▀▀▀▀▀ ████▄  ███ ███▀▀██▄
█████████  ▀████▄  ███▄▄    ███▀██▄███ ███  ███
███▀▀▀███    ▀████ ███      ███  ▀████ ███  ███
███   ███ ███████▀ ▀███████ ███    ███ ██████▀\033[0m
  \033[2mFast & Secure Local/Tunnel File & Text Transfer\033[0m
    '''
    print(banner)
