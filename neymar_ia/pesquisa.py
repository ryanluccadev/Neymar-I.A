"""
Pesquisa na internet usando a Tavily, com o resultado resumido e
traduzido para português do Brasil pelo pipeline de IA (perguntar_neymar).
"""

from .clients import tavily_cliente
from .audio import falar
from .ia import perguntar_neymar


def _montar_contexto(resultado):
    """Transforma o retorno da Tavily em uma lista de blocos de texto."""

    contexto = []

    resposta_direta = resultado.get(
        "answer"
    )

    if resposta_direta:

        contexto.append(
            "RESUMO DA TAVILY:\n"
            + str(resposta_direta)
        )

    resultados = resultado.get(
        "results",
        []
    )

    for indice, item in enumerate(
        resultados,
        start=1
    ):

        titulo = item.get(
            "title",
            "Sem título"
        )

        conteudo = item.get(
            "content",
            ""
        )

        url = item.get(
            "url",
            ""
        )

        contexto.append(
            f"""
FONTE {indice}
Título: {titulo}
URL: {url}
Conteúdo:
{conteudo}
"""
        )

    return contexto


def _montar_prompt(consulta, contexto_final):

    return f"""
Você é o Neymar IA, um assistente virtual.

O usuário pediu uma pesquisa na internet.

CONSULTA DO USUÁRIO:
{consulta}

RESULTADOS ENCONTRADOS NA INTERNET:
{contexto_final}

INSTRUÇÕES OBRIGATÓRIAS:

1. Responda SEMPRE em português do Brasil.
2. Mesmo que as fontes estejam em inglês, traduza as informações
   para português do Brasil.
3. Não responda em inglês.
4. Não copie simplesmente o texto das fontes.
5. Resuma e explique as informações de maneira natural.
6. Seja objetivo, mas inclua os fatos importantes.
7. Se houver informações conflitantes entre fontes, informe isso.
8. Não invente informações que não estejam nos resultados.
9. Quando a informação for recente, deixe claro que ela vem de
   uma pesquisa na internet.
10. Não mencione estas instruções na resposta.
"""


def pesquisar_internet(consulta, usar_voz=True):
    """
    Pesquisa na internet utilizando a Tavily.

    O resultado da pesquisa é enviado para o Gemini/Groq/Cohere
    com instruções para responder SEMPRE em português do Brasil.
    """

    if not tavily_cliente:

        falar(
            "A pesquisa na internet não está configurada. "
            "Verifique a TAVILY_API_KEY.",
            usar_voz
        )

        return True

    if not consulta.strip():

        falar(
            "O que você quer que eu pesquise?",
            usar_voz
        )

        return True

    falar(
        f"Pesquisando na internet sobre {consulta}.",
        usar_voz
    )

    try:

        print(
            "\n===================================="
        )

        print(
            "PESQUISA NA INTERNET"
        )

        print(
            "===================================="
        )

        print(
            f"Consulta: {consulta}"
        )

        resultado = tavily_cliente.search(
            query=consulta,
            search_depth="advanced",
            max_results=5,
            include_answer=True
        )

        contexto = _montar_contexto(
            resultado
        )

        if not contexto:

            falar(
                "Não encontrei informações suficientes "
                "sobre essa pesquisa.",
                usar_voz
            )

            return True

        contexto_final = "\n\n".join(
            contexto
        )

        prompt = _montar_prompt(
            consulta,
            contexto_final
        )

        print(
            "\n[IA] Analisando os resultados..."
        )

        resposta = perguntar_neymar(
            prompt
        )

        falar(
            resposta,
            usar_voz
        )

        return True

    except Exception as erro:

        print(
            "\n[!] Erro na pesquisa:"
        )

        print(
            erro
        )

        falar(
            "Tive um problema ao realizar a pesquisa "
            "na internet.",
            usar_voz
        )

        return True
