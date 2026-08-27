"""
Entrada e saída de áudio do Neymar IA.

- TTS via edge-tts + pygame
- STT via SpeechRecognition + Google
- Captura via sounddevice
- Escuta contínua da frase "ligar Neymar"
- Compatível com PyCharm e PyInstaller
"""

import os
import sys
import time
import asyncio
import tempfile
import threading

import speech_recognition as sr
import sounddevice as sd
import edge_tts
import pygame

from . import config


# ============================================================
# CONFIGURAÇÃO
# ============================================================

AUDIO_LOCK = threading.Lock()

# Taxas de amostragem candidatas, testadas em ordem até uma
# funcionar no dispositivo detectado. Isso evita o erro clássico
# do Windows/WASAPI "OSError(22, 'Não há suporte para o pedido')",
# que acontece quando se força uma taxa (ex.: 16000 Hz) que o
# driver do microfone não aceita em modo compartilhado.
TAXAS_CANDIDATAS = (16000, 48000, 44100, 32000, 22050, 8000)

CANAIS_AUDIO = 1

IDIOMA = "pt-BR"

# Cache do dispositivo/taxa que já se provou funcional, para não
# precisar redescobrir a cada gravação.
_DISPOSITIVO_CACHE = None
_TAXA_CACHE = None


# ============================================================
# PREPARAÇÃO PARA PYINSTALLER
# ============================================================

def _preparar_audio_executavel():

    try:

        if not getattr(sys, "frozen", False):
            return

        base_dir = getattr(
            sys,
            "_MEIPASS",
            None
        )

        if not base_dir:
            return

        caminhos = [
            base_dir,
            os.path.join(
                base_dir,
                "_sounddevice_data"
            ),
        ]

        for caminho in caminhos:

            if not os.path.isdir(caminho):
                continue

            try:
                os.add_dll_directory(caminho)
            except Exception:
                pass

            os.environ["PATH"] = (
                caminho
                + os.pathsep
                + os.environ.get(
                    "PATH",
                    ""
                )
            )

    except Exception as erro:

        print(
            "\n⚠️ Aviso ao preparar áudio:"
        )

        print(
            repr(erro)
        )


_preparar_audio_executavel()


# ============================================================
# PYGAME
# ============================================================

try:

    pygame.mixer.init()

    print(
        "✓ Sistema de áudio inicializado."
    )

except Exception as erro:

    print(
        "\n⚠️ Erro ao iniciar áudio:"
    )

    print(
        repr(erro)
    )


# ============================================================
# MICROFONE
# ============================================================

def _localizar_microfone(forcar_nova_busca=False):
    """
    Descobre qual dispositivo de entrada usar.

    Em vez de depender de um índice fixo (que muda de PC pra PC,
    de reinicialização pra reinicialização, e entre execução via
    PyCharm x .exe), o Neymar procura o dispositivo:

    1. Pelo nome configurado em config.MICROFONE_PREFERIDO
       (ou variável de ambiente NEYMAR_MICROFONE), se definido;
    2. Pelo microfone padrão do Windows;
    3. Pelo primeiro dispositivo de entrada disponível.
    """

    global _DISPOSITIVO_CACHE

    if _DISPOSITIVO_CACHE is not None and not forcar_nova_busca:
        return _DISPOSITIVO_CACHE

    dispositivos = sd.query_devices()

    # 1) Nome preferido definido pelo usuário.
    preferido = getattr(config, "MICROFONE_PREFERIDO", None)

    if preferido:

        preferido_lower = preferido.lower()

        for indice, dispositivo in enumerate(dispositivos):

            if dispositivo["max_input_channels"] <= 0:
                continue

            if preferido_lower in dispositivo["name"].lower():
                _DISPOSITIVO_CACHE = indice
                return indice

    # 2) Dispositivo de entrada padrão do sistema.
    try:

        indice_padrao = sd.default.device[0]

        if indice_padrao is not None and indice_padrao >= 0:

            info_padrao = sd.query_devices(
                indice_padrao,
                "input"
            )

            if info_padrao["max_input_channels"] > 0:
                _DISPOSITIVO_CACHE = indice_padrao
                return indice_padrao

    except Exception:
        pass

    # 3) Primeiro dispositivo de entrada disponível.
    for indice, dispositivo in enumerate(dispositivos):

        if dispositivo["max_input_channels"] > 0:
            _DISPOSITIVO_CACHE = indice
            return indice

    _DISPOSITIVO_CACHE = None
    return None


def verificar_microfone():

    try:

        indice = _localizar_microfone(
            forcar_nova_busca=True
        )

        if indice is None:

            print(
                "\n❌ Nenhum microfone foi encontrado no sistema."
            )

            return False

        info = sd.query_devices(
            indice,
            "input"
        )

        print(
            "\n" + "=" * 55
        )

        print(
            "MICROFONE DO NEYMAR IA"
        )

        print(
            "=" * 55
        )

        print(
            "Índice:",
            indice
        )

        print(
            "Microfone:",
            info["name"]
        )

        print(
            "Canais:",
            info["max_input_channels"]
        )

        print(
            "Sample rate padrão:",
            info["default_samplerate"]
        )

        if info["max_input_channels"] <= 0:

            print(
                "\n❌ O dispositivo não possui entrada."
            )

            return False

        print(
            "\n✓ Microfone encontrado."
        )

        return True

    except Exception as erro:

        print(
            "\n❌ ERRO AO ENCONTRAR MICROFONE:"
        )

        print(
            "Tipo:",
            type(erro).__name__
        )

        print(
            "Detalhes:",
            repr(erro)
        )

        return False


# ============================================================
# TTS
# ============================================================

def falar(texto, usar_voz=True):

    print(
        "\nNEYMAR:"
    )

    print(
        texto
    )

    if not usar_voz:
        return

    texto_limpo = (
        texto
        .replace("*", "")
        .replace("#", "")
    )

    if not texto_limpo.strip():
        return

    descritor, arquivo = tempfile.mkstemp(
        suffix=".mp3"
    )

    os.close(
        descritor
    )

    try:

        async def gerar_audio():

            comunicador = edge_tts.Communicate(
                texto_limpo,
                config.VOZ_TTS,
                rate=config.TAXA_TTS
            )

            await comunicador.save(
                arquivo
            )

        asyncio.run(
            gerar_audio()
        )

        pygame.mixer.music.load(
            arquivo
        )

        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():

            time.sleep(
                0.1
            )

        try:

            pygame.mixer.music.unload()

        except Exception:

            pass

    except Exception as erro:

        print(
            "\n❌ Erro ao reproduzir voz:"
        )

        print(
            repr(erro)
        )

    finally:

        if os.path.exists(arquivo):

            try:
                os.remove(arquivo)
            except Exception:
                pass


# ============================================================
# GRAVAÇÃO
# ============================================================

def _gravar(duracao):

    """
    Grava áudio do microfone detectado automaticamente.

    Em vez de forçar uma taxa de amostragem fixa (o que causava
    o erro "OSError(22, 'Não há suporte para o pedido')" quando o
    driver WASAPI não aceitava 16 kHz), o Neymar testa uma lista
    de taxas candidatas e usa a primeira que o dispositivo aceitar.
    Uma vez encontrada, a combinação (dispositivo, taxa) fica em
    cache para as próximas gravações.
    """

    global _DISPOSITIVO_CACHE, _TAXA_CACHE

    with AUDIO_LOCK:

        indice = _localizar_microfone()

        if indice is None:
            raise RuntimeError(
                "Nenhum microfone disponível para gravação."
            )

        info = sd.query_devices(
            indice,
            "input"
        )

        canais = min(
            CANAIS_AUDIO,
            max(info["max_input_channels"], 1)
        )

        print(
            f"\n🎤 Gravando {duracao:.1f} segundos..."
        )

        print(
            f"🎙️ Microfone: {info['name']}"
        )

        # Monta a lista de taxas a tentar: a que já funcionou antes
        # (se houver), depois a taxa padrão do próprio dispositivo,
        # depois as candidatas conhecidas.
        taxas_para_tentar = []

        if _TAXA_CACHE and _DISPOSITIVO_CACHE == indice:
            taxas_para_tentar.append(_TAXA_CACHE)

        try:
            taxas_para_tentar.append(int(info["default_samplerate"]))
        except Exception:
            pass

        for taxa in TAXAS_CANDIDATAS:
            taxas_para_tentar.append(taxa)

        # Remove duplicadas mantendo a ordem.
        taxas_para_tentar = list(dict.fromkeys(taxas_para_tentar))

        ultimo_erro = None

        for taxa in taxas_para_tentar:

            try:

                quantidade = int(duracao * taxa)

                audio = sd.rec(
                    quantidade,
                    samplerate=taxa,
                    channels=canais,
                    dtype="int16",
                    device=indice
                )

                sd.wait()

                _TAXA_CACHE = taxa
                _DISPOSITIVO_CACHE = indice

                print(
                    "✓ Gravação concluída "
                    f"({taxa} Hz, {canais} canal(is))."
                )

                return audio.tobytes(), taxa, canais

            except Exception as erro:

                ultimo_erro = erro

                print(
                    f"⚠️ Taxa {taxa} Hz não suportada pelo "
                    f"dispositivo, tentando outra..."
                )

                continue

        # Nenhuma taxa funcionou: força uma nova busca de
        # dispositivo na próxima tentativa (pode ter sido
        # desconectado/trocado) e propaga o erro original.
        _DISPOSITIVO_CACHE = None
        _TAXA_CACHE = None

        raise ultimo_erro if ultimo_erro else RuntimeError(
            "Não foi possível gravar áudio com nenhuma taxa testada."
        )


# ============================================================
# RECONHECIMENTO
# ============================================================

def _reconhecer_audio(audio_bytes, taxa, canais=1):

    """
    Converte os bytes capturados pelo sounddevice
    em AudioData do SpeechRecognition.

    É essencial usar aqui a MESMA taxa de amostragem que foi
    realmente usada na gravação (retornada por `_gravar`), senão
    o reconhecimento de fala recebe áudio "acelerado" ou "lento"
    e simplesmente não entende nada.
    """

    audio_data = sr.AudioData(
        audio_bytes,
        taxa,
        2
    )

    reconhecedor = sr.Recognizer()

    # Evita o recognizer considerar a gravação
    # silenciosa de forma inadequada.
    reconhecedor.energy_threshold = 100

    reconhecedor.dynamic_energy_threshold = False

    try:

        texto = reconhecedor.recognize_google(
            audio_data,
            language=IDIOMA
        )

        if texto:

            return texto.strip()

        return None

    except sr.UnknownValueError:

        return None

    except sr.RequestError as erro:

        print(
            "\n❌ Erro de conexão com reconhecimento:"
        )

        print(
            repr(erro)
        )

        return None


# ============================================================
# OUVIR
# ============================================================

def ouvir(
    duracao=config.DURACAO_ESCUTA_PADRAO
):

    try:

        print(
            "\n🎤 Pode falar..."
        )

        audio_bytes, taxa, canais = _gravar(
            duracao
        )

        print(
            "🔎 Reconhecendo..."
        )

        texto = _reconhecer_audio(
            audio_bytes,
            taxa,
            canais
        )

        if not texto:

            print(
                "\nNão consegui entender."
            )

            return None

        print(
            f"\nVOCÊ: {texto}"
        )

        return texto

    except Exception as erro:

        print(
            "\n❌ ERRO DURANTE A ESCUTA:"
        )

        print(
            "Tipo:",
            type(erro).__name__
        )

        print(
            "Detalhes:",
            repr(erro)
        )

        return None


# ============================================================
# ESCUTA CONTÍNUA
# ============================================================

def aguardar_neymar():

    """
    Fica ouvindo continuamente até detectar
    a frase de ativação.
    """

    duracao = 3.0

    frase_ativacao = (
        config.FRASE_ATIVACAO
        .lower()
        .strip()
    )

    print(
        "\n" + "=" * 55
    )

    print(
        "🎙️ NEYMAR IA - ESCUTA CONTÍNUA"
    )

    print(
        "=" * 55
    )

    print(
        f'Fale: "{config.FRASE_ATIVACAO}"'
    )

    # --------------------------------------------------------
    # MICROFONE
    # --------------------------------------------------------

    if not verificar_microfone():

        print(
            "\n❌ Neymar não conseguiu acessar o microfone."
        )

        return False

    print(
        "\n✓ Microfone pronto."
    )

    print(
        f'\n🎙️ Aguardando: "{config.FRASE_ATIVACAO}"'
    )

    # --------------------------------------------------------
    # LOOP
    # --------------------------------------------------------

    while True:

        try:

            print(
                "\n🎤 Escutando..."
            )

            audio_bytes, taxa, canais = _gravar(
                duracao
            )

            print(
                "🔎 Reconhecendo..."
            )

            texto = _reconhecer_audio(
                audio_bytes,
                taxa,
                canais
            )

            if not texto:

                print(
                    "... não consegui entender."
                )

                continue

            texto_normalizado = (
                texto
                .lower()
                .strip()
            )

            print(
                f'\n👂 Você disse: "{texto_normalizado}"'
            )

            # ------------------------------------------------
            # FRASE DE ATIVAÇÃO
            # ------------------------------------------------

            if frase_ativacao in texto_normalizado:

                print(
                    "\n" + "=" * 55
                )

                print(
                    "🟢 NEYMAR ATIVADO!"
                )

                print(
                    "=" * 55
                )

                return True

        except KeyboardInterrupt:

            print(
                "\n🛑 Escuta interrompida."
            )

            return False

        except Exception as erro:

            print(
                "\n❌ ERRO DURANTE A ESCUTA:"
            )

            print(
                "Tipo:",
                type(erro).__name__
            )

            print(
                "Detalhes:",
                repr(erro)
            )

            time.sleep(
                1
            )

            continue