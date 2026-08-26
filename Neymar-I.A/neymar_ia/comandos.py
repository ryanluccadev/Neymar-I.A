"""
Tabela de comandos do sistema (frases -> ação) e a função de despacho
`executar_comando_sistema`, que tenta interpretar um comando de texto/voz
como uma ação local antes de cair no fallback de IA.
"""

import os
import subprocess

import pyautogui

from .sistema import (
    bate,
    matar_processo,
    abrir_url,
    abrir_aplicativo,
    fechar_janelas_explorador
)

from .fc26 import (
    abrir_fc26,
    fechar_fc26
)

from .musica import (
    controlar_musica,
    controlar_deezer
)

from .youtube import tocar_youtube
from .pesquisa import pesquisar_internet
from .audio import falar
from .streamings import controlar_streamings


# ============================================================
# CONTROLE DE MÍDIA
# ============================================================

def pausar_midia(usar_voz=True):
    pyautogui.press("playpause")

    falar(
        "Pausando.",
        usar_voz
    )

    return True


def continuar_midia(usar_voz=True):
    pyautogui.press("playpause")

    falar(
        "Continuando.",
        usar_voz
    )

    return True


def proximo_episodio(usar_voz=True):
    pyautogui.press("nexttrack")

    falar(
        "Indo para o próximo episódio.",
        usar_voz
    )

    return True


def episodio_anterior(usar_voz=True):
    pyautogui.press("prevtrack")

    falar(
        "Voltando para o episódio anterior.",
        usar_voz
    )

    return True


def avancar_midia(usar_voz=True):
    """
    Avança aproximadamente 30 segundos.

    A seta direita é usada porque navegadores e vários players
    de vídeo utilizam essa tecla para avanço.
    """

    for _ in range(3):
        pyautogui.press("right")

    falar(
        "Avançando.",
        usar_voz
    )

    return True


def voltar_midia(usar_voz=True):
    """
    Volta aproximadamente 20 segundos.
    """

    for _ in range(2):
        pyautogui.press("left")

    falar(
        "Voltando.",
        usar_voz
    )

    return True


def aumentar_volume_midia(usar_voz=True):

    for _ in range(5):
        pyautogui.press("volumeup")

    falar(
        "Aumentando o volume.",
        usar_voz
    )

    return True


def diminuir_volume_midia(usar_voz=True):

    for _ in range(5):
        pyautogui.press("volumedown")

    falar(
        "Diminuindo o volume.",
        usar_voz
    )

    return True


def mutar_midia(usar_voz=True):

    pyautogui.press("volumemute")

    falar(
        "Mutando o volume.",
        usar_voz
    )

    return True


# ============================================================
# TABELA DE COMANDOS DO SISTEMA
# ============================================================

COMANDOS_SISTEMA = [

    (
        [
            "abrir youtube",
            "abrir o youtube"
        ],
        "Abrindo o YouTube.",
        lambda: abrir_url(
            "https://www.youtube.com"
        )
    ),

    (
        [
            "abrir brave",
            "abrir o brave",
            "abrir navegador",
            "abrir o navegador"
        ],
        "Abrindo o Brave.",
        lambda: abrir_aplicativo(
            "Brave"
        )
    ),

    (
        [
            "abrir discord",
            "abrir o discord"
        ],
        "Abrindo o Discord.",
        lambda: abrir_aplicativo(
            "Discord"
        )
    ),

    (
        [
            "abrir vs code",
            "abrir vscode",
            "abrir visual studio code"
        ],
        "Abrindo o Visual Studio Code.",
        lambda: abrir_aplicativo(
            "Visual Studio Code"
        )
    ),

    (
        [
            "abrir steam",
            "abrir a steam"
        ],
        "Abrindo a Steam.",
        lambda: abrir_aplicativo(
            "Steam"
        )
    ),

    (
        [
            "abrir fifa",
            "abrir o fifa",
            "abrir fc 26",
            "abrir o fc 26",
            "abrir ea sports fc",
            "abrir ea sports"
        ],
        "Abrindo o EA SPORTS FC 26.",
        abrir_fc26
    ),

    (
        [
            "fechar fifa",
            "fechar o fifa",
            "fechar fc 26",
            "fechar o fc 26",
            "fechar ea sports fc",
            "fechar ea sports"
        ],
        "Fechando o EA SPORTS FC 26.",
        fechar_fc26
    ),

    (
        [
            "fechar brave",
            "fechar navegador",
            "fechar o brave"
        ],
        "Fechando o Brave.",
        lambda: matar_processo(
            "brave.exe"
        )
    ),

    (
        [
            "fechar discord",
            "fechar o discord"
        ],
        "Fechando o Discord.",
        lambda: matar_processo(
            "Discord.exe"
        )
    ),

    (
        [
            "fechar vs code",
            "fechar vscode",
            "fechar visual studio code"
        ],
        "Fechando o Visual Studio Code.",
        lambda: matar_processo(
            "Code.exe"
        )
    ),

    (
        [
            "fechar steam",
            "fechar a steam"
        ],
        "Fechando a Steam.",
        lambda: matar_processo(
            "steam.exe"
        )
    ),

    (
        [
            "fechar powershell",
            "fechar power shell",
            "fechar o powershell"
        ],
        "Fechando o PowerShell.",
        lambda: matar_processo(
            "powershell.exe"
        )
    ),

    (
        [
            "fechar cmd",
            "fechar terminal",
            "fechar prompt"
        ],
        "Fechando o terminal.",
        lambda: matar_processo(
            "cmd.exe"
        )
    ),

    (
        [
            "abrir arquivos",
            "abrir arquivo",
            "abrir explorador"
        ],
        "Abrindo o explorador de arquivos.",
        lambda: pyautogui.hotkey(
            "win",
            "e"
        )
    ),

    (
        [
            "aumentar volume",
            "aumentar o volume",
            "aumenta o volume"
        ],
        "Aumentando o volume.",
        lambda: [
            pyautogui.press(
                "volumeup"
            )
            for _ in range(10)
        ]
    ),

    (
        [
            "diminuir volume",
            "diminuir o volume",
            "baixar volume",
            "abaixar volume"
        ],
        "Diminuindo o volume.",
        lambda: [
            pyautogui.press(
                "volumedown"
            )
            for _ in range(10)
        ]
    ),

    (
        [
            "mutar",
            "mudo",
            "silenciar"
        ],
        "Silenciando o computador.",
        lambda: pyautogui.press(
            "volumemute"
        )
    ),

    (
        [
            "menu iniciar",
            "abrir menu iniciar",
            "abrir o menu iniciar",
            "abrir menu windows",
            "abrir o menu windows"
        ],
        "Abrindo o menu iniciar.",
        lambda: pyautogui.press(
            "win"
        )
    ),

    (
        [
            "mostrar área de trabalho",
            "mostrar area de trabalho",
            "mostrar desktop"
        ],
        "Mostrando a área de trabalho.",
        lambda: pyautogui.hotkey(
            "win",
            "d"
        )
    ),

    (
        [
            "trocar de janela",
            "alternar janela",
            "próxima janela",
            "proxima janela"
        ],
        "Trocando de janela.",
        lambda: pyautogui.hotkey(
            "alt",
            "tab"
        )
    ),

    (
        [
            "fechar janela",
            "fechar isso",
            "fechar programa atual"
        ],
        "Fechando a janela atual.",
        lambda: pyautogui.hotkey(
            "alt",
            "f4"
        )
    ),

    (
        [
            "minimizar janela",
            "minimizar programa"
        ],
        "Minimizando a janela.",
        lambda: pyautogui.hotkey(
            "win",
            "down"
        )
    ),

    (
        [
            "maximizar janela",
            "maximizar programa"
        ],
        "Maximizando a janela.",
        lambda: pyautogui.hotkey(
            "win",
            "up"
        )
    ),

    (
        [
            "abrir configurações",
            "abrir configuracoes",
            "abrir configurações do windows"
        ],
        "Abrindo as configurações.",
        lambda: pyautogui.hotkey(
            "win",
            "i"
        )
    ),

    (
        [
            "abrir gerenciador",
            "abrir gerenciador de tarefas"
        ],
        "Abrindo o gerenciador de tarefas.",
        lambda: pyautogui.hotkey(
            "ctrl",
            "shift",
            "esc"
        )
    ),

    (
        [
            "abrir calculadora"
        ],
        "Abrindo a calculadora.",
        lambda: subprocess.Popen(
            "calc.exe"
        )
    ),

    (
        [
            "abrir bloco de notas",
            "abrir notepad"
        ],
        "Abrindo o bloco de notas.",
        lambda: subprocess.Popen(
            "notepad.exe"
        )
    ),

    (
        [
            "abrir paint"
        ],
        "Abrindo o Paint.",
        lambda: subprocess.Popen(
            "mspaint.exe"
        )
    ),

    (
        [
            "abrir terminal",
            "abrir cmd",
            "abrir prompt"
        ],
        "Abrindo o terminal.",
        lambda: subprocess.Popen(
            "cmd.exe"
        )
    ),

    (
        [
            "abrir powershell",
            "abrir power shell"
        ],
        "Abrindo o PowerShell.",
        lambda: subprocess.Popen(
            "powershell.exe"
        )
    ),

    (
        [
            "copiar"
        ],
        "Copiando.",
        lambda: pyautogui.hotkey(
            "ctrl",
            "c"
        )
    ),

    (
        [
            "colar"
        ],
        "Colando.",
        lambda: pyautogui.hotkey(
            "ctrl",
            "v"
        )
    ),

    (
        [
            "desfazer"
        ],
        "Desfazendo.",
        lambda: pyautogui.hotkey(
            "ctrl",
            "z"
        )
    ),

    (
        [
            "salvar",
            "salvar arquivo"
        ],
        "Salvando.",
        lambda: pyautogui.hotkey(
            "ctrl",
            "s"
        )
    ),

    (
        [
            "selecionar tudo"
        ],
        "Selecionando tudo.",
        lambda: pyautogui.hotkey(
            "ctrl",
            "a"
        )
    ),

    (
        [
            "bloquear computador",
            "bloquear pc"
        ],
        "Bloqueando o computador.",
        lambda: pyautogui.hotkey(
            "win",
            "l"
        )
    ),

    (
        [
            "desligar computador",
            "desligar o computador",
            "desligar pc"
        ],
        "Desligando o computador em trinta segundos.",
        lambda: os.system(
            "shutdown /s /t 30"
        )
    ),

    (
        [
            "cancelar desligamento",
            "cancelar o desligamento"
        ],
        "Desligamento cancelado.",
        lambda: os.system(
            "shutdown /a"
        )
    ),

    (
        [
            "reiniciar computador",
            "reiniciar pc"
        ],
        "Reiniciando o computador em trinta segundos.",
        lambda: os.system(
            "shutdown /r /t 30"
        )
    ),

    (
        [
            "cancelar reinicialização",
            "cancelar reinicializacao"
        ],
        "Reinicialização cancelada.",
        lambda: os.system(
            "shutdown /a"
        )
    ),

]


# ============================================================
# PREFIXOS DE PESQUISA NA INTERNET
# ============================================================

COMANDOS_PESQUISA = [
    "pesquise ",
    "pesquisar ",
    "pesquisa ",
    "procure na internet ",
    "procura na internet ",
    "pesquise na internet ",
    "pesquisar na internet ",
    "busque na internet ",
    "buscar na internet "
]


# ============================================================
# EXECUTAR COMANDO
# ============================================================

def executar_comando_sistema(
    comando,
    usar_voz=True
):
    """
    Interpreta e executa comandos do sistema.
    """

    comando = comando.lower().strip()

    # ========================================================
    # CONTROLE DE MÍDIA / STREAMING
    # ========================================================

    if comando in (
        "pausar",
        "pausa",
        "pause",
        "pausar vídeo",
        "pausar video",
        "pausar o vídeo",
        "pausar o video",
        "pausar filme",
        "pausar série",
        "pausar serie",
    ):

        return pausar_midia(
            usar_voz
        )

    if comando in (
        "continuar",
        "continua",
        "despausar",
        "retomar",
        "retoma",
        "continuar vídeo",
        "continuar video",
        "continuar o vídeo",
        "continuar o video",
    ):

        return continuar_midia(
            usar_voz
        )

    if comando in (
        "próximo episódio",
        "proximo episodio",
        "próximo capítulo",
        "proximo capitulo",
        "próximo",
        "proximo",
        "pular episódio",
        "pular episodio",
        "pular capítulo",
        "pular capitulo",
        "próximo filme",
        "proximo filme",
    ):

        return proximo_episodio(
            usar_voz
        )

    if comando in (
        "episódio anterior",
        "episodio anterior",
        "voltar episódio",
        "voltar episodio",
        "voltar capítulo",
        "voltar capitulo",
        "anterior",
    ):

        return episodio_anterior(
            usar_voz
        )

    if (
        "avançar" in comando
        or "avancar" in comando
        or "avança" in comando
        or "avanca" in comando
    ):

        return avancar_midia(
            usar_voz
        )

    if (
        "voltar" in comando
        or "retroceder" in comando
        or "retroceda" in comando
    ):

        return voltar_midia(
            usar_voz
        )

    # ========================================================
    # STREAMINGS EXISTENTES
    #
    # Mantido exatamente antes da pesquisa geral.
    # ========================================================

    if controlar_streamings(
        comando,
        usar_voz
    ):

        return True

    # ========================================================
    # PESQUISA NA INTERNET
    # ========================================================

    for inicio in COMANDOS_PESQUISA:

        if comando.startswith(
            inicio
        ):

            consulta = comando[
                len(inicio):
            ].strip()

            return pesquisar_internet(
                consulta,
                usar_voz
            )

    # ========================================================
    # MÚSICA
    # ========================================================

    if controlar_musica(
        comando,
        usar_voz
    ):

        return True

    # ========================================================
    # YOUTUBE
    # ========================================================

    if tocar_youtube(
        comando,
        usar_voz
    ):

        return True

    # ========================================================
    # DEEZER
    # ========================================================

    if controlar_deezer(
        comando,
        usar_voz
    ):

        return True

    # ========================================================
    # FECHAR EXPLORADOR
    # ========================================================

    if bate(
        comando,
        "fechar explorador",
        "fechar arquivos",
        "fechar arquivo"
    ):

        janelas = fechar_janelas_explorador()

        if janelas:

            falar(
                "Fechando o explorador de arquivos.",
                usar_voz
            )

        else:

            falar(
                "Nenhuma janela do explorador de arquivos "
                "está aberta.",
                usar_voz
            )

        return True

    # ========================================================
    # ATUALIZAR PÁGINA
    # ========================================================

    if bate(
        comando,
        "atualizar página",
        "atualizar pagina",
        "recarregar página",
        "recarregar pagina"
    ):

        falar(
            "Atualizando a página.",
            usar_voz
        )

        pyautogui.hotkey(
            "ctrl",
            "r"
        )

        return True

    # ========================================================
    # VOLTAR PÁGINA
    # ========================================================

    if bate(
        comando,
        "voltar página",
        "voltar pagina",
        "página anterior",
        "pagina anterior"
    ):

        falar(
            "Voltando para a página anterior.",
            usar_voz
        )

        pyautogui.hotkey(
            "alt",
            "left"
        )

        return True

    # ========================================================
    # AVANÇAR PÁGINA
    # ========================================================

    if bate(
        comando,
        "avançar página",
        "avancar pagina",
        "próxima página",
        "proxima pagina"
    ):

        falar(
            "Avançando para a próxima página.",
            usar_voz
        )

        pyautogui.hotkey(
            "alt",
            "right"
        )

        return True

    # ========================================================
    # DOWNLOADS / HISTÓRICO
    # ========================================================

    if bate(
        comando,
        "abrir downloads",
        "abrir meus downloads",
        "abrir histórico do navegador",
        "abrir historico do navegador"
    ):

        falar(
            "Abrindo a área solicitada do navegador.",
            usar_voz
        )

        if "download" in comando:

            pyautogui.hotkey(
                "ctrl",
                "j"
            )

        else:

            pyautogui.hotkey(
                "ctrl",
                "h"
            )

        return True

    # ========================================================
    # ENTER
    # ========================================================

    if bate(
        comando,
        "pressionar enter",
        "apertar enter"
    ):

        falar(
            "Enter.",
            usar_voz
        )

        pyautogui.press(
            "enter"
        )

        return True

    # ========================================================
    # ESC
    # ========================================================

    if bate(
        comando,
        "pressionar escape",
        "pressionar esc",
        "apertar escape"
    ):

        falar(
            "Escape.",
            usar_voz
        )

        pyautogui.press(
            "esc"
        )

        return True

    # ========================================================
    # ROLAR PARA BAIXO
    # ========================================================

    if bate(
        comando,
        "rolar para baixo",
        "descer página",
        "descer pagina"
    ):

        pyautogui.scroll(
            -5
        )

        return True

    # ========================================================
    # ROLAR PARA CIMA
    # ========================================================

    if bate(
        comando,
        "rolar para cima",
        "subir página",
        "subir pagina"
    ):

        pyautogui.scroll(
            5
        )

        return True

    # ========================================================
    # COMANDOS PADRÃO
    # ========================================================

    for frases, mensagem, acao in COMANDOS_SISTEMA:

        if bate(
            comando,
            *frases
        ):

            falar(
                mensagem,
                usar_voz
            )

            acao()

            return True

    # ========================================================
    # ABRIR QUALQUER PROGRAMA
    # ========================================================

    if comando.startswith(
        "abrir "
    ):

        programa = comando.replace(
            "abrir ",
            "",
            1
        ).strip()

        if programa.startswith(
            "o "
        ):

            programa = programa[2:]

        elif programa.startswith(
            "a "
        ):

            programa = programa[2:]

        falar(
            f"Abrindo {programa}.",
            usar_voz
        )

        abrir_aplicativo(
            programa
        )

        return True

    return False