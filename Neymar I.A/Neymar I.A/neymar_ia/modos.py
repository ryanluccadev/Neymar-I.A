"""
Máquina de estados do Neymar IA.

Controla:
- Modo de espera
- Modo de voz
- Modo de texto
- Histórico de conversas
- Memória
- Comandos do sistema
"""

import os
import sqlite3
from datetime import datetime

from .sistema import bate
from .audio import falar, ouvir, aguardar_neymar
from .comandos import executar_comando_sistema
from .ia import perguntar_neymar

from .historico import (
    salvar_mensagem,
    listar_conversas,
    formatar_sessao,
    limpar_historico,
    nova_sessao,
    inicializar as inicializar_historico,
    DB_PATH
)

from .memoria import (
    processar_comando as processar_memoria,
    inicializar as inicializar_memoria
)


# ============================================================
# PROCESSAR RECURSOS
# ============================================================

def _processar_recursos(comando, usar_voz):
    """
    Processa memória e comandos relacionados ao histórico.
    """

    resposta_memoria = processar_memoria(comando)

    if resposta_memoria is not None:

        salvar_mensagem(
            "usuario",
            comando
        )

        salvar_mensagem(
            "assistente",
            resposta_memoria
        )

        falar(
            resposta_memoria,
            usar_voz
        )

        return True

    normalizado = comando.lower().strip()

    # ========================================================
    # NOVA CONVERSA
    # ========================================================

    if normalizado in (
        "nova",
        "/nova",
        "nova conversa",
        "/nova conversa",
    ):

        nova_sessao()

        resposta = "Nova conversa iniciada."

        print(
            f"\nNEYMAR IA: {resposta}"
        )

        falar(
            resposta,
            usar_voz
        )

        return True

    # ========================================================
    # HISTÓRICO
    # ========================================================

    if normalizado in (
        "histórico",
        "historico",
        "exibir histórico",
        "exibir historico",
        "mostrar histórico",
        "mostrar historico",
        "ver histórico",
        "ver historico",
        "minhas conversas",
        "mostrar conversas",
        "ver conversas",
        "histórico de conversas",
        "historico de conversas",
        "histórico das conversas",
        "historico das conversas",
    ):

        sessoes = listar_conversas()

        if not sessoes:

            resposta = (
                "Ainda não existe nenhuma conversa salva."
            )

            falar(
                resposta,
                usar_voz
            )

            return True

        while True:

            os.system("cls")

            print()
            print(
                "╔" + "═" * 68 + "╗"
            )

            print(
                "║"
                + " NEYMAR IA — HISTÓRICO ".center(68)
                + "║"
            )

            print(
                "╠" + "═" * 68 + "╣"
            )

            print(
                "║"
                + " Escolha uma conversa para visualizar:".ljust(68)
                + "║"
            )

            print(
                "╠" + "═" * 68 + "╣"
            )

            for numero, sessao in enumerate(
                sessoes,
                start=1
            ):

                try:

                    inicio = datetime.fromisoformat(
                        sessao["inicio"]
                    )

                    ultima = datetime.fromisoformat(
                        sessao["ultima"]
                    )

                    hoje = datetime.now().date()

                    if inicio.date() == hoje:

                        data_inicio = (
                            "Hoje - "
                            + inicio.strftime("%H:%M")
                        )

                    else:

                        data_inicio = inicio.strftime(
                            "%d/%m/%Y - %H:%M"
                        )

                    ultima_formatada = ultima.strftime(
                        "%H:%M"
                    )

                except (
                    ValueError,
                    TypeError,
                    KeyError
                ):

                    data_inicio = sessao.get(
                        "inicio",
                        "Data desconhecida"
                    )

                    ultima_formatada = sessao.get(
                        "ultima",
                        ""
                    )

                resumo = _obter_resumo_conversa(
                    sessao["id"]
                )

                quantidade = sessao.get(
                    "quantidade",
                    0
                )

                print(
                    "║"
                    + f" {numero}. {data_inicio}".ljust(68)
                    + "║"
                )

                print(
                    "║"
                    + f"    {resumo}".ljust(68)[:68]
                    + "║"
                )

                print(
                    "║"
                    + (
                        f"    {quantidade} mensagens"
                        f" - última às {ultima_formatada}"
                    ).ljust(68)
                    + "║"
                )

                print(
                    "║"
                    + "".ljust(68)
                    + "║"
                )

            print(
                "╠" + "═" * 68 + "╣"
            )

            print(
                "║"
                + " 0. Voltar".ljust(68)
                + "║"
            )

            print(
                "╚" + "═" * 68 + "╝"
            )

            escolha = input(
                "\nDigite o número da conversa: "
            ).strip()

            if escolha == "0":

                return True

            try:

                numero = int(
                    escolha
                )

            except ValueError:

                print(
                    "\nNúmero inválido."
                )

                input(
                    "\nPressione ENTER para continuar..."
                )

                continue

            if numero < 1 or numero > len(sessoes):

                print(
                    "\nEssa conversa não existe."
                )

                input(
                    "\nPressione ENTER para continuar..."
                )

                continue

            sessao_escolhida = sessoes[
                numero - 1
            ]

            os.system("cls")

            print()
            print(
                "╔" + "═" * 68 + "╗"
            )

            print(
                "║"
                + f" CONVERSA {numero} ".center(68)
                + "║"
            )

            print(
                "╚" + "═" * 68 + "╝"
            )

            print()

            historico = formatar_sessao(
                sessao_escolhida["sessao"]
            )

            print(
                historico
            )

            print()
            print(
                "=" * 70
            )

            input(
                "\nPressione ENTER para voltar ao histórico..."
            )

            continue

    # ========================================================
    # LIMPAR HISTÓRICO
    # ========================================================

    if normalizado in (
        "limpar histórico",
        "limpar historico",
        "apagar histórico",
        "apagar historico",
        "limpar conversas",
        "apagar conversas",
    ):

        limpar_historico()

        resposta = (
            "Todo o histórico de conversas foi apagado."
        )

        falar(
            resposta,
            usar_voz
        )

        return True

    return False


# ============================================================
# RESUMO DA CONVERSA
# ============================================================

def _obter_resumo_conversa(sessao_id):
    """
    Obtém a primeira mensagem do usuário de uma conversa.
    """

    try:

        conexao = sqlite3.connect(
            DB_PATH
        )

        conexao.row_factory = sqlite3.Row

        mensagem = conexao.execute(
            """
            SELECT mensagem
            FROM mensagens
            WHERE sessao_id = ?
            AND papel = 'usuario'
            ORDER BY id ASC
            LIMIT 1
            """,
            (
                sessao_id,
            )
        ).fetchone()

        conexao.close()

        if not mensagem:

            return "Conversa sem mensagens"

        texto = mensagem["mensagem"].strip()

        texto = " ".join(
            texto.split()
        )

        if len(texto) > 58:

            texto = (
                texto[:55]
                + "..."
            )

        return texto

    except Exception:

        return "Conversa"


# ============================================================
# INICIALIZAÇÃO
# ============================================================

def _inicializar_dados():
    """Inicializa histórico e memória."""

    inicializar_historico()
    inicializar_memoria()


# ============================================================
# MODO VOZ
# ============================================================

def modo_voz():
    """Loop principal do modo de voz."""

    while True:

        mensagem = ouvir()

        if not mensagem:

            continue

        comando = mensagem.lower().strip()

        if _processar_recursos(
            mensagem.strip(),
            True
        ):

            continue

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

        salvar_mensagem(
            "usuario",
            mensagem
        )

        salvar_mensagem(
            "assistente",
            resposta
        )

        falar(
            resposta,
            True
        )


# ============================================================
# MODO TEXTO
# ============================================================

def modo_texto():
    """Loop principal do modo texto."""

    while True:

        mensagem = input(
            "\nVOCÊ: "
        ).strip()

        if not mensagem:

            continue

        comando = mensagem.lower().strip()

        if _processar_recursos(
            mensagem,
            False
        ):

            continue

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

        salvar_mensagem(
            "usuario",
            mensagem
        )

        salvar_mensagem(
            "assistente",
            resposta
        )

        falar(
            resposta,
            False
        )


# ============================================================
# INICIAR ASSISTENTE
# ============================================================

def iniciar_assistente():
    """Máquina de estados principal."""

    _inicializar_dados()

    nova_sessao()

    modo = "espera"

    while True:

        if modo == "espera":

            os.system("cls")

            print(
                "\n" + "=" * 55
            )

            print(
                "                   NEYMAR IA"
            )

            print(
                "=" * 55
            )

            print(
                "\n[Aguardando 'Ligar Neymar'...]"
            )

            acordou = aguardar_neymar()

            if not acordou:

                break

            falar(
                "Fala aí arrogante, donde quieres?",
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