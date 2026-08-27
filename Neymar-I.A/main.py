"""Ponto de entrada do Neymar IA."""

import sys

if __name__ == "__main__":
    if "--console" in sys.argv:
        from neymar_ia import iniciar_assistente
        iniciar_assistente()
    else:
        from neymar_ia.interface import iniciar_interface
        iniciar_interface()
