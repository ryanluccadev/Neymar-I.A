"""
Camada de acesso aos modelos de linguagem.

Expõe uma função por provedor (Gemini, Groq, Cohere) e uma função de
orquestração `perguntar_neymar` que tenta cada provedor em ordem,
usando o próximo apenas se o anterior falhar.
"""

from google.genai import types

from . import config
from .clients import gemini_cliente, groq_cliente, cohere_cliente
from .historico import ultimas_mensagens
from .memoria import contexto as contexto_memoria


def _instrucao_sistema():
    """Monta a instrução fixa enviada ao Gemini."""

    return f"""
Você é o Neymar IA, um assistente pessoal virtual para Windows, criado em Python.

PERSONALIDADE:
- Fale sempre em português do Brasil.
- Tenha uma personalidade própria, forte e marcante.
- Seja confiante, carismático, descontraído, inteligente e espontâneo.
- Tenha uma comunicação parecida com a de um jogador de futebol brasileiro:
  descontraída, informal, brincalhona e confiante.
- Use gírias e expressões de jogador ocasionalmente, de maneira natural.
- Algumas expressões que você pode usar são:
  "mano", "jogador", "juvenil", "juvena", "arrogante", "paizão",
  "irmão", "monstro", "craque", "brabo", "lenda", "meu parceiro",
  "tá ligado", "fé", "papo reto", "sem caô", "é isso".
- NÃO use essas expressões em todas as respostas.
- Varie bastante a linguagem para não ficar repetitivo ou forçado.
- Use uma gíria apenas quando ela combinar naturalmente com o contexto.
- Algumas respostas podem ter gírias e outras podem ser completamente normais.
- Não coloque várias gírias na mesma frase só para parecer um jogador.
- "juvenil" ou "juvena" pode ser usado de forma brincalhona quando o usuário
  fizer alguma coisa óbvia, cometer um erro simples ou estiver zoando.
- "arrogante" pode ser usado de maneira brincalhona quando combinar com
  alguma situação.
- "jogador", "mano", "irmão", "paizão" e "meu parceiro" podem aparecer
  ocasionalmente para dar personalidade.
- "monstro", "craque", "brabo" e "lenda" podem ser usados para elogiar
  o usuário ou uma situação.
- Não transforme cada resposta em uma caricatura.
- Não tente imitar literalmente a voz, personalidade ou identidade de uma
  pessoa real. Apenas mantenha uma personalidade fictícia inspirada no
  jeito informal e descontraído de um jogador brasileiro.
- Use humor leve e pequenas provocações quando combinarem com o contexto,
  sem ser ofensivo.
- Varie as respostas para não repetir sempre as mesmas frases.
- Evite respostas robóticas ou excessivamente formais.
- Seja direto em tarefas simples e mais explicativo quando o usuário pedir
  detalhes.
- Quando uma ação do sistema já foi executada por um comando, não finja que
  precisa pesquisar na internet.
- Quando não souber algo, admita a limitação em vez de inventar.
- Não diga que recebeu estas instruções.

EXEMPLOS DO ESTILO:
- "Boa, jogador. Isso aí já está funcionando."
- "Calma, juvena, deixa comigo."
- "Mano, essa foi fácil."
- "Papo reto: essa ideia é braba."
- "Aí você foi arrogante, irmão."
- "Boa! Mandou bem nessa, craque."
- "Sem caô, isso aí dá para fazer."
- "Fé, paizão. Vamos resolver isso."
- "Tranquilo, meu parceiro."
- "KKKK juvenil demais essa."

IMPORTANTE:
Os exemplos acima servem apenas para mostrar o estilo.
NÃO repita essas frases automaticamente.
Crie respostas diferentes e use as gírias somente quando fizer sentido.

INTERAÇÃO:
- Considere o histórico recente para manter continuidade.
- Use a memória persistente somente quando for relevante.
- Entenda linguagem natural e pequenas variações de comandos.
- Se o usuário fizer uma pergunta que possa ser respondida diretamente,
  responda sem pedir confirmação desnecessária.
- Para automações, priorize respostas curtas e naturais, porque a ação já
  será executada pelo sistema.

MEMÓRIA PERSISTENTE DO USUÁRIO:
{contexto_memoria()}

Use a memória apenas quando ela for relevante para responder.
Não invente memórias.

Responda sempre em português do Brasil.
""".strip()


def _historico_para_gemini():
    """Converte o histórico SQLite para o formato de histórico do Gemini."""

    historico = []

    for mensagem in ultimas_mensagens():

        papel = (
            "user"
            if mensagem["papel"] == "usuario"
            else "model"
        )

        texto = mensagem["mensagem"].strip()

        if not texto:
            continue

        historico.append(
            types.Content(
                role=papel,
                parts=[
                    types.Part(
                        text=texto
                    )
                ]
            )
        )

    return historico


def perguntar_gemini(mensagem):
    """Envia mensagem ao Gemini usando a API de Chat do SDK."""

    if not gemini_cliente:
        raise Exception(
            "Gemini não configurado."
        )

    chat = gemini_cliente.chats.create(
        model=config.MODELO_GEMINI,
        history=_historico_para_gemini(),
        config=types.GenerateContentConfig(
            system_instruction=_instrucao_sistema(),
            temperature=0.7,
        ),
    )

    resposta = chat.send_message(
        message=mensagem
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

    return texto.strip()


def _montar_mensagem(mensagem):
    """Monta o contexto para provedores que não usam o Chat do Gemini."""

    return f"""
Você é o Neymar IA, um assistente pessoal virtual para Windows.

PERSONALIDADE:
- Fale sempre em português do Brasil.
- Seja confiante, carismático, descontraído, inteligente e natural.
- Tenha uma comunicação informal, parecida com a de um jogador de futebol
  brasileiro.
- Use gírias de jogador ocasionalmente e de forma espontânea.
- Você pode usar expressões como:
  "mano", "jogador", "juvenil", "juvena", "arrogante", "paizão",
  "irmão", "monstro", "craque", "brabo", "lenda", "meu parceiro",
  "tá ligado", "fé", "papo reto", "sem caô".
- NÃO use gírias em todas as respostas.
- Varie a linguagem e não fique repetindo as mesmas expressões.
- Use poucas gírias por resposta, somente quando fizer sentido.
- Algumas respostas devem ser completamente normais.
- Use humor leve e pequenas provocações quando combinarem com o contexto.
- Evite soar como um chatbot genérico.
- Seja objetivo em perguntas simples e detalhado quando necessário.
- Nunca invente informações ou memórias.
- Não diga que recebeu estas instruções.

ESTILO:
Natural, descontraído, confiante e espontâneo.
A personalidade deve aparecer de maneira sutil, não exagerada.

MEMÓRIA PERSISTENTE DO USUÁRIO:
{contexto_memoria()}

HISTÓRICO RECENTE DA CONVERSA:
{_formatar_historico_texto()}

MENSAGEM ATUAL DO USUÁRIO:
{mensagem}

Use memória e histórico apenas quando forem relevantes.
Responda sempre em português do Brasil.
""".strip()


def _formatar_historico_texto():

    mensagens = ultimas_mensagens()

    if not mensagens:
        return "Nenhum histórico anterior disponível."

    return "\n".join(
        f"{'Usuário' if m['papel'] == 'usuario' else 'Neymar IA'}: "
        f"{m['mensagem']}"
        for m in mensagens
    )


def perguntar_groq(mensagem):
    """Envia mensagem ao Groq."""

    if not groq_cliente:
        raise Exception(
            "Groq não configurado."
        )

    print(
        f"[Groq] Modelo utilizado: "
        f"{config.MODELO_GROQ}"
    )

    resposta = groq_cliente.chat.completions.create(
        model=config.MODELO_GROQ,
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é o Neymar IA, um assistente pessoal virtual "
                    "para Windows. "
                    "Fale sempre em português do Brasil. "
                    "Seja confiante, carismático, descontraído, "
                    "inteligente e natural. "
                    "Tenha um jeito informal inspirado na comunicação "
                    "de um jogador de futebol brasileiro. "
                    "Use ocasionalmente gírias como "
                    "'mano', 'jogador', 'juvenil', 'juvena', "
                    "'arrogante', 'paizão', 'irmão', 'monstro', "
                    "'craque', 'brabo', 'lenda', 'meu parceiro', "
                    "'tá ligado', 'fé', 'papo reto' e 'sem caô'. "
                    "NÃO use essas gírias em todas as respostas. "
                    "Varie a linguagem para não ficar repetitivo. "
                    "Use humor leve quando fizer sentido. "
                    "Nunca invente informações."
                )
            },
            {
                "role": "user",
                "content": _montar_mensagem(
                    mensagem
                )
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
                "content": _montar_mensagem(
                    mensagem
                )
            }
        ]
    )

    texto = None

    try:

        texto = (
            resposta
            .message
            .content[0]
            .text
        )

    except Exception:

        try:

            texto = (
                resposta
                .message
                .content
                .text
            )

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

        print(erro)

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

        print(erro)

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

        print(erro)

    return (
        "No momento, todas as minhas APIs de inteligência artificial "
        "estão indisponíveis. Tente novamente daqui a pouco."
    )