"""Ponto de entrada do Neymar IA."""

import sys

from neymar_ia import inicializacao


if __name__ == "__main__":
    # Ativa automaticamente a inicialização com o Windows.
    # A função verifica se o atalho já existe, portanto não cria duplicados.
    if sys.platform == "win32":
        inicializacao.ativar()

    if "--console" in sys.argv:
        from neymar_ia import iniciar_assistente
        iniciar_assistente()
    else:
        from neymar_ia.interface import iniciar_interface
        iniciar_interface(iniciar_minimizado="--minimized" in sys.argv)