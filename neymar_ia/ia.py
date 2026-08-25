"""
Camada de acesso aos modelos de linguagem.

Expõe uma função por provedor (Gemini, Groq, Cohere) e uma função de
orquestração `perguntar_neymar` que tenta cada provedor em ordem,
usando o próximo apenas se o anterior falhar.
"""

from . import config
from .clients import gemini_cliente, groq_cliente, cohere_cliente


def perguntar_gemini(mensagem):
    """Envia mensagem ao Gemini."""

    if not gemini_cliente:

        raise Exception(
            "Gemini não configurado."
        )

    resposta = gemini_cliente.models.generate_content(
        model=config.MODELO_GEMINI,
        contents=mensagem
    )

    if not resposta:

        raise Exception(
            "Gemini não retornou resposta."
        )

    texto = getattr(
        resposta,
        "text",
        None
    )

    if not texto:

        raise Exception(
            "Gemini retornou resposta vazia."
        )

    return texto


def perguntar_groq(mensagem):
    """Envia mensagem ao Groq."""

    if not groq_cliente:

        raise Exception(
            "Groq não configurado."
        )

    print(
        f"[Groq] Modelo utilizado: {config.MODELO_GROQ}"
    )

    resposta = groq_cliente.chat.completions.create(
        model=config.MODELO_GROQ,
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é Neymar IA, um assistente virtual "
                    "em português do Brasil. "
                    "Responda SEMPRE em português do Brasil, "
                    "mesmo quando receber informações em inglês. "
                    "Responda de maneira objetiva."
                )
            },
            {
                "role": "user",
                "content": mensagem
            }
        ],
        temperature=0.7
    )

    texto = resposta.choices[0].message.content

    if not texto:

        raise Exception(
            "Groq retornou resposta vazia."
        )

    return texto


def perguntar_cohere(mensagem):
    """Envia mensagem à Cohere."""

    if not cohere_cliente:

        raise Exception(
            "Cohere não configurado."
        )

    resposta = cohere_cliente.chat(
        model=config.MODELO_COHERE,
        messages=[
            {
                "role": "user",
                "content": mensagem
            }
        ]
    )

    texto = None

    try:

        texto = resposta.message.content[0].text

    except Exception:

        try:

            texto = resposta.message.content.text

        except Exception:

            pass

    if not texto:

        raise Exception(
            "Cohere retornou resposta vazia."
        )

    return texto


def perguntar_neymar(mensagem):
    """Tenta Gemini, depois Groq e finalmente Cohere."""

    print(
        "\n[1/3] Tentando Gemini..."
    )

    try:

        resposta = perguntar_gemini(
            mensagem
        )

        print(
            "[OK] Gemini respondeu."
        )

        return resposta

    except Exception as erro:

        print(
            "\n[!] Gemini apresentou erro:"
        )

        print(
            erro
        )

    print(
        "\n[2/3] Tentando Groq..."
    )

    try:

        resposta = perguntar_groq(
            mensagem
        )

        print(
            "[OK] Groq respondeu."
        )

        return resposta

    except Exception as erro:

        print(
            "\n[!] Groq apresentou erro:"
        )

        print(
            erro
        )

    print(
        "\n[3/3] Tentando Cohere..."
    )

    try:

        resposta = perguntar_cohere(
            mensagem
        )

        print(
            "[OK] Cohere respondeu."
        )

        return resposta

    except Exception as erro:

        print(
            "\n[!] Cohere apresentou erro:"
        )

        print(
            erro
        )

    return (
        "No momento, todas as minhas APIs "
        "de inteligência artificial estão indisponíveis. "
        "Tente novamente daqui a pouco."
    )
