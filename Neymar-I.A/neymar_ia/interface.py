"""
Interface gráfica e bandeja do sistema do Neymar IA.
"""

import os
import sys
import queue
import threading
import tkinter as tk
from tkinter import messagebox

try:
    import customtkinter as ctk

except ImportError as erro:

    raise RuntimeError(
        "Instale customtkinter para usar a interface gráfica."
    ) from erro


try:
    import pystray
    from PIL import Image, ImageDraw

except ImportError as erro:

    raise RuntimeError(
        "Instale pystray e pillow para usar a bandeja do sistema."
    ) from erro


from . import inicializacao

from .sistema import bate

from .modos import (
    iniciar_assistente,
    processar_comando,
    ControleNucleo
)


class _GUIStream:
    """
    Redireciona stdout/stderr para a interface.
    """

    def __init__(
        self,
        fila,
        original=None
    ):
        self.fila = fila
        self.original = original

    def write(self, texto):

        if texto:
            self.fila.put(
                texto
            )

        return len(texto)

    def flush(self):

        if self.original:

            try:
                self.original.flush()

            except Exception:
                pass


class NeymarApp(ctk.CTk):
    """
    Janela principal do Neymar IA.
    """

    def __init__(self):

        super().__init__()

        # ----------------------------------------------------
        # FILA DE SAÍDA
        # ----------------------------------------------------

        self._saida_fila = queue.Queue()

        self._stdout_original = sys.stdout
        self._stderr_original = sys.stderr

        sys.stdout = _GUIStream(
            self._saida_fila,
            self._stdout_original
        )

        sys.stderr = _GUIStream(
            self._saida_fila,
            self._stderr_original
        )

        # ----------------------------------------------------
        # JANELA
        # ----------------------------------------------------

        self.title(
            "Neymar IA"
        )

        self.geometry(
            "900x600"
        )

        self.minsize(
            760,
            500
        )

        self.protocol(
            "WM_DELETE_WINDOW",
            self.minimizar
        )

        # ----------------------------------------------------
        # TEMA
        # ----------------------------------------------------

        ctk.set_appearance_mode(
            "dark"
        )

        ctk.set_default_color_theme(
            "dark-blue"
        )

        # ----------------------------------------------------
        # ESTADO
        # ----------------------------------------------------

        self.assistente_iniciado = False

        # Ponte com a máquina de estados (modo voz <-> modo texto)
        self.controle = ControleNucleo()

        self._stdout_original = sys.stdout
        self._stderr_original = sys.stderr

        self.tray = None

        # ----------------------------------------------------
        # INTERFACE
        # ----------------------------------------------------

        self._montar_interface()

        self._iniciar_tray()

        # ----------------------------------------------------
        # ATUALIZAÇÃO DO LOG
        # ----------------------------------------------------

        self.after(
            100,
            self._atualizar_saida
        )

        # ----------------------------------------------------
        # INICIA O NÚCLEO
        # ----------------------------------------------------

        self.after(
            300,
            self.iniciar_assistente
        )

    # ========================================================
    # INTERFACE
    # ========================================================

    def _montar_interface(self):

        self.grid_columnconfigure(
            1,
            weight=1
        )

        self.grid_rowconfigure(
            0,
            weight=1
        )

        # ----------------------------------------------------
        # LATERAL
        # ----------------------------------------------------

        lateral = ctk.CTkFrame(
            self,
            width=210,
            corner_radius=0
        )

        lateral.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        lateral.grid_propagate(
            False
        )

        ctk.CTkLabel(
            lateral,
            text="NEYMAR IA",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        ).pack(
            pady=(38, 5)
        )

        ctk.CTkLabel(
            lateral,
            text="Assistente pessoal",
            text_color="#9aa4b2"
        ).pack(
            pady=(0, 35)
        )

        self.status_label = ctk.CTkLabel(
            lateral,
            text='●  Aguardando "ligar Neymar"',
            text_color="#f5b942"
        )

        self.status_label.pack(
            pady=12
        )

        # ----------------------------------------------------
        # INICIALIZAÇÃO DO WINDOWS
        # ----------------------------------------------------

        self.startup_var = tk.BooleanVar(
            value=inicializacao.esta_ativado()
        )

        self.startup_switch = ctk.CTkSwitch(
            lateral,
            text="Iniciar com Windows",
            variable=self.startup_var,
            command=self.alternar_inicializacao
        )

        self.startup_switch.pack(
            padx=22,
            pady=18,
            anchor="w"
        )

        # ----------------------------------------------------
        # SAIR
        # ----------------------------------------------------

        ctk.CTkButton(
            lateral,
            text="Sair",
            fg_color="transparent",
            border_width=1,
            command=self.sair
        ).pack(
            side="bottom",
            padx=22,
            pady=25,
            fill="x"
        )

        # ----------------------------------------------------
        # CONTEÚDO
        # ----------------------------------------------------

        conteudo = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="#11151c"
        )

        conteudo.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        conteudo.grid_columnconfigure(
            0,
            weight=1
        )

        conteudo.grid_rowconfigure(
            2,
            weight=1
        )

        ctk.CTkLabel(
            conteudo,
            text="Olá, Ryan 👋",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            ),
            anchor="w"
        ).grid(
            row=0,
            column=0,
            padx=38,
            pady=(42, 4),
            sticky="ew"
        )

        ctk.CTkLabel(
            conteudo,
            text=(
                'Fale "ligar Neymar" para ativar. '
                'O microfone fica ouvindo em segundo plano.'
            ),
            text_color="#9aa4b2",
            anchor="w"
        ).grid(
            row=1,
            column=0,
            padx=40,
            pady=(0, 20),
            sticky="ew"
        )

        # ----------------------------------------------------
        # LOG
        # ----------------------------------------------------

        self.log = ctk.CTkTextbox(
            conteudo,
            corner_radius=14,
            fg_color="#171c24",
            border_width=1,
            border_color="#242c38"
        )

        self.log.grid(
            row=2,
            column=0,
            padx=38,
            pady=10,
            sticky="nsew"
        )

        self.log.configure(
            state="disabled"
        )

        self._log(
            "Neymar IA iniciado.\n"
        )

        # ----------------------------------------------------
        # CAMPO DE COMANDO
        # ----------------------------------------------------

        rodape = ctk.CTkFrame(
            conteudo,
            fg_color="transparent"
        )

        rodape.grid(
            row=3,
            column=0,
            padx=38,
            pady=(12, 30),
            sticky="ew"
        )

        rodape.grid_columnconfigure(
            0,
            weight=1
        )

        self.entrada = ctk.CTkEntry(
            rodape,
            height=42,
            placeholder_text="Digite um comando..."
        )

        self.entrada.grid(
            row=0,
            column=0,
            padx=(0, 10),
            sticky="ew"
        )

        self.entrada.bind(
            "<Return>",
            self.enviar_texto
        )

        ctk.CTkButton(
            rodape,
            text="Enviar",
            width=100,
            height=42,
            command=self.enviar_texto
        ).grid(
            row=0,
            column=1
        )

    # ========================================================
    # LOG
    # ========================================================

    def _atualizar_saida(self):

        partes = []

        while True:

            try:

                partes.append(
                    self._saida_fila.get_nowait()
                )

            except queue.Empty:

                break

        if partes:

            texto = "".join(
                partes
            )

            self._log(
                texto
            )

        if self.winfo_exists():

            self.after(
                100,
                self._atualizar_saida
            )

    def _log(self, texto):

        self.log.configure(
            state="normal"
        )

        self.log.insert(
            "end",
            texto
        )

        self.log.see(
            "end"
        )

        self.log.configure(
            state="disabled"
        )

    # ========================================================
    # INICIAR ASSISTENTE
    # ========================================================

    def iniciar_assistente(self):

        if self.assistente_iniciado:
            return

        self.assistente_iniciado = True

        self.status_label.configure(
            text='●  Aguardando "ligar Neymar"',
            text_color="#f5b942"
        )

        self._log(
            "\n✓ Núcleo do assistente em execução.\n"
        )

        threading.Thread(
            target=self._rodar_nucleo,
            daemon=True,
            name="NeymarIA-Core"
        ).start()

    def _rodar_nucleo(self):

        try:

            iniciar_assistente(
                status_callback=self._status_do_nucleo,
                controle=self.controle
            )

        except Exception as erro:

            # Importante: usar "erro=erro" como valor padrão do
            # parâmetro da lambda. O Python apaga a variável 'erro'
            # assim que o bloco except termina, e o self.after(0, ...)
            # só executa a lambda depois disso — sem o valor padrão,
            # ela tentaria ler uma variável que não existe mais e
            # estourava NameError ("cannot access free variable").
            self.after(
                0,
                lambda erro=erro: self._erro_nucleo(erro)
            )

    # ========================================================
    # STATUS DO NÚCLEO
    # ========================================================

    def _status_do_nucleo(
        self,
        estado
    ):

        textos = {

            "aguardando": (
                '●  Aguardando "ligar Neymar"',
                "#f5b942",
                ""
            ),

            "ativo": (
                "●  Neymar ligado",
                "#4ade80",
                "\n🟢 Neymar ligado. Pode falar normalmente.\n"
            ),

            "ouvindo": (
                "●  Ouvindo...",
                "#60a5fa",
                "\n🎙️ Ouvindo...\n"
            ),

            "processando": (
                "●  Processando...",
                "#a78bfa",
                "🔎 Processando comando...\n"
            ),

            "desligado": (
                "●  Neymar desligado",
                "#f87171",
                "\n🔴 Neymar desligado.\n"
            ),

            "modo_texto": (
                '●  Modo texto — digite abaixo',
                "#4ade80",
                "\n⌨️  Modo texto ativado. Digite na caixa abaixo.\n"
            ),
        }

        dados = textos.get(
            estado
        )

        if not dados:
            return

        texto, cor, log = dados

        self.after(
            0,
            lambda: self.status_label.configure(
                text=texto,
                text_color=cor
            )
        )

        if log:

            self.after(
                0,
                lambda: self._log(log)
            )

    # ========================================================
    # ERRO
    # ========================================================

    def _erro_nucleo(
        self,
        erro
    ):

        self.status_label.configure(
            text="●  Erro no assistente",
            text_color="#ef4444"
        )

        self._log(
            "\n✕ Erro no núcleo:\n"
        )

        self._log(
            f"{type(erro).__name__}: {erro}\n"
        )

    # ========================================================
    # COMANDO DIGITADO
    # ========================================================

    def enviar_texto(
        self,
        _evento=None
    ):

        texto = self.entrada.get().strip()

        if not texto:
            return

        self.entrada.delete(
            0,
            "end"
        )

        self._log(
            f"\nVocê: {texto}\n"
        )

        threading.Thread(
            target=self._processar_texto,
            args=(texto,),
            daemon=True,
            name="NeymarIA-Command"
        ).start()

    def _processar_texto(
        self,
        texto
    ):

        try:

            comando = texto.lower().strip()

            # ------------------------------------------------
            # Comandos de controle (mesmos gatilhos de
            # modo_texto()/modo_voz(), só que digitados aqui em
            # vez de ditos por voz).
            # ------------------------------------------------

            if bate(
                comando,
                "desligar neymar",
                "desliga neymar"
            ):

                self.controle.pedir_desligar()

                self.after(
                    0,
                    lambda: self._log(
                        "Neymar: Desligando os sistemas. Até logo, "
                        "senhor.\n"
                    )
                )

                return

            if bate(
                comando,
                "mudar para voz",
                "modo voz",
                "trocar para voz"
            ):

                self.controle.pedir_modo_voz()

                self.after(
                    0,
                    lambda: self._log(
                        "Neymar: Mudando para o modo voz.\n"
                    )
                )

                return

            if bate(
                comando,
                "mudar para texto",
                "modo texto",
                "trocar para texto"
            ):

                self.controle.pedir_modo_texto()

                self.after(
                    0,
                    lambda: self._log(
                        "Neymar: Já estamos no modo texto.\n"
                    )
                )

                return

            resposta = processar_comando(
                texto,
                usar_voz=False
            )

            if resposta:

                self.after(
                    0,
                    lambda: self._log(
                        f"Neymar: {resposta}\n"
                    )
                )

        except Exception as erro:

            # Mesmo motivo do outro except: precisa capturar 'erro'
            # como valor padrão, senão dá o mesmo NameError quando
            # a lambda roda depois do bloco except já ter terminado.
            self.after(
                0,
                lambda erro=erro: self._log(
                    f"Erro: {erro}\n"
                )
            )

    # ========================================================
    # INICIALIZAÇÃO COM WINDOWS
    # ========================================================

    def alternar_inicializacao(self):

        ativo = bool(
            self.startup_var.get()
        )

        sucesso = (
            inicializacao.ativar()
            if ativo
            else inicializacao.desativar()
        )

        if not sucesso and os.name == "nt":

            self.startup_var.set(
                inicializacao.esta_ativado()
            )

            messagebox.showwarning(
                "Inicialização",
                (
                    "Não foi possível alterar "
                    "a inicialização automática."
                )
            )

    # ========================================================
    # BANDEJA
    # ========================================================

    def minimizar(self):

        self.withdraw()

    def mostrar(self):

        self.deiconify()

        self.lift()

        self.focus_force()

    def _criar_icone(self):

        imagem = Image.new(
            "RGBA",
            (64, 64),
            (17, 21, 28, 255)
        )

        desenho = ImageDraw.Draw(
            imagem
        )

        desenho.ellipse(
            (8, 8, 56, 56),
            fill=(76, 99, 255, 255)
        )

        desenho.text(
            (24, 17),
            "N",
            fill="white"
        )

        return imagem

    def _iniciar_tray(self):

        def rodar():

            menu = pystray.Menu(

                pystray.MenuItem(
                    "Abrir Neymar IA",
                    lambda: self.after(
                        0,
                        self.mostrar
                    )
                ),

                pystray.MenuItem(
                    "Ocultar",
                    lambda: self.after(
                        0,
                        self.minimizar
                    )
                ),

                pystray.MenuItem(
                    "Sair",
                    lambda: self.after(
                        0,
                        self.sair
                    )
                ),
            )

            self.tray = pystray.Icon(
                "NeymarIA",
                self._criar_icone(),
                "Neymar IA",
                menu
            )

            self.tray.run()

        threading.Thread(
            target=rodar,
            daemon=True,
            name="NeymarIA-Tray"
        ).start()

    # ========================================================
    # SAIR
    # ========================================================

    def sair(self):

        try:

            if self.tray:
                self.tray.stop()

        except Exception:
            pass

        sys.stdout = self._stdout_original
        sys.stderr = self._stderr_original

        self.destroy()


# ============================================================
# FUNÇÃO PÚBLICA
# ============================================================

def iniciar_interface():

    app = NeymarApp()

    app.mainloop()