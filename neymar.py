import os
import time
import speech_recognition as sr
import sounddevice as sd
import asyncio
import edge_tts
import pygame

from google import genai

# ============================================================
# CONFIGURAÇÃO DA API
# ============================================================

CHAVE_API = os.getenv("GEMINI_API_KEY")

if not CHAVE_API:
    print("\nERRO: GEMINI_API_KEY não encontrada.")
    print("Configure a chave no PowerShell antes de executar.")
    input("\nPressione ENTER para sair...")
    exit()

cliente = genai.Client(
    api_key=CHAVE_API
)

# ============================================================
# CONFIGURAÇÃO DO MODELO
# ============================================================

MODELO = "gemini-3.6-flash"

# ============================================================
# CRIA O CHAT
# ============================================================

try:
    chat = cliente.chats.create(
        model=MODELO
    )

except Exception as erro:
    print("\nERRO AO CRIAR O CHAT:")
    print(erro)
    input("\nPressione ENTER para sair...")
    exit()


# ============================================================
# INICIALIZA O ÁUDIO
# ============================================================

try:
    pygame.mixer.init()

except Exception as erro:
    print("\nErro ao iniciar o reprodutor de áudio:", erro)


# ============================================================
# LIMPAR TELA
# ============================================================

def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


# ============================================================
# FUNÇÃO FALAR
# ============================================================

def falar(texto, usar_voz=True):

    print("\nNEYMAR:")
    print(texto)

    if not usar_voz:
        return

    texto_limpo = texto.replace("*", "").replace("#", "")

    if not texto_limpo.strip():
        return

    arquivo_audio = "resposta.mp3"

    try:

        async def gerar_audio():

            comunicador = edge_tts.Communicate(
                texto_limpo,
                "pt-BR-AntonioNeural",
                rate="+10%"
            )

            await comunicador.save(arquivo_audio)

        asyncio.run(gerar_audio())

        pygame.mixer.music.load(arquivo_audio)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        pygame.mixer.music.unload()

        time.sleep(0.1)

        if os.path.exists(arquivo_audio):
            os.remove(arquivo_audio)

    except Exception as erro:

        print(
            f"\nErro ao gerar ou reproduzir a voz: {erro}"
        )


# ============================================================
# OUVIR ÁUDIO
# ============================================================

def ouvir(duracao=6):

    reconhecedor = sr.Recognizer()
    taxa_amostragem = 16000

    try:

        print("\n🎤 Pode falar...")

        audio = sd.rec(
            int(duracao * taxa_amostragem),
            samplerate=taxa_amostragem,
            channels=1,
            dtype="int16"
        )

        sd.wait()

        print("🔎 Processando...")

        audio_bytes = audio.tobytes()

        audio_data = sr.AudioData(
            audio_bytes,
            taxa_amostragem,
            2
        )

        texto = reconhecedor.recognize_google(
            audio_data,
            language="pt-BR"
        )

        print(f"\nVOCÊ: {texto}")

        return texto

    except sr.UnknownValueError:

        print("\nNão consegui entender.")

        return None

    except sr.RequestError:

        print("\nErro no serviço de reconhecimento.")

        return None

    except Exception as erro:

        print("\nERRO NO MICROFONE:", erro)

        return None


# ============================================================
# AGUARDAR "ALÔ NEYMAR"
# ============================================================

def aguardar_neymar():

    reconhecedor = sr.Recognizer()

    taxa_amostragem = 16000
    duracao_espera = 3

    while True:

        try:

            audio = sd.rec(
                int(duracao_espera * taxa_amostragem),
                samplerate=taxa_amostragem,
                channels=1,
                dtype="int16"
            )

            sd.wait()

            audio_bytes = audio.tobytes()

            audio_data = sr.AudioData(
                audio_bytes,
                taxa_amostragem,
                2
            )

            texto = reconhecedor.recognize_google(
                audio_data,
                language="pt-BR"
            ).lower()

            if "ligar neymar" in texto:
                return True

        except (sr.UnknownValueError, sr.RequestError):

            continue

        except KeyboardInterrupt:

            return False

        except Exception:

            continue


# ============================================================
# PERGUNTAR AO NEYMAR
# ============================================================

def perguntar_neymar(mensagem, tentativas=3):

    for tentativa in range(1, tentativas + 1):

        try:

            resposta = chat.send_message(mensagem)

            if not resposta:
                return "O Neymar não retornou nenhuma resposta."

            texto = resposta.text

            if not texto:
                return "Recebi uma resposta vazia do Neymar."

            return texto

        except Exception as erro:

            erro_texto = str(erro)

            if (
                "503" in erro_texto
                or "UNAVAILABLE" in erro_texto
            ):

                if tentativa < tentativas:

                    time.sleep(tentativa * 3)

                    continue

                return (
                    "O sistema do Neymar está "
                    "com alta demanda no momento."
                )

            if (
                "429" in erro_texto
                or "RESOURCE_EXHAUSTED" in erro_texto
            ):

                return (
                    "A API do Neymar está "
                    "sem cota disponível no momento."
                )

            return (
                "Ocorreu um erro ao conversar "
                "com o Neymar."
            )


# ============================================================
# MODO VOZ
# ============================================================

def modo_voz():

    while True:

        mensagem = ouvir()

        if not mensagem:
            continue

        comando = mensagem.lower().strip()

        # --------------------------------------------
        # DESLIGAR
        # --------------------------------------------

        if (
            "desligar neymar" in comando
            or "desliga neymar" in comando
        ):

            falar(
                "Desligando os sistemas. Até logo, senhor.",
                usar_voz=True
            )

            return "desligar"

        # --------------------------------------------
        # MUDAR PARA TEXTO
        # --------------------------------------------

        if (
            "mudar para texto" in comando
            or "modo texto" in comando
            or "trocar para texto" in comando
        ):

            falar(
                "Mudando para o modo texto.",
                usar_voz=True
            )

            return "texto"

        # --------------------------------------------
        # PERGUNTA NORMAL
        # --------------------------------------------

        resposta = perguntar_neymar(mensagem)

        falar(
            resposta,
            usar_voz=True
        )


# ============================================================
# MODO TEXTO
# ============================================================

def modo_texto():

    while True:

        mensagem = input("\nVOCÊ: ").strip()

        if not mensagem:
            continue

        comando = mensagem.lower()

        # --------------------------------------------
        # DESLIGAR
        # --------------------------------------------

        if (
            "desligar neymar" in comando
            or "desliga neymar" in comando
        ):

            falar(
                "Desligando os sistemas. Até logo, senhor.",
                usar_voz=False
            )

            return "desligar"

        # --------------------------------------------
        # MUDAR PARA VOZ
        # --------------------------------------------

        if (
            "mudar para voz" in comando
            or "modo voz" in comando
            or "trocar para voz" in comando
        ):

            falar(
                "Mudando para o modo voz.",
                usar_voz=False
            )

            return "voz"

        # --------------------------------------------
        # PERGUNTA NORMAL
        # --------------------------------------------

        resposta = perguntar_neymar(mensagem)

        falar(
            resposta,
            usar_voz=False
        )


# ============================================================
# ASSISTENTE PRINCIPAL
# ============================================================

def iniciar_assistente():

    modo = "espera"

    while True:

        # ====================================================
        # MODO ESPERA
        # ====================================================

        if modo == "espera":

            limpar_tela()

            print("=" * 55)
            print("                   NEYMAR IA")
            print("=" * 55)

            print(
                "\n[Aguardando 'Ligar Neymar'... ]"
            )

            acordou = aguardar_neymar()

            if not acordou:
                break

            falar(
                "Sim, senhor?",
                usar_voz=True
            )

            # Ao acordar, começa diretamente em voz
            modo = "voz"

        # ====================================================
        # MODO VOZ
        # ====================================================

        elif modo == "voz":

            resultado = modo_voz()

            if resultado == "texto":

                modo = "texto"

            elif resultado == "desligar":

                break

        # ====================================================
        # MODO TEXTO
        # ====================================================

        elif modo == "texto":

            resultado = modo_texto()

            if resultado == "voz":

                modo = "voz"

            elif resultado == "desligar":

                break


# ============================================================
# INÍCIO DO PROGRAMA
# ============================================================

if __name__ == "__main__":

    try:

        iniciar_assistente()

    except KeyboardInterrupt:

        print("\n\nSistemas desligados.")

    except Exception as erro:

        print("\nERRO INESPERADO:", erro)

        input("\nPressione ENTER para sair...")