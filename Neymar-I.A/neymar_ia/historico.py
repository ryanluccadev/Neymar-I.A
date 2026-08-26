"""
Sistema de histórico de conversas do Neymar IA.

Cada conversa possui sua própria sessão.
O histórico é armazenado permanentemente em SQLite.
"""

import os
import sqlite3
from datetime import datetime


# ============================================================
# CONFIGURAÇÃO
# ============================================================

DB_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data"
)

DB_PATH = os.path.join(
    DB_DIR,
    "neymar_historico.db"
)


_sessao_atual = None


# ============================================================
# CONEXÃO
# ============================================================

def _conectar():
    os.makedirs(
        DB_DIR,
        exist_ok=True
    )

    conexao = sqlite3.connect(
        DB_PATH
    )

    conexao.row_factory = sqlite3.Row

    return conexao


# ============================================================
# INICIALIZAÇÃO
# ============================================================

def inicializar():
    """Cria as tabelas caso ainda não existam."""

    with _conectar() as db:

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS sessoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inicio TEXT NOT NULL,
                ultima TEXT NOT NULL
            )
            """
        )

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS mensagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sessao_id INTEGER NOT NULL,
                papel TEXT NOT NULL,
                mensagem TEXT NOT NULL,
                data TEXT NOT NULL,
                FOREIGN KEY (sessao_id)
                    REFERENCES sessoes(id)
                    ON DELETE CASCADE
            )
            """
        )

        db.commit()


# ============================================================
# NOVA SESSÃO
# ============================================================

def nova_sessao():
    """Cria uma nova sessão e a torna a sessão atual."""

    global _sessao_atual

    inicializar()

    agora = datetime.now().isoformat(
        timespec="seconds"
    )

    with _conectar() as db:

        cursor = db.execute(
            """
            INSERT INTO sessoes (
                inicio,
                ultima
            )
            VALUES (?, ?)
            """,
            (
                agora,
                agora
            )
        )

        db.commit()

        _sessao_atual = cursor.lastrowid

    return _sessao_atual


# ============================================================
# SESSÃO ATUAL
# ============================================================

def _obter_sessao_atual():

    global _sessao_atual

    if _sessao_atual is None:

        _sessao_atual = nova_sessao()

    return _sessao_atual


# ============================================================
# SALVAR MENSAGEM
# ============================================================

def salvar_mensagem(papel, mensagem):
    """
    Salva uma mensagem na sessão atual.

    papel:
        usuario
        assistente
    """

    if mensagem is None:
        return

    mensagem = str(mensagem).strip()

    if not mensagem:
        return

    inicializar()

    sessao_id = _obter_sessao_atual()

    agora = datetime.now().isoformat(
        timespec="seconds"
    )

    with _conectar() as db:

        db.execute(
            """
            INSERT INTO mensagens (
                sessao_id,
                papel,
                mensagem,
                data
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                sessao_id,
                papel,
                mensagem,
                agora
            )
        )

        db.execute(
            """
            UPDATE sessoes
            SET ultima = ?
            WHERE id = ?
            """,
            (
                agora,
                sessao_id
            )
        )

        db.commit()


# ============================================================
# ÚLTIMAS MENSAGENS
# ============================================================

def ultimas_mensagens(limite=20):
    """
    Retorna as últimas mensagens da sessão atual.

    Usada pelo ia.py para fornecer contexto à IA.
    """

    inicializar()

    sessao_id = _obter_sessao_atual()

    with _conectar() as db:

        mensagens = db.execute(
            """
            SELECT
                papel,
                mensagem,
                data
            FROM mensagens
            WHERE sessao_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                sessao_id,
                limite
            )
        ).fetchall()

    mensagens = list(
        reversed(mensagens)
    )

    return [
        dict(mensagem)
        for mensagem in mensagens
    ]


# ============================================================
# LISTAR CONVERSAS
# ============================================================

def listar_conversas():
    """
    Retorna todas as sessões.

    A sessão mais recente aparece primeiro.
    """

    inicializar()

    with _conectar() as db:

        sessoes = db.execute(
            """
            SELECT
                s.id,
                s.inicio,
                s.ultima,
                COUNT(m.id) AS quantidade
            FROM sessoes s
            LEFT JOIN mensagens m
                ON m.sessao_id = s.id
            GROUP BY
                s.id,
                s.inicio,
                s.ultima
            ORDER BY s.id DESC
            """
        ).fetchall()

    resultado = []

    for sessao in sessoes:

        dados = dict(sessao)

        resultado.append(
            {
                "id": dados["id"],
                "inicio": dados["inicio"],
                "ultima": dados["ultima"],
                "quantidade": dados["quantidade"],
                "sessao": {
                    "id": dados["id"],
                    "inicio": dados["inicio"],
                    "ultima": dados["ultima"],
                    "quantidade": dados["quantidade"]
                }
            }
        )

    return resultado


# ============================================================
# BUSCAR MENSAGENS DE UMA SESSÃO
# ============================================================

def _buscar_mensagens_sessao(sessao_id):
    """Busca todas as mensagens de uma sessão."""

    try:
        sessao_id = int(sessao_id)
    except (ValueError, TypeError):
        return []

    with _conectar() as db:

        mensagens = db.execute(
            """
            SELECT
                id,
                papel,
                mensagem,
                data
            FROM mensagens
            WHERE sessao_id = ?
            ORDER BY id ASC
            """,
            (
                sessao_id,
            )
        ).fetchall()

    return [
        dict(mensagem)
        for mensagem in mensagens
    ]


# ============================================================
# FORMATAR SESSÃO
# ============================================================

def formatar_sessao(sessao):
    """
    Formata uma sessão completa para exibição.
    """

    if sessao is None:

        return (
            "Não foi possível localizar esta conversa."
        )

    # --------------------------------------------------------
    # Descobre o ID da sessão
    # --------------------------------------------------------

    if isinstance(sessao, dict):

        sessao_id = sessao.get("id")

    else:

        sessao_id = sessao

    try:

        sessao_id = int(
            sessao_id
        )

    except (
        ValueError,
        TypeError
    ):

        return (
            "Não foi possível identificar esta conversa."
        )

    # --------------------------------------------------------
    # Busca as mensagens diretamente no banco
    # --------------------------------------------------------

    mensagens = _buscar_mensagens_sessao(
        sessao_id
    )

    if not mensagens:

        return (
            "Esta conversa ainda não possui mensagens."
        )

    linhas = []

    for mensagem in mensagens:

        papel = mensagem.get(
            "papel",
            ""
        )

        texto = mensagem.get(
            "mensagem",
            ""
        )

        data = mensagem.get(
            "data",
            ""
        )

        # ----------------------------------------------------
        # Nome do remetente
        # ----------------------------------------------------

        if papel == "usuario":

            nome = "VOCÊ"

        elif papel == "assistente":

            nome = "NEYMAR IA"

        else:

            nome = str(
                papel
            ).upper()

        # ----------------------------------------------------
        # Data
        # ----------------------------------------------------

        try:

            horario = datetime.fromisoformat(
                data
            ).strftime(
                "%d/%m/%Y %H:%M"
            )

        except (
            ValueError,
            TypeError
        ):

            horario = str(
                data
            )

        linhas.append(
            f"[{horario}] {nome}:\n"
            f"{texto}"
        )

    return "\n\n".join(
        linhas
    )


# ============================================================
# LIMPAR HISTÓRICO
# ============================================================

def limpar_historico():
    """Apaga todas as sessões e mensagens."""

    global _sessao_atual

    inicializar()

    with _conectar() as db:

        db.execute(
            "DELETE FROM mensagens"
        )

        db.execute(
            "DELETE FROM sessoes"
        )

        db.commit()

    _sessao_atual = None


# ============================================================
# ÚLTIMA SESSÃO
# ============================================================

def obter_ultima_sessao():
    """Retorna a sessão mais recente."""

    inicializar()

    with _conectar() as db:

        sessao = db.execute(
            """
            SELECT
                id,
                inicio,
                ultima
            FROM sessoes
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()

    if not sessao:

        return None

    return dict(sessao)