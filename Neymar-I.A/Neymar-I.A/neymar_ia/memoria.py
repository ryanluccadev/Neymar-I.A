"""
Memória persistente do Neymar IA.

A memória é controlada por comandos explícitos do usuário.
As informações são armazenadas em SQLite e continuam disponíveis
mesmo depois que o programa é fechado e iniciado novamente.
"""

import os
import sqlite3
import re
from datetime import datetime

from . import config


# ============================================================
# CONFIGURAÇÃO
# ============================================================

DB_DIR = str(config.diretorio_dados())
DB_PATH = os.path.join(DB_DIR, "neymar_ia.db")


# ============================================================
# CONEXÃO
# ============================================================

def _conectar():
    """Cria uma conexão com o banco de dados."""

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
    """Cria a tabela de memórias caso ela não exista."""

    with _conectar() as db:

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS memorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conteudo TEXT NOT NULL,
                criado_em TEXT NOT NULL
            )
            """
        )

        db.commit()


# ============================================================
# SALVAR
# ============================================================

def salvar(conteudo):
    """Salva uma nova memória."""

    conteudo = conteudo.strip()

    if not conteudo:

        return False

    inicializar()

    with _conectar() as db:

        db.execute(
            """
            INSERT INTO memorias (
                conteudo,
                criado_em
            )
            VALUES (?, ?)
            """,
            (
                conteudo,
                datetime.now().isoformat(
                    timespec="seconds"
                )
            )
        )

        db.commit()

    return True


# ============================================================
# LISTAR
# ============================================================

def listar():
    """Retorna todas as memórias salvas."""

    inicializar()

    with _conectar() as db:

        return db.execute(
            """
            SELECT
                id,
                conteudo,
                criado_em
            FROM memorias
            ORDER BY id DESC
            """
        ).fetchall()


# ============================================================
# EXCLUIR
# ============================================================

def excluir(id_memoria):
    """Exclui uma memória pelo ID."""

    inicializar()

    with _conectar() as db:

        cursor = db.execute(
            """
            DELETE FROM memorias
            WHERE id = ?
            """,
            (
                id_memoria,
            )
        )

        db.commit()

        return cursor.rowcount > 0


# ============================================================
# LIMPAR
# ============================================================

def limpar():
    """Apaga todas as memórias."""

    inicializar()

    with _conectar() as db:

        db.execute(
            "DELETE FROM memorias"
        )

        db.commit()


# ============================================================
# CONTEXTO PARA A IA
# ============================================================

def contexto():
    """
    Retorna as memórias em formato de texto para a IA.
    """

    memorias = listar()

    if not memorias:

        return "Nenhuma memória salva."

    return "\n".join(
        f"- {m['conteudo']}"
        for m in memorias
    )


# ============================================================
# PROCESSAR COMANDOS
# ============================================================

def processar_comando(comando):
    """
    Processa comandos relacionados à memória.

    Retorna:
        str  -> quando o comando é de memória
        None -> quando não é um comando de memória
    """

    texto = comando.strip()

    if not texto:

        return None

    normalizado = texto.lower()

    # ========================================================
    # SALVAR MEMÓRIA
    # ========================================================

    prefixos_salvar = (
        "lembre que ",
        "lembre-se que ",
        "lembre de ",
        "memorize que ",
        "memorize ",
        "guarde que ",
        "guarde ",
        "guarde na memória que ",
        "guarde na memoria que ",
        "salve na memória que ",
        "salve na memoria que ",
        "salvar na memória que ",
        "salvar na memoria que ",
        "anote que ",
        "anote ",
    )

    for prefixo in prefixos_salvar:

        if normalizado.startswith(prefixo):

            conteudo = texto[
                len(prefixo):
            ].strip()

            if salvar(conteudo):

                return (
                    f"Entendido. Vou lembrar que {conteudo}"
                )

            return (
                "Não encontrei nada para salvar na memória."
            )

    # ========================================================
    # FORMAS NATURAIS DE SALVAR
    # ========================================================

    padroes_salvar = (
        r"^meu nome é (.+),?\s*(?:salve|salva|guarde|lembre)$",
        r"^meu nome é (.+)\s+salve$",
        r"^meu nome é (.+)\s+guarde$",
        r"^meu nome é (.+)\s+lembre$",
    )

    for padrao in padroes_salvar:

        match = re.match(
            padrao,
            normalizado
        )

        if match:

            nome = match.group(1).strip()

            conteudo = (
                f"o nome do usuário é {nome}"
            )

            if salvar(conteudo):

                return (
                    f"Entendido. Vou lembrar que seu nome é {nome}."
                )

            return (
                "Não consegui salvar essa informação."
            )

    # ========================================================
    # MOSTRAR MEMÓRIAS
    # ========================================================

    if normalizado in (
        "o que você lembra",
        "o que voce lembra",
        "mostrar memória",
        "mostrar memoria",
        "ver memória",
        "ver memoria",
        "minhas memórias",
        "minhas memorias",
        "listar memórias",
        "listar memorias",
    ):

        itens = listar()

        if not itens:

            return (
                "Ainda não tenho nenhuma memória salva."
            )

        linhas = [
            "Estas são as informações que você pediu "
            "para eu lembrar:"
        ]

        for memoria in itens:

            linhas.append(
                f"{memoria['id']}. "
                f"{memoria['conteudo']}"
            )

        return "\n".join(
            linhas
        )

    # ========================================================
    # LIMPAR MEMÓRIA
    # ========================================================

    if normalizado in (
        "limpar memória",
        "limpar memoria",
        "apagar memória",
        "apagar memoria",
        "esquecer tudo",
        "esqueça tudo",
        "esqueca tudo",
    ):

        limpar()

        return (
            "Memória apagada."
        )

    # ========================================================
    # EXCLUIR UMA MEMÓRIA
    # ========================================================

    match = re.match(
        r"^(?:esqueça|esqueca|apague|delete|remova|remover)"
        r"\s+(?:a\s+)?memória\s+(\d+)$",
        normalizado
    )

    if match:

        id_memoria = int(
            match.group(1)
        )

        if excluir(
            id_memoria
        ):

            return (
                f"Memória {id_memoria} apagada."
            )

        return (
            f"Não encontrei a memória {id_memoria}."
        )

    # ========================================================
    # NÃO É COMANDO DE MEMÓRIA
    # ========================================================

    return None