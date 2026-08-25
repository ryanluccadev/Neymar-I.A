"""
Máquina de estados do assistente: espera pela ativação, e alterna
entre o modo voz e o modo texto até receber o comando de desligar.
"""

import os

from .sistema import bate
from .audio import falar, ouvir, aguardar_neymar
from .comandos import executar_comando_sistema
from .ia import perguntar_neymar


def modo_voz():
    """Loop principal do modo de voz."""

    while True:

        mensagem = ouvir()

        if not mensagem:

            continue

        comando = mensagem.lower().strip()

        if bate(
            comando,
            "desligar neymar",
            "desliga neymar"
        ):

            falar(
                "Desligando os sistemas. Até logo, senhor.",
                True
            )

            return "desligar"

        if bate(
            comando,
            "mudar para texto",
            "modo texto",
            "trocar para texto"
        ):

            falar(
                "Mudando para o modo texto.",
                True
            )

            return "texto"

        if executar_comando_sistema(
            comando,
            True
        ):

            continue

        resposta = perguntar_neymar(
            mensagem
        )

        falar(
            resposta,
            True
        )


def modo_texto():
    """Loop principal do modo texto."""

    while True:

        mensagem = input(
            "\nVOCÊ: "
        ).strip()

        if not mensagem:

            continue

        comando = mensagem.lower()

        if bate(
            comando,
            "desligar neymar",
            "desliga neymar"
        ):

            falar(
                "Desligando os sistemas. Até logo, senhor.",
                False
            )

            return "desligar"

        if bate(
            comando,
            "mudar para voz",
            "modo voz",
            "trocar para voz"
        ):

            falar(
                "Mudando para o modo voz.",
                False
            )

            return "voz"

        if executar_comando_sistema(
            comando,
            False
        ):

            continue

        resposta = perguntar_neymar(
            mensagem
        )

        falar(
            resposta,
            False
        )


def iniciar_assistente():
    """Máquina de estados principal."""

    modo = "espera"

    while True:

        if modo == "espera":

            os.system("cls")

            print("\n" + "=" * 55)

            print(
                "                   NEYMAR IA"
            )

            print("=" * 55)

            print(
                "\n[Aguardando 'Ligar Neymar'...]"
            )

            acordou = aguardar_neymar()

            if not acordou:

                break

            falar(
                "Fala aí mano, tudo certo?",
                True
            )

            modo = "voz"

        elif modo == "voz":

            resultado = modo_voz()

            if resultado == "texto":

                modo = "texto"

            elif resultado == "desligar":

                break

        elif modo == "texto":

            resultado = modo_texto()

            if resultado == "voz":

                modo = "voz"

            elif resultado == "desligar":

                break
