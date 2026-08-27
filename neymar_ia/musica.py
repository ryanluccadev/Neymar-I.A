"""
Controle de reprodução de mídia (teclas de multimídia do sistema)
e do aplicativo Deezer.
"""

import pyautogui

from .sistema import bate, matar_processo, abrir_aplicativo
from .audio import falar


def controlar_musica(comando, usar_voz=True):

    if bate(
        comando,
        "pular música",
        "pular musica",
        "próxima música",
        "proxima musica",
        "próxima",
        "proxima"
    ):

        falar(
            "Pulando a música.",
            usar_voz
        )

        pyautogui.press(
            "nexttrack"
        )

        return True

    if bate(
        comando,
        "voltar música",
        "voltar musica",
        "música anterior",
        "musica anterior",
        "voltar"
    ):

        falar(
            "Voltando para a música anterior.",
            usar_voz
        )

        pyautogui.press(
            "prevtrack"
        )

        return True

    if bate(
        comando,
        "pausar música",
        "pausar musica",
        "pausar"
    ):

        falar(
            "Pausando a música.",
            usar_voz
        )

        pyautogui.press(
            "playpause"
        )

        return True

    if bate(
        comando,
        "despausar música",
        "despausar musica",
        "despausar",
        "continuar música",
        "continuar musica",
        "continuar"
    ):

        falar(
            "Continuando a música.",
            usar_voz
        )

        pyautogui.press(
            "playpause"
        )

        return True

    return False


def controlar_deezer(comando, usar_voz=True):

    if bate(
        comando,
        "abrir deezer",
        "abrir o deezer"
    ):

        falar(
            "Abrindo o Deezer.",
            usar_voz
        )

        abrir_aplicativo(
            "Deezer"
        )

        return True

    if bate(
        comando,
        "fechar deezer",
        "fechar o deezer"
    ):

        falar(
            "Fechando o Deezer.",
            usar_voz
        )

        matar_processo(
            "deezer.exe"
        )

        return True

    return False
