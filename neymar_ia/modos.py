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
import sys
import sqlite3
import threading
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
# CONSOLE DISPONÍVEL?
# ============================================================

def _console_disponivel():
    """
    Verifica se existe um console interativo (stdin) de verdade.

    Quando o Neymar roda dentro da interface gráfica (ou como .exe
    gerado com PyInstaller em modo janela), não existe um console
    de verdade por trás: sys.stdin pode ser None ou não ser um
    terminal. Nesse caso, chamar input() explode com
    'RuntimeError: lost sys.stdin'. Esta função existe para evitar
    isso: qualquer trecho que dependa de input() deve checar aqui
    antes.
    """

    try:

        return (
            sys.stdin is not None
            and sys.stdin.isatty()
        )

    except Exception:

        return False


# ============================================================
# CONTROLE DO NÚCLEO (PONTE COM A INTERFACE GRÁFICA)
# ============================================================

class ControleNucleo:
    """
    Ponte entre a interface gráfica e a máquina de estados.

    Não substitui modo_voz()/modo_texto() (que continuam existindo
    e funcionando normalmente pelo terminal). Ela só existe para o
    caso de rodar dentro da interface, onde não há input() de
    console disponível: em vez de travar em input(), o modo texto
    dorme aqui até a própria interface avisar "voltar pra voz" ou
    "desligar" (o que ela já faz sempre que você digita algo na
    caixa de texto).
    """

    def __init__(self):
        self.modo = "voz"
        self.rodando = True
        self._evento = threading.Event()

    def pedir_modo_voz(self):
        self.modo = "voz"
        self._evento.set()

    def pedir_modo_texto(self):
        self.modo = "texto"
        self._evento.set()

    def pedir_desligar(self):
        self.rodando = False
        self._evento.set()

    def _aguardar_mudanca(self):
        self._evento.wait()
        self._evento.clear()


def _modo_texto_gui(controle, status_callback=None):
    """
    Equivalente ao modo_texto(), só que para quando o Neymar roda
    na interface gráfica. As mensagens continuam sendo digitadas
    normalmente na caixa de texto da interface (que já chama
    processar_comando() por conta própria) — aqui a gente só fica
    esperando, sem consumir CPU e sem tocar em input(), até a
    interface avisar que é pra voltar ao modo voz ou desligar.
    """

    if status_callback:
        status_callback("modo_texto")

    falar(
        "Modo texto ativado. Pode digitar na caixa de texto da "
        "interface. Para voltar a falar, digite 'mudar para voz'.",
        False
    )

    controle.modo = "texto"

    while True:

        controle._aguardar_mudanca()

        if not controle.rodando:
            return "desligar"

        if controle.modo == "voz":
            return "voz"

        # Mudança sinalizada mas ainda em modo texto: falso alarme,
        # continua esperando.


# ============================================================
# PROCESSAR RECURSOS
# ============================================================

def _processar_recursos(comando, usar_voz, message_callback=None):
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

        if message_callback:
            message_callback("assistente", resposta_memoria)

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

        if message_callback:
            message_callback("assistente", resposta)

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

            if message_callback:
                message_callback("assistente", resposta)

            return True

        if not _console_disponivel():

            # Sem console interativo (ex.: rodando pela interface
            # gráfica). Mostra um resumo direto, sem menu que
            # dependeria de input().

            print(
                "\nHistórico de conversas:"
            )

            for numero, sessao in enumerate(
                sessoes,
                start=1
            ):

                resumo = _obter_resumo_conversa(
                    sessao["id"]
                )

                print(
                    f"{numero}. {resumo}"
                )

            resposta = (
                "Aqui está um resumo do seu histórico. Para ver uma "
                "conversa específica, use a caixa de texto da "
                "interface."
            )

            falar(
                resposta,
                usar_voz
            )

            if message_callback:
                message_callback("assistente", resposta)

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

        if message_callback:
            message_callback("assistente", resposta)

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

def modo_voz(status_callback=None, message_callback=None):
    """Loop principal do modo de voz."""

    while True:

        if status_callback:
            status_callback("ouvindo")

        mensagem = ouvir()

        if not mensagem:

            continue

        if status_callback:
            status_callback("processando")

        comando = mensagem.lower().strip()

        if message_callback:
            message_callback("usuario", mensagem.strip())

        if _processar_recursos(
            mensagem.strip(),
            True,
            message_callback
        ):

            continue

        if bate(
            comando,
            "desligar neymar",
            "desliga neymar"
        ):

            falar(
                "Valeu jogador, até mais.",
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

        if message_callback:
            message_callback("assistente", resposta)


# ============================================================
# MODO TEXTO
# ============================================================

def modo_texto():
    """
    Loop principal do modo texto pelo TERMINAL (usa input() de
    verdade). Só é chamado quando existe um console interativo de
    verdade (ex.: `python Neymar_IA.py --console`). Quando roda pela
    interface gráfica, quem assume é a _modo_texto_gui().
    """

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
                "Valeu jogador, até mais",
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
# COMANDO EXTERNO (INTERFACE)
# ============================================================

def processar_comando(comando, usar_voz=False, message_callback=None):
    """Processa um comando individual vindo da interface gráfica."""

    mensagem = comando.strip()

    if not mensagem:
        return None

    normalizado = mensagem.lower()

    if _processar_recursos(mensagem, usar_voz, message_callback):
        return "Comando processado."

    if bate(
        normalizado,
        "desligar neymar",
        "desliga neymar"
    ):
        resposta = "Valeu jogador, até mais"
        falar(resposta, usar_voz)
        return resposta

    if executar_comando_sistema(normalizado, usar_voz):
        return "Comando executado."

    resposta = perguntar_neymar(mensagem)

    salvar_mensagem("usuario", mensagem)
    salvar_mensagem("assistente", resposta)
    falar(resposta, usar_voz)

    return resposta


# ============================================================
# INICIAR ASSISTENTE
# ============================================================

def iniciar_assistente(status_callback=None, controle=None, message_callback=None):
    """
    Máquina de estados principal. A interface acompanha o mesmo
    núcleo de voz.

    `controle`: instância de ControleNucleo, passada pela interface
    gráfica. Quando None (uso normal pelo terminal), o modo texto
    usa input() como sempre. Quando fornecida, o modo texto usa a
    ponte _modo_texto_gui() em vez de input().
    """

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

            if status_callback:
                status_callback("aguardando")

            acordou = aguardar_neymar()

            if not acordou:

                break

            if status_callback:
                status_callback("ativo")

            falar(
                "Fala aí arrogante, donde quieres?",
                True
            )

            modo = "voz"

        elif modo == "voz":

            resultado = modo_voz(status_callback, message_callback)

            if resultado == "texto":

                modo = "texto"

            elif resultado == "desligar":

                if status_callback:
                    status_callback("desligado")

                break

        elif modo == "texto":

            if controle is not None:

                resultado = _modo_texto_gui(
                    controle,
                    status_callback
                )

            else:

                resultado = modo_texto()

            if resultado == "voz":

                if controle is not None:
                    controle.modo = "voz"

                modo = "voz"

            elif resultado == "desligar":

                if status_callback:
                    status_callback("desligado")

                break