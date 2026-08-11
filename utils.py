import qrcode

def mostrar_qrcode(url):
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.make()
    qr.print_ascii(invert=True)

def imprimir_banner():
    banner ='''
▄▄▄   ▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄ ▄▄▄    ▄▄▄ ▄▄▄▄▄▄
███   ███ █████▀▀▀ ███▀▀▀▀▀ ████▄  ███ ███▀▀██▄
█████████  ▀████▄  ███▄▄    ███▀██▄███ ███  ███
███▀▀▀███    ▀████ ███      ███  ▀████ ███  ███
███   ███ ███████▀ ▀███████ ███    ███ ██████▀
    '''
    print (banner)
