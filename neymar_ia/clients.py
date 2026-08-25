"""
Inicialização dos clientes de APIs externas (Gemini, Groq, Cohere, Tavily).

Cada cliente é criado uma única vez neste módulo e reaproveitado pelo
resto da aplicação via import. Se uma chave estiver ausente ou a criação
falhar, o cliente correspondente permanece None e os módulos que o usam
tratam essa ausência (ver neymar_ia/ia.py e neymar_ia/pesquisa.py).
"""

from google import genai
from groq import Groq
import cohere
from tavily import TavilyClient

from . import config


gemini_cliente = None
groq_cliente = None
cohere_cliente = None
tavily_cliente = None


def _configurar_gemini():

    global gemini_cliente

    if not config.GEMINI_API_KEY:

        return

    try:

        gemini_cliente = genai.Client(
            api_key=config.GEMINI_API_KEY
        )

    except Exception as erro:

        print("[!] Erro ao configurar Gemini:")
        print(erro)


def _configurar_groq():

    global groq_cliente

    if not config.GROQ_API_KEY:

        return

    try:

        groq_cliente = Groq(
            api_key=config.GROQ_API_KEY
        )

    except Exception as erro:

        print("[!] Erro ao configurar Groq:")
        print(erro)


def _configurar_cohere():

    global cohere_cliente

    if not config.COHERE_API_KEY:

        return

    try:

        cohere_cliente = cohere.ClientV2(
            api_key=config.COHERE_API_KEY
        )

    except Exception as erro:

        print("[!] Erro ao configurar Cohere:")
        print(erro)


def _configurar_tavily():

    global tavily_cliente

    if not config.TAVILY_API_KEY:

        print("[!] TAVILY_API_KEY não encontrada.")

        return

    try:

        tavily_cliente = TavilyClient(
            api_key=config.TAVILY_API_KEY
        )


    except Exception as erro:

        print("[!] Erro ao configurar Tavily:")
        print(erro)


def inicializar_clientes():
    """Configura todos os clientes de API. Chamado uma vez na inicialização."""

    _configurar_gemini()
    _configurar_groq()
    _configurar_cohere()
    _configurar_tavily()


# Mantém o comportamento original: os clientes já ficam configurados
# assim que o módulo é importado, sem exigir uma chamada explícita.
inicializar_clientes()
