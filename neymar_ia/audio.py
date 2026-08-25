"""
Entrada e saída de áudio: síntese de voz (TTS via edge-tts + pygame),
reconhecimento de fala (STT via speech_recognition + sounddevice) e
a escuta contínua da frase de ativação "ligar neymar".
"""

import os
import time
import asyncio
import tempfile

import speech_recognition as sr
import sounddevice as sd
import edge_tts
import pygame

from . import config


try:

    pygame.mixer.init()

except Exception as erro:

    print("\nErro ao iniciar o áudio:")
    print(erro)


def falar(texto, usar_voz=True):
    """Imprime e, opcionalmente, reproduz a resposta em voz."""

    print("\nNEYMAR:")
    print(texto)

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

    os.close(descritor)

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

            time.sleep(0.1)

        pygame.mixer.music.unload()

        time.sleep(0.1)

    except Exception as erro:

        print(
            "\nErro ao reproduzir voz:",
            erro
        )

    finally:

        if os.path.exists(arquivo):

            os.remove(arquivo)


def _gravar(duracao):
    """Grava `duracao` segundos de áudio do microfone e retorna um sr.AudioData."""

    audio = sd.rec(
        int(
            duracao * config.TAXA_AMOSTRAGEM_AUDIO
        ),
        samplerate=config.TAXA_AMOSTRAGEM_AUDIO,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    return sr.AudioData(
        audio.tobytes(),
        config.TAXA_AMOSTRAGEM_AUDIO,
        2
    )


def ouvir(duracao=config.DURACAO_ESCUTA_PADRAO):
    """Grava áudio do microfone e retorna o texto reconhecido."""

    reconhecedor = sr.Recognizer()

    try:

        print("\n🎤 Pode falar...")

        audio_data = _gravar(duracao)

        print("🔎 Processando...")

        texto = reconhecedor.recognize_google(
            audio_data,
            language="pt-BR"
        )

        print(
            f"\nVOCÊ: {texto}"
        )

        return texto

    except sr.UnknownValueError:

        print(
            "\nNão consegui entender."
        )

        return None

    except sr.RequestError:

        print(
            "\nErro no reconhecimento de voz."
        )

        return None

    except Exception as erro:

        print(
            "\nERRO NO MICROFONE:",
            erro
        )

        return None


def aguardar_neymar():
    """Espera pela frase de ativação."""

    reconhecedor = sr.Recognizer()

    duracao = config.DURACAO_ESCUTA_ATIVACAO

    while True:

        try:

            audio_data = _gravar(duracao)

            texto = reconhecedor.recognize_google(
                audio_data,
                language="pt-BR"
            ).lower()

            if config.FRASE_ATIVACAO in texto:

                return True

        except (
            sr.UnknownValueError,
            sr.RequestError
        ):

            continue

        except KeyboardInterrupt:

            return False

        except Exception:

            continue
