"""
Configuração central do Neymar IA.

Concentra: chaves de API, nomes de modelos, constantes de tempo/UI
e caminhos de sistema. Nenhum outro módulo deve ler variáveis de
ambiente ou definir "números mágicos" diretamente — tudo passa por aqui.
"""

import os


# ============================================================
# CHAVES DE API
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


# ============================================================
# MODELOS DE IA
# ============================================================

MODELO_GEMINI = "gemini-3.6-flash"
MODELO_GROQ = "openai/gpt-oss-120b"
MODELO_COHERE = "command-a-03-2025"


# ============================================================
# CONSTANTES DE INTERAÇÃO (UI / AUTOMAÇÃO)
# ============================================================

ATRASO_MENU_INICIAR = 0.7
INTERVALO_DIGITACAO = 0.04
ATRASO_ANTES_DO_ENTER = 1
ATRASO_ABERTURA_APP = 3
ATRASO_CARREGAMENTO_YOUTUBE = 5
ATRASO_APOS_CLIQUE_YOUTUBE = 3

# Ponto de clique usado para focar o primeiro resultado do YouTube.
CLIQUE_YOUTUBE_X = 600
CLIQUE_YOUTUBE_Y = 300


# ============================================================
# CONSTANTES DE ÁUDIO
# ============================================================

TAXA_AMOSTRAGEM_AUDIO = 16000
DURACAO_ESCUTA_PADRAO = 6
DURACAO_ESCUTA_ATIVACAO = 3

VOZ_TTS = "pt-BR-AntonioNeural"
TAXA_TTS = "+10%"

FRASE_ATIVACAO = "ligar neymar"


# ============================================================
# CONSTANTES DO WINDOWS
# ============================================================

WM_CLOSE = 0x0010


# ============================================================
# CAMINHOS DE APLICATIVOS
# ============================================================

CAMINHO_FC26 = r"D:\Steam\steamapps\common\FC 26\FC26.exe"


# ============================================================
# HISTÓRICO E MEMÓRIA
# ============================================================

HISTORICO_CONTEXTO = 12
HISTORICO_LISTAGEM = 20
