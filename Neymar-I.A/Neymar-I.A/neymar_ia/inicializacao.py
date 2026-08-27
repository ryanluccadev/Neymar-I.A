"""Integração do Neymar IA com a inicialização do Windows."""

import os
import sys
from pathlib import Path

from . import config


NOME_ATALHO = "Neymar IA.lnk"


def _pasta_startup():
    """Retorna a pasta de inicialização do usuário atual."""
    appdata = os.getenv("APPDATA")

    if not appdata:
        return None

    return (
        Path(appdata)
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs"
        / "Startup"
    )


def _alvo_inicializacao():
    """Define qual programa o atalho deve executar."""

    # Quando estiver rodando como .exe criado pelo PyInstaller.
    if getattr(sys, "frozen", False):
        return Path(sys.executable), "--minimized"

    # Quando estiver rodando diretamente pelo Python.
    pythonw = Path(sys.executable).with_name("pythonw.exe")

    if pythonw.exists():
        interpretador = pythonw
    else:
        interpretador = Path(sys.executable)

    script = Path(sys.argv[0]).resolve()

    return interpretador, f'"{script}" --minimized'


def esta_ativado():
    """Verifica se o Neymar IA está configurado para iniciar com o Windows."""

    pasta = _pasta_startup()

    if not pasta:
        return False

    return (pasta / NOME_ATALHO).exists()


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

    try:
        shell = win32com.client.Dispatch("WScript.Shell")

        shortcut = shell.CreateShortCut(str(atalho))

        shortcut.Targetpath = str(executavel)
        shortcut.Arguments = argumentos

        if getattr(sys, "frozen", False):
            shortcut.WorkingDirectory = str(Path(sys.executable).resolve().parent)
        else:
            shortcut.WorkingDirectory = str(
                Path(sys.argv[0]).resolve().parent
            )

        icon = config.caminho_asset("neymar_ia.ico")

        if icon.exists():
            shortcut.IconLocation = str(icon)
        else:
            shortcut.IconLocation = str(executavel)

        shortcut.save()

        return True

    except Exception:
        return False


def desativar():
    """Remove o atalho da inicialização do Windows."""

    pasta = _pasta_startup()

    if not pasta:
        return False

    atalho = pasta / NOME_ATALHO

    try:
        atalho.unlink(missing_ok=True)
        return True
    except OSError:
        return False