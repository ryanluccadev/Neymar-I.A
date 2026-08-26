"""
Utilitários de baixo nível de interação com o sistema operacional:
encerrar processos, abrir URLs/atalhos/aplicativos e fechar janelas
do Explorador de Arquivos.

Este módulo não conhece "comandos de voz" nem lógica de negócio —
apenas expõe operações reutilizáveis do Windows.
"""

import os
import subprocess
import time
import ctypes
from ctypes import wintypes

import pyautogui

from . import config


def bate(comando, *frases):
    """Retorna True se qualquer uma das frases estiver contida no comando."""

    return any(
        frase in comando
        for frase in frases
    )


def matar_processo(nome_exe):
    """Encerra um processo do Windows pelo nome do executável."""

    os.system(
        f"taskkill /f /im {nome_exe} >nul 2>&1"
    )


def abrir_url(url):
    """Abre uma URL no navegador padrão do Windows."""

    subprocess.Popen(
        [
            "cmd",
            "/c",
            "start",
            "",
            url
        ],
        shell=False
    )


def abrir_aplicativo(nome):
    """Abre um aplicativo pelo menu iniciar."""

    pyautogui.press("win")

    time.sleep(
        config.ATRASO_MENU_INICIAR
    )

    pyautogui.write(
        nome,
        interval=config.INTERVALO_DIGITACAO
    )

    time.sleep(
        config.ATRASO_ANTES_DO_ENTER
    )

    pyautogui.press("enter")

    time.sleep(
        config.ATRASO_ABERTURA_APP
    )


def abrir_atalho_desktop(nome_atalho):
    """Abre um atalho .lnk da área de trabalho."""

    caminho = os.path.join(
        os.environ["USERPROFILE"],
        "Desktop",
        nome_atalho + ".lnk"
    )

    if not os.path.exists(caminho):

        print(
            f"\n[!] Atalho não encontrado: {caminho}"
        )

        return False

    os.startfile(
        caminho
    )

    return True


def fechar_janelas_explorador():
    """Fecha todas as janelas abertas do Explorador de Arquivos."""

    user32 = ctypes.windll.user32

    janelas_fechadas = []

    EnumWindowsProc = ctypes.WINFUNCTYPE(
        ctypes.c_bool,
        wintypes.HWND,
        wintypes.LPARAM
    )

    def callback(hwnd, lparam):

        if not user32.IsWindowVisible(hwnd):

            return True

        buffer = ctypes.create_unicode_buffer(256)

        user32.GetClassNameW(
            hwnd,
            buffer,
            256
        )

        if buffer.value == "CabinetWClass":

            user32.PostMessageW(
                hwnd,
                config.WM_CLOSE,
                0,
                0
            )

            janelas_fechadas.append(hwnd)

        return True

    user32.EnumWindows(
        EnumWindowsProc(callback),
        0
    )

    return janelas_fechadas
