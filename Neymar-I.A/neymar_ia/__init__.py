"""
Neymar IA — assistente de voz/texto para Windows.

Pacote organizado por responsabilidade:

- config.py    -> constantes, chaves de API, caminhos
- clients.py   -> inicialização dos clientes de API (Gemini, Groq, Cohere, Tavily)
- sistema.py   -> utilitários de SO (processos, URLs, janelas, apps)
- audio.py     -> síntese de voz (TTS), reconhecimento de fala (STT), ativação
- ia.py        -> integração com os provedores de IA e fallback em cascata
- pesquisa.py  -> pesquisa na internet (Tavily) resumida pela IA
- fc26.py      -> abrir/fechar o EA SPORTS FC 26
- youtube.py   -> pesquisar e tocar música no YouTube
- streamings.py -> automação de Netflix e Prime Video pelo Brave
- musica.py    -> controle de mídia do sistema e Deezer
- comandos.py  -> tabela de comandos do sistema + despachante
- modos.py     -> loops de modo voz/texto e máquina de estados principal
- historico.py  -> histórico persistente de conversas em SQLite
- memoria.py   -> memória persistente controlada por comandos explícitos
"""

from .modos import iniciar_assistente, processar_comando

__all__ = [
    "iniciar_assistente",
    "processar_comando",
]
