"""
Pesquisa de música no YouTube e abertura do primeiro resultado.
"""

import time
import urllib.parse

import pyautogui

from . import config
from .sistema import abrir_url
from .audio import falar


def tocar_youtube(comando, usar_voz=True):
    """Pesquisa uma música no YouTube e abre o primeiro resultado."""

    if not comando.startswith("tocar "):

        return False

    musica = comando.replace(
        "tocar ",
        "",
        1
    ).strip()

    if not musica:

        return False

    falar(
        f"Procurando {musica} no YouTube.",
        usar_voz
    )

    pesquisa = urllib.parse.quote_plus(
        musica
    )

    url = (
        "https://www.youtube.com/results?search_query="
        + pesquisa
    )

    abrir_url(url)

    time.sleep(
        config.ATRASO_CARREGAMENTO_YOUTUBE
    )

    pyautogui.click(
        config.CLIQUE_YOUTUBE_X,
        config.CLIQUE_YOUTUBE_Y
    )

    time.sleep(
        config.ATRASO_APOS_CLIQUE_YOUTUBE
    )

    return True
