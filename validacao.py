import os
import hmac


def passar_senha(senha):
    if senha is not None:
        os.environ["SENHA_ENVIO"] = senha


def validar_senha(tentativa):
    senha_correta = os.environ.get("SENHA_ENVIO")

    if senha_correta is None:
        return True

    return hmac.compare_digest(tentativa or "", senha_correta)
