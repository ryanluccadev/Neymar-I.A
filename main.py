"""
Ponto de entrada do Neymar IA.

Execução: python main.py
"""

from neymar_ia import iniciar_assistente


if __name__ == "__main__":

    try:

        iniciar_assistente()

    except KeyboardInterrupt:

        print(
            "\n\nSistemas desligados."
        )

    except Exception as erro:

        print(
            "\nERRO INESPERADO:",
            erro
        )

        input(
            "\nPressione ENTER para sair..."
        )