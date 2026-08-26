"""Integração simples do Neymar IA com a inicialização do Windows."""

import os
import sys
from pathlib import Path

NOME_ATALHO = "Neymar IA.lnk"


def _pasta_startup():
    appdata = os.getenv("APPDATA")
    if not appdata:
        return None
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def _alvo_inicializacao():
    if getattr(sys, "frozen", False):
        return Path(sys.executable), ""

    pythonw = Path(sys.executable).with_name("pythonw.exe")
    interpretador = pythonw if pythonw.exists() else Path(sys.executable)
    script = Path(sys.argv[0]).resolve()
    return interpretador, f'"{script}"'


def esta_ativado():
    pasta = _pasta_startup()
    return bool(pasta and (pasta / NOME_ATALHO).exists())


def ativar():
    """Cria o atalho do Neymar IA na inicialização do Windows."""
    if os.name != "nt":
        return False

    pasta = _pasta_startup()
    if not pasta:
        return False

    pasta.mkdir(parents=True, exist_ok=True)
    atalho = pasta / NOME_ATALHO
    executavel, argumentos = _alvo_inicializacao()

    try:
        import win32com.client
    except ImportError:
        return False

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(str(atalho))
    shortcut.Targetpath = str(executavel)
    shortcut.Arguments = argumentos
    shortcut.WorkingDirectory = str(Path(sys.argv[0]).resolve().parent)
    shortcut.IconLocation = str(executavel)
    shortcut.save()
    return True


def desativar():
    """Remove o atalho da inicialização."""
    pasta = _pasta_startup()
    if not pasta:
        return False

    atalho = pasta / NOME_ATALHO
    try:
        atalho.unlink(missing_ok=True)
        return True
    except OSError:
        return False
