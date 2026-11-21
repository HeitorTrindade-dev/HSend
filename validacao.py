import os
import hmac
import time
from collections import defaultdict

# Rate limiting para proteção contra força bruta
MAX_TENTATIVAS = 5
JANELA_TEMPO_SEGUNDOS = 60
BLOQUEIO_TEMPO_SEGUNDOS = 60

_falhas_por_ip = defaultdict(list)
_bloqueios_por_ip = {}


def passar_senha(senha: str | None):
    if senha is not None and str(senha).strip() != "":
        os.environ["SENHA_ENVIO"] = str(senha).strip()
    elif "SENHA_ENVIO" in os.environ:
        del os.environ["SENHA_ENVIO"]


def senha_configurada() -> bool:
    return bool(os.environ.get("SENHA_ENVIO"))


def esta_bloqueado(ip_cliente: str) -> bool:
    agora = time.time()
    if ip_cliente in _bloqueios_por_ip:
        if agora < _bloqueios_por_ip[ip_cliente]:
            return True
        del _bloqueios_por_ip[ip_cliente]
    return False


def registrar_falha(ip_cliente: str):
    agora = time.time()
    _falhas_por_ip[ip_cliente] = [
        t for t in _falhas_por_ip[ip_cliente] if agora - t < JANELA_TEMPO_SEGUNDOS
    ]
    _falhas_por_ip[ip_cliente].append(agora)

    if len(_falhas_por_ip[ip_cliente]) >= MAX_TENTATIVAS:
        _bloqueios_por_ip[ip_cliente] = agora + BLOQUEIO_TEMPO_SEGUNDOS
        _falhas_por_ip[ip_cliente].clear()


def registrar_sucesso(ip_cliente: str):
    _falhas_por_ip.pop(ip_cliente, None)
    _bloqueios_por_ip.pop(ip_cliente, None)


def validar_senha(tentativa: str | None, ip_cliente: str | None = None) -> bool:
    if ip_cliente and esta_bloqueado(ip_cliente):
        return False

    senha_correta = os.environ.get("SENHA_ENVIO")

    if not senha_correta:
        if ip_cliente:
            registrar_sucesso(ip_cliente)
        return True

    valida = hmac.compare_digest(str(tentativa or ""), senha_correta)
    if ip_cliente:
        if valida:
            registrar_sucesso(ip_cliente)
        else:
            registrar_falha(ip_cliente)
    return valida
