"""Interface principal do Neymar IA.

Visual inspirado na interface aprovada: sem painel lateral, sem log técnico,
com orbe central animado e conversa limpa.
"""

import os
import sys
import threading
import tkinter as tk
import ctypes
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk
import pystray
from PIL import Image, ImageDraw, ImageTk

from . import inicializacao, config
from .sistema import bate
from .modos import iniciar_assistente, processar_comando, ControleNucleo


def _asset_path(nome):
    return config.caminho_asset(nome)


class NeymarApp(ctk.CTk):
    def __init__(self, iniciar_minimizado=False):
        super().__init__()

        self.title("Neymar IA")
        self.geometry("1000x680")
        self.minsize(820, 560)
        self.configure(fg_color="#020807")

        self._logo_png = str(_asset_path("neymar_ia.png"))
        self._logo_ico = str(_asset_path("neymar_ia.ico"))
        self._window_icon = None
        # Windows: give the process its own AppUserModelID so the shell
        # uses Neymar IA instead of the Python/PyCharm generic icon.
        if os.name == "nt":
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                    "NeymarIA.NeymarIA"
                )
            except Exception:
                pass
        try:
            self.iconbitmap(self._logo_ico)
        except Exception as erro:
            print(f"[!] Falha ao carregar iconbitmap ({self._logo_ico}): {erro!r}")
        try:
            icon_image = Image.open(self._logo_png).convert("RGBA")
            icon_image.thumbnail((64, 64), Image.Resampling.LANCZOS)
            self._window_icon = ImageTk.PhotoImage(icon_image)
            self.iconphoto(True, self._window_icon)
        except Exception as erro:
            self._window_icon = None
            print(f"[!] Falha ao carregar iconphoto ({self._logo_png}): {erro!r}")

        ctk.set_appearance_mode("dark")
        self.protocol("WM_DELETE_WINDOW", self.minimizar)

        self.controle = ControleNucleo()
        self.assistente_iniciado = False
        self.tray = None
        self._estado = "aguardando"
        self._orbe_fase = 0.0
        self._montar_interface()
        self._iniciar_tray()
        self.after(50, self._animar_orbe)
        self.after(300, self.iniciar_assistente)

        if iniciar_minimizado:
            self.after(350, self.minimizar)

    def _montar_interface(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Cabeçalho
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(8, 0))
        header.grid_columnconfigure(1, weight=1)

        try:
            self._header_logo = ctk.CTkImage(
                light_image=Image.open(self._logo_png),
                dark_image=Image.open(self._logo_png),
                size=(52, 52),
            )
            ctk.CTkLabel(
                header, text="", image=self._header_logo
            ).grid(row=0, column=0, rowspan=2, padx=(0, 12))
        except Exception as erro:
            print(f"[!] Falha ao montar logo do cabeçalho ({self._logo_png}): {erro!r}")

        ctk.CTkLabel(
            header, text="NEYMAR IA", anchor="w",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#f2f2f2"
        ).grid(row=0, column=1, sticky="w", pady=(4, 0))

        ctk.CTkLabel(
            header, text="ASSISTENTE INTELIGENTE", anchor="w",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#00c853"
        ).grid(row=1, column=1, sticky="w")

        # Saudação
        intro = ctk.CTkFrame(self, fg_color="transparent")
        intro.grid(row=1, column=0, sticky="ew", padx=24, pady=(8, 0))
        intro.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            intro, text="Olá, Ryan", anchor="w",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#f5f5f5"
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            intro, text="Fale comigo ou escreva uma mensagem abaixo.", anchor="w",
            font=ctk.CTkFont(size=12), text_color="#d7dedb"
        ).grid(row=0, column=2, sticky="w")

        # Área central
        center = ctk.CTkFrame(self, fg_color="#00100b", corner_radius=0)
        center.grid(row=2, column=0, sticky="nsew", padx=24, pady=(8, 0))
        center.grid_columnconfigure(0, weight=1)
        center.grid_rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(center, bg="#00100b", highlightthickness=0, bd=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", lambda _e: self._desenhar_orbe())

        # Conversa
        self.chat = ctk.CTkScrollableFrame(
            self, fg_color="#00100b", corner_radius=14,
            border_width=1, border_color="#064a31"
        )
        self.chat.grid(row=3, column=0, sticky="ew", padx=24, pady=(12, 0))
        self.chat.grid_columnconfigure(0, weight=1)
        self._sistema_box = None
        self._sistema_label = None
        self._adicionar_sistema('Aguardando "Ligar Neymar".')

        # Entrada
        footer = ctk.CTkFrame(self, fg_color="#061b13", corner_radius=18,
                              border_width=1, border_color="#075a3a")
        footer.grid(row=4, column=0, sticky="ew", padx=24, pady=(12, 0))
        footer.grid_columnconfigure(0, weight=1)

        self.entrada = ctk.CTkEntry(
            footer, height=52, border_width=0, fg_color="transparent",
            placeholder_text="Digite sua mensagem...",
            placeholder_text_color="#568273",
            font=ctk.CTkFont(size=13)
        )
        self.entrada.grid(row=0, column=0, sticky="ew", padx=(18, 4), pady=3)
        self.entrada.bind("<Return>", self.enviar_texto)

        self.enviar_btn = ctk.CTkButton(
            footer, text="Enviar  ➜", width=104, height=42,
            corner_radius=13, fg_color="#00a844", hover_color="#00c853",
            command=self.enviar_texto
        )
        self.enviar_btn.grid(row=0, column=1, padx=8, pady=5)

        self.modo_label = ctk.CTkLabel(
            self, text="Modo de voz ativo.",
            anchor="w", font=ctk.CTkFont(size=9), text_color="#51796b"
        )
        self.modo_label.grid(row=5, column=0, sticky="w", padx=24, pady=(8, 18))
        self._atualizar_controles_modo("voz")

    # ---------- orbe ----------
    def _cores_orbe(self):
        return {
            "aguardando": ("#ffe600", "#6b5700"),
            "ativo": ("#00d85a", "#064f28"),
            "ouvindo": ("#00d85a", "#064f28"),
            "processando": ("#00d85a", "#064f28"),
            "modo_texto": ("#168cff", "#063e70"),
            "desligado": ("#ff3b3b", "#570d0d"),
        }.get(self._estado, ("#00a844", "#064f28"))

    def _desenhar_orbe(self):
        if not hasattr(self, "canvas"):
            return
        self.canvas.delete("all")
        w = max(self.canvas.winfo_width(), 1)
        h = max(self.canvas.winfo_height(), 1)
        cx, cy = w * 0.78, h * 0.5
        main, dark = self._cores_orbe()
        pulse = (1 + __import__('math').sin(self._orbe_fase)) / 2
        r = 56 + pulse * 9

        # halos discretos
        for i, mul in enumerate((2.9, 2.35, 1.85, 1.45)):
            rr = r * mul
            fill = dark if i < 2 else "#08351f"
            self.canvas.create_oval(cx-rr, cy-rr, cx+rr, cy+rr, fill=fill, outline="")
        for rr in (r*1.35, r*1.18, r*1.04):
            self.canvas.create_oval(cx-rr, cy-rr, cx+rr, cy+rr, outline=main, width=1)
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=main, outline="")
        self.canvas.create_oval(cx-r*0.55, cy-r*0.65, cx+r*0.05, cy-r*0.05,
                                fill="#f4fff9", outline="")
        self.canvas.create_oval(cx-r*0.18, cy-r*0.02, cx+r*0.34, cy+r*0.40,
                                fill="#ffffff", outline="")
        self.canvas.create_oval(cx-r*0.02, cy+r*0.18, cx+r*0.34, cy+r*0.48,
                                fill=main, outline="")

    def _animar_orbe(self):
        self._orbe_fase += 0.10
        self._desenhar_orbe()
        if self.winfo_exists():
            self.after(50, self._animar_orbe)

    # ---------- conversa ----------
    def _limpar_chat(self):
        for child in self.chat.winfo_children():
            child.destroy()

    def _adicionar_bolha(self, quem, texto, cor):
        box = ctk.CTkFrame(self.chat, fg_color=cor, corner_radius=14)
        box.grid(sticky="ew", padx=18, pady=6)
        ctk.CTkLabel(
            box, text=f"{quem}:  {texto}", anchor="w", justify="left",
            wraplength=900, font=ctk.CTkFont(size=12), text_color="#f4f7f5"
        ).pack(fill="x", padx=14, pady=11)
        self.after(20, lambda: self.chat._parent_canvas.yview_moveto(1.0))

    def _adicionar_sistema(self, texto):
        if self._sistema_box is None or not self._sistema_box.winfo_exists():
            self._sistema_box = ctk.CTkFrame(
                self.chat, fg_color="#3a3000", corner_radius=14,
                border_width=1, border_color="#ffe600"
            )
            self._sistema_box.grid(sticky="ew", padx=18, pady=10)
            self._sistema_label = ctk.CTkLabel(
                self._sistema_box, text="", anchor="w",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#fff08a"
            )
            self._sistema_label.pack(fill="x", padx=14, pady=12)
        self._sistema_label.configure(text=f"Sistema:  {texto}")

    # ---------- núcleo ----------
    def iniciar_assistente(self):
        if self.assistente_iniciado:
            return
        self.assistente_iniciado = True
        threading.Thread(target=self._rodar_nucleo, daemon=True, name="NeymarIA-Core").start()

    def _rodar_nucleo(self):
        try:
            iniciar_assistente(status_callback=self._status_do_nucleo,
                                controle=self.controle,
                                message_callback=self._mensagem_do_nucleo)
        except TypeError:
            # compatibilidade com versões antigas do modos.py
            iniciar_assistente(status_callback=self._status_do_nucleo, controle=self.controle)
        except Exception as erro:
            self.after(0, lambda erro=erro: self._erro_nucleo(erro))

    def _status_do_nucleo(self, estado):
        self._estado = estado
        if estado == "aguardando":
            texto = 'Aguardando "Ligar Neymar".'
        elif estado == "ativo":
            texto = "Neymar está ligado."
        elif estado == "ouvindo":
            texto = "Estou ouvindo..."
        elif estado == "processando":
            texto = ""
        elif estado == "modo_texto":
            texto = "Modo texto ativo."
        elif estado == "desligado":
            texto = "Neymar está desligado."
        else:
            return
        if estado == "modo_texto":
            self.after(0, lambda: self._atualizar_controles_modo("texto"))
        elif estado == "ativo":
            self.after(0, lambda: self._atualizar_controles_modo("voz"))
        elif estado == "aguardando":
            self.after(0, lambda: self._atualizar_controles_modo("voz"))
        elif estado == "desligado":
            self.after(0, lambda: self._atualizar_controles_modo("voz"))
        if estado not in ("processando", "ouvindo"):
            self.after(0, lambda t=texto: self._atualizar_sistema(t))

    def _mensagem_do_nucleo(self, quem, texto):
        if not texto:
            return
        self.after(0, lambda q=quem, t=texto: self._adicionar_bolha(
            "Você" if q == "usuario" else "Neymar", t,
            "#06345b" if q == "usuario" else "#064b2c"
        ))

    def _atualizar_sistema(self, texto):
        self._adicionar_sistema(texto)

    def _erro_nucleo(self, erro):
        self._estado = "desligado"
        self._atualizar_sistema(f"Não foi possível iniciar o assistente: {erro}")

    def _atualizar_controles_modo(self, modo):
        modo = "texto" if modo == "texto" else "voz"
        if modo == "voz":
            self.entrada.configure(state="disabled", placeholder_text="Modo de voz ativo.")
            self.enviar_btn.configure(state="disabled")
            self.modo_label.configure(text="Modo de voz ativo.")
        else:
            self.entrada.configure(state="normal", placeholder_text="Digite sua mensagem...")
            self.enviar_btn.configure(state="normal")
            self.modo_label.configure(text="Modo de texto ativo.")

    def enviar_texto(self, _evento=None):
        if self._estado != "modo_texto":
            return
        texto = self.entrada.get().strip()
        if not texto:
            return
        self.entrada.delete(0, "end")
        self._adicionar_bolha("Você", texto, "#06345b")
        threading.Thread(target=self._processar_texto, args=(texto,), daemon=True,
                           name="NeymarIA-Command").start()

    def _processar_texto(self, texto):
        try:
            comando = texto.lower().strip()
            if bate(comando, "desligar neymar", "desliga neymar"):
                self.controle.pedir_desligar()
                self.after(0, lambda: self._mensagem_do_nucleo("assistente", "Valeu jogador, até mais"))
                return
            if bate(comando, "mudar para voz", "modo voz", "trocar para voz"):
                self.controle.pedir_modo_voz()
                self.after(0, lambda: self._status_do_nucleo("ativo"))
                return
            if bate(comando, "mudar para texto", "modo texto", "trocar para texto"):
                self.controle.pedir_modo_texto()
                self.after(0, lambda: self._status_do_nucleo("modo_texto"))
                return
            resposta = processar_comando(texto, usar_voz=False,
                                          message_callback=self._mensagem_do_nucleo)
            if resposta:
                # evitar respostas artificiais de controle do backend
                if resposta not in ("Comando processado.", "Comando executado."):
                    self._mensagem_do_nucleo("assistente", resposta)
        except Exception:
            self.after(0, lambda: self._atualizar_sistema("Não consegui processar essa mensagem."))

    # ---------- inicialização ----------
    def alternar_inicializacao(self):
        """Alterna a inicialização automática com o Windows (chamado pela bandeja)."""
        ativo = not inicializacao.esta_ativado()
        sucesso = inicializacao.ativar() if ativo else inicializacao.desativar()
        if not sucesso and os.name == "nt":
            messagebox.showwarning("Inicialização", "Não foi possível alterar a inicialização automática.")

    # ---------- bandeja ----------
    def minimizar(self):
        self.withdraw()

    def mostrar(self):
        self.deiconify(); self.lift(); self.focus_force()

    def _criar_icone(self):
        try:
            return Image.open(self._logo_png).convert("RGBA").resize((64, 64), Image.Resampling.LANCZOS)
        except Exception as erro:
            print(f"[!] Falha ao carregar ícone da bandeja ({self._logo_png}): {erro!r}")
            img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            ImageDraw.Draw(img).ellipse((4, 4, 60, 60), fill="#00a844")
            ImageDraw.Draw(img).text((25, 17), "N", fill="white")
            return img

    def _iniciar_tray(self):
        def rodar():
            menu = pystray.Menu(
                pystray.MenuItem("Abrir Neymar IA", lambda: self.after(0, self.mostrar)),
                pystray.MenuItem("Ocultar", lambda: self.after(0, self.minimizar)),
                pystray.MenuItem(
                    "Iniciar com o Windows",
                    lambda: self.after(0, self.alternar_inicializacao),
                    checked=lambda _item: inicializacao.esta_ativado(),
                ),
                pystray.MenuItem("Sair", lambda: self.after(0, self.sair)),
            )
            self.tray = pystray.Icon("NeymarIA", self._criar_icone(), "Neymar IA", menu)
            self.tray.run()
        threading.Thread(target=rodar, daemon=True, name="NeymarIA-Tray").start()

    def sair(self):
        try:
            if self.tray:
                self.tray.stop()
        except Exception:
            pass
        self.destroy()


def iniciar_interface(iniciar_minimizado=False):
    app = NeymarApp(iniciar_minimizado=iniciar_minimizado)
    app.mainloop()
