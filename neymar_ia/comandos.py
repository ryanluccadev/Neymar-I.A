"""
Tabela de comandos do sistema (frases -> ação) e a função de despacho
`executar_comando_sistema`, que tenta interpretar um comando de texto/voz
como uma ação local antes de cair no fallback de IA.
"""

import os
import subprocess

import pyautogui

from .sistema import bate, matar_processo, abrir_url, abrir_aplicativo, fechar_janelas_explorador
from .fc26 import abrir_fc26, fechar_fc26
from .musica import controlar_musica, controlar_deezer
from .youtube import tocar_youtube
from .pesquisa import pesquisar_internet
from .audio import falar


# ============================================================
# TABELA DE COMANDOS DO SISTEMA
# ============================================================

COMANDOS_SISTEMA = [

    (
        ["abrir youtube", "abrir o youtube"],
        "Abrindo o YouTube.",
        lambda: abrir_url(
            "https://www.youtube.com"
        )
    ),

    (
        ["abrir brave", "abrir o brave", "abrir navegador",
         "abrir o navegador"],
        "Abrindo o Brave.",
        lambda: abrir_aplicativo(
            "Brave"
        )
    ),

    (
        ["abrir discord", "abrir o discord"],
        "Abrindo o Discord.",
        lambda: abrir_aplicativo(
            "Discord"
        )
    ),

    (
        ["abrir vs code", "abrir vscode",
         "abrir visual studio code"],
        "Abrindo o Visual Studio Code.",
        lambda: abrir_aplicativo(
            "Visual Studio Code"
        )
    ),

    (
        ["abrir steam", "abrir a steam"],
        "Abrindo a Steam.",
        lambda: abrir_aplicativo(
            "Steam"
        )
    ),

    (
        ["abrir fifa", "abrir o fifa",
         "abrir fc 26", "abrir o fc 26",
         "abrir ea sports fc",
         "abrir ea sports"],
        "Abrindo o EA SPORTS FC 26.",
        abrir_fc26
    ),

    (
        ["fechar fifa", "fechar o fifa",
         "fechar fc 26", "fechar o fc 26",
         "fechar ea sports fc",
         "fechar ea sports"],
        "Fechando o EA SPORTS FC 26.",
        fechar_fc26
    ),

    (
        ["fechar brave", "fechar navegador",
         "fechar o brave"],
        "Fechando o Brave.",
        lambda: matar_processo(
            "brave.exe"
        )
    ),

    (
        ["fechar discord", "fechar o discord"],
        "Fechando o Discord.",
        lambda: matar_processo(
            "Discord.exe"
        )
    ),

    (
        ["fechar vs code", "fechar vscode",
         "fechar visual studio code"],
        "Fechando o Visual Studio Code.",
        lambda: matar_processo(
            "Code.exe"
        )
    ),

    (
        ["fechar steam", "fechar a steam"],
        "Fechando a Steam.",
        lambda: matar_processo(
            "steam.exe"
        )
    ),

    (
        ["fechar powershell", "fechar power shell",
         "fechar o powershell"],
        "Fechando o PowerShell.",
        lambda: matar_processo(
            "powershell.exe"
        )
    ),

    (
        ["fechar cmd", "fechar terminal",
         "fechar prompt"],
        "Fechando o terminal.",
        lambda: matar_processo(
            "cmd.exe"
        )
    ),

    (
        ["abrir arquivos", "abrir arquivo",
         "abrir explorador"],
        "Abrindo o explorador de arquivos.",
        lambda: pyautogui.hotkey(
            "win",
            "e"
        )
    ),

    (
        ["aumentar volume", "aumentar o volume",
         "aumenta o volume"],
        "Aumentando o volume.",
        lambda: [
            pyautogui.press("volumeup")
            for _ in range(10)
        ]
    ),

    (
        ["diminuir volume", "diminuir o volume",
         "baixar volume", "abaixar volume"],
        "Diminuindo o volume.",
        lambda: [
            pyautogui.press("volumedown")
            for _ in range(10)
        ]
    ),

    (
        ["mutar", "mudo", "silenciar"],
        "Silenciando o computador.",
        lambda: pyautogui.press(
            "volumemute"
        )
    ),

    (
        ["menu iniciar", "abrir menu iniciar",
         "abrir o menu iniciar",
         "abrir menu windows",
         "abrir o menu windows"],
        "Abrindo o menu iniciar.",
        lambda: pyautogui.press(
            "win"
        )
    ),

    (
        ["mostrar área de trabalho",
         "mostrar area de trabalho",
         "mostrar desktop"],
        "Mostrando a área de trabalho.",
        lambda: pyautogui.hotkey(
            "win",
            "d"
        )
    ),

    (
        ["trocar de janela", "alternar janela",
         "próxima janela", "proxima janela"],
        "Trocando de janela.",
        lambda: pyautogui.hotkey(
            "alt",
            "tab"
        )
    ),

    (
        ["fechar janela", "fechar isso",
         "fechar programa atual"],
        "Fechando a janela atual.",
        lambda: pyautogui.hotkey(
            "alt",
            "f4"
        )
    ),

    (
        ["minimizar janela",
         "minimizar programa"],
        "Minimizando a janela.",
        lambda: pyautogui.hotkey(
            "win",
            "down"
        )
    ),

    (
        ["maximizar janela",
         "maximizar programa"],
        "Maximizando a janela.",
        lambda: pyautogui.hotkey(
            "win",
            "up"
        )
    ),

    (
        ["abrir configurações",
         "abrir configuracoes",
         "abrir configurações do windows"],
        "Abrindo as configurações.",
        lambda: pyautogui.hotkey(
            "win",
            "i"
        )
    ),

    (
        ["abrir gerenciador",
         "abrir gerenciador de tarefas"],
        "Abrindo o gerenciador de tarefas.",
        lambda: pyautogui.hotkey(
            "ctrl",
            "shift",
            "esc"
        )
    ),

    (
        ["abrir calculadora"],
        "Abrindo a calculadora.",
        lambda: subprocess.Popen(
            "calc.exe"
        )
    ),

    (
        ["abrir bloco de notas",
         "abrir notepad"],
        "Abrindo o bloco de notas.",
        lambda: subprocess.Popen(
            "notepad.exe"
        )
    ),

    (
        ["abrir paint"],
        "Abrindo o Paint.",
        lambda: subprocess.Popen(
            "mspaint.exe"
        )
    ),

    (
        ["abrir terminal",
         "abrir cmd",
         "abrir prompt"],
        "Abrindo o terminal.",
        lambda: subprocess.Popen(
            "cmd.exe"
        )
    ),

    (
        ["abrir powershell",
         "abrir power shell"],
        "Abrindo o PowerShell.",
        lambda: subprocess.Popen(
            "powershell.exe"
        )
    ),

    (
        ["copiar"],
        "Copiando.",
        lambda: pyautogui.hotkey(
            "ctrl",
            "c"
        )
    ),

    (
        ["colar"],
        "Colando.",
        lambda: pyautogui.hotkey(
            "ctrl",
            "v"
        )
    ),

    (
        ["desfazer"],
        "Desfazendo.",
        lambda: pyautogui.hotkey(
            "ctrl",
            "z"
        )
    ),

    (
        ["salvar", "salvar arquivo"],
        "Salvando.",
        lambda: pyautogui.hotkey(
            "ctrl",
            "s"
        )
    ),

    (
        ["selecionar tudo"],
        "Selecionando tudo.",
        lambda: pyautogui.hotkey(
            "ctrl",
            "a"
        )
    ),

    (
        ["bloquear computador",
         "bloquear pc"],
        "Bloqueando o computador.",
        lambda: pyautogui.hotkey(
            "win",
            "l"
        )
    ),

    (
        ["desligar computador",
         "desligar o computador",
         "desligar pc"],
        "Desligando o computador em trinta segundos.",
        lambda: os.system(
            "shutdown /s /t 30"
        )
    ),

    (
        ["cancelar desligamento",
         "cancelar o desligamento"],
        "Desligamento cancelado.",
        lambda: os.system(
            "shutdown /a"
        )
    ),

    (
        ["reiniciar computador",
         "reiniciar pc"],
        "Reiniciando o computador em trinta segundos.",
        lambda: os.system(
            "shutdown /r /t 30"
        )
    ),

    (
        ["cancelar reinicialização",
         "cancelar reinicializacao"],
        "Reinicialização cancelada.",
        lambda: os.system(
            "shutdown /a"
        )
    ),

]


# ============================================================
# PREFIXOS QUE ACIONAM PESQUISA NA INTERNET
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


def executar_comando_sistema(comando, usar_voz=True):
    """Interpreta e executa comandos do sistema."""

    comando = comando.lower().strip()

    # --------------------------------------------------------
    # PESQUISA NA INTERNET
    # --------------------------------------------------------

    for inicio in COMANDOS_PESQUISA:

        if comando.startswith(inicio):

            consulta = comando[
                len(inicio):
            ].strip()

            return pesquisar_internet(
                consulta,
                usar_voz
            )

    # --------------------------------------------------------
    # MÚSICA
    # --------------------------------------------------------

    if controlar_musica(
        comando,
        usar_voz
    ):

        return True

    # --------------------------------------------------------
    # YOUTUBE
    # --------------------------------------------------------

    if tocar_youtube(
        comando,
        usar_voz
    ):

        return True

    # --------------------------------------------------------
    # DEEZER
    # --------------------------------------------------------

    if controlar_deezer(
        comando,
        usar_voz
    ):

        return True

    # --------------------------------------------------------
    # FECHAR EXPLORADOR
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # COMANDOS PADRÃO
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # ABRIR QUALQUER PROGRAMA
    # --------------------------------------------------------

    if comando.startswith("abrir "):

        programa = comando.replace(
            "abrir ",
            "",
            1
        ).strip()

        if programa.startswith("o "):

            programa = programa[2:]

        elif programa.startswith("a "):

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
