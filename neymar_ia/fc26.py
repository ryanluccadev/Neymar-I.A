"""
Controle do EA SPORTS FC 26: abertura direta do executável e
encerramento do processo.
"""

import os
import subprocess
import time

from . import config
from .sistema import matar_processo


def abrir_fc26():
    """Abre diretamente o executável do FC 26."""

    if not os.path.exists(config.CAMINHO_FC26):

        print(
            "\n[!] Executável do FC 26 não encontrado:"
        )

        print(
            config.CAMINHO_FC26
        )

        return False

    try:

        subprocess.Popen(
            config.CAMINHO_FC26,
            cwd=os.path.dirname(config.CAMINHO_FC26)
        )

        return True

    except Exception as erro:

        print(
            "\n[!] Erro ao abrir o FC 26:"
        )

        print(erro)

        return False


def fechar_fc26():
    """Fecha o processo do FC 26."""

    matar_processo(
        "FC26.exe"
    )

    # Algumas versões podem utilizar outro processo.
    # O EA app/Steam não é encerrado.
    time.sleep(1)
