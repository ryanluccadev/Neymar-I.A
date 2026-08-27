"""
Automação de serviços de streaming pelo Brave.
"""

import os
import subprocess
import urllib.parse

from .audio import falar


# ============================================================
# STREAMINGS
# ============================================================

STREAMINGS = {
    "netflix": {
        "nome": "Netflix",
        "url": "https://www.netflix.com/br/",
        "pesquisa": "https://www.netflix.com/search?q={}"
    },

    "prime": {
        "nome": "Prime Video",
        "url": "https://www.primevideo.com/region/na/?ref_=atv_auth_pre",
        "pesquisa": "https://www.primevideo.com/region/na/?ref_=atv_auth_pre"
    },

    "prime video": {
        "nome": "Prime Video",
        "url": "https://www.primevideo.com/region/na/?ref_=atv_auth_pre",
        "pesquisa": "https://www.primevideo.com/region/na/?ref_=atv_auth_pre"
    },

    "pobreflix": {
        "nome": "Pobreflix",
        "url": "https://filmehdsub.info/",
        "pesquisa": "https://filmehdsub.info/?s={}"
    },
}


# ============================================================
# ABRIR DIRETAMENTE NO BRAVE
# ============================================================

def _abrir_no_brave(url):
    """
    Abre uma URL diretamente no navegador Brave.
    """

    caminhos_brave = [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",

        r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",

        os.path.expandvars(
            r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"
        ),
    ]

    for caminho in caminhos_brave:

        if os.path.exists(caminho):

            subprocess.Popen(
                [caminho, url],
                shell=False
            )

            return True

    # Caso o Brave esteja disponível no PATH do Windows.
    try:

        subprocess.Popen(
            ["brave.exe", url],
            shell=False
        )

        return True

    except FileNotFoundError:

        return False


# ============================================================
# NORMALIZAR CONSULTA
# ============================================================

def _normalizar_consulta(texto):
    """
    Remove espaços desnecessários da pesquisa.
    """

    return " ".join(
        texto.strip().split()
    )


# ============================================================
# ABRIR STREAMING
# ============================================================

def abrir_streaming(
    servico,
    usar_voz=True
):
    """
    Abre diretamente o streaming no Brave.
    """

    dados = STREAMINGS.get(
        servico
    )

    if not dados:

        return False

    sucesso = _abrir_no_brave(
        dados["url"]
    )

    if sucesso:

        falar(
            f"Abrindo a {dados['nome']} no Brave.",
            usar_voz
        )

    else:

        falar(
            "Não consegui localizar o Brave.",
            usar_voz
        )

    return sucesso


# ============================================================
# PESQUISAR NO STREAMING
# ============================================================

def pesquisar_streaming(
    servico,
    titulo,
    usar_voz=True
):
    """
    Pesquisa um filme ou série no streaming.

    Netflix:
        Abre diretamente a pesquisa da Netflix.

    Pobreflix:
        Abre diretamente a pesquisa da Pobreflix.

    Prime Video:
        Abre diretamente o Prime Video no Brave.
        O Prime Video controla a pesquisa internamente
        pelo próprio site.
    """

    dados = STREAMINGS.get(
        servico
    )

    titulo = _normalizar_consulta(
        titulo
    )

    if not dados or not titulo:

        return False

    # --------------------------------------------------------
    # NETFLIX
    # --------------------------------------------------------

    if servico == "netflix":

        consulta = urllib.parse.quote_plus(
            titulo
        )

        url = dados["pesquisa"].format(
            consulta
        )

    # --------------------------------------------------------
    # PRIME VIDEO
    # --------------------------------------------------------

    elif servico in (
        "prime",
        "prime video"
    ):

        url = dados["url"]

    # --------------------------------------------------------
    # POBREFLIX
    # --------------------------------------------------------

    elif servico == "pobreflix":

        consulta = urllib.parse.quote_plus(
            titulo
        )

        url = dados["pesquisa"].format(
            consulta
        )

    else:

        return False

    sucesso = _abrir_no_brave(
        url
    )

    if sucesso:

        falar(
            f"Pesquisando {titulo} na {dados['nome']}.",
            usar_voz
        )

    else:

        falar(
            "Não consegui localizar o Brave.",
            usar_voz
        )

    return sucesso


# ============================================================
# CONTROLAR STREAMINGS
# ============================================================

def controlar_streamings(
    comando,
    usar_voz=True
):
    """
    Reconhece comandos relacionados aos streamings.
    """

    comando = comando.lower().strip()

    # --------------------------------------------------------
    # REMOVE EXPRESSÕES SOBRE O BRAVE
    # --------------------------------------------------------

    expressoes_brave = (
        " no brave",
        " pelo brave",
        " usando brave",
        " usando o brave",
        " no navegador brave",
        " pelo navegador brave",
    )

    for expressao in expressoes_brave:

        comando = comando.replace(
            expressao,
            ""
        )

    comando = comando.strip()

    # ========================================================
    # ABRIR NETFLIX
    # ========================================================

    if comando in (
        "abrir netflix",
        "abrir a netflix",
        "abrir o netflix",
    ):

        return abrir_streaming(
            "netflix",
            usar_voz
        )

    # ========================================================
    # ABRIR PRIME VIDEO
    # ========================================================

    if comando in (
        "abrir prime",
        "abrir o prime",
        "abrir a prime",
        "abrir prime video",
        "abrir o prime video",
        "abrir a prime video",
    ):

        return abrir_streaming(
            "prime video",
            usar_voz
        )

    # ========================================================
    # ABRIR POBREFLIX
    # ========================================================

    if comando in (
        "abrir pobreflix",
        "abrir a pobreflix",
        "abrir o pobreflix",
    ):

        return abrir_streaming(
            "pobreflix",
            usar_voz
        )

    # ========================================================
    # PESQUISAS
    # ========================================================

    marcadores = (

        # Netflix
        (" na netflix", "netflix"),
        (" no netflix", "netflix"),
        (" em netflix", "netflix"),

        # Prime Video
        (" no prime video", "prime video"),
        (" na prime video", "prime video"),
        (" em prime video", "prime video"),

        (" no prime", "prime"),
        (" na prime", "prime"),
        (" em prime", "prime"),

        # Pobreflix
        (" na pobreflix", "pobreflix"),
        (" no pobreflix", "pobreflix"),
        (" em pobreflix", "pobreflix"),
    )

    palavras_pesquisa = (
        "pesquisar ",
        "pesquise ",
        "pesquisa ",
        "procurar ",
        "procure ",
        "buscar ",
        "busque ",
        "assistir ",
        "assista ",
        "ver ",
        "veja ",
    )

    for marcador, servico in marcadores:

        if marcador in comando:

            posicao = comando.find(
                marcador
            )

            titulo = comando[
                :posicao
            ].strip()

            for palavra in palavras_pesquisa:

                if titulo.startswith(
                    palavra
                ):

                    titulo = titulo[
                        len(palavra):
                    ].strip()

                    break

            if titulo:

                return pesquisar_streaming(
                    servico,
                    titulo,
                    usar_voz
                )

    # ========================================================
    # PESQUISA PELO PREFIXO
    # ========================================================

    prefixos = (
        ("netflix ", "netflix"),
        ("prime video ", "prime video"),
        ("prime ", "prime"),
        ("pobreflix ", "pobreflix"),
    )

    for prefixo, servico in prefixos:

        if comando.startswith(
            prefixo
        ):

            titulo = comando[
                len(prefixo):
            ].strip()

            if titulo:

                return pesquisar_streaming(
                    servico,
                    titulo,
                    usar_voz
                )

    return False