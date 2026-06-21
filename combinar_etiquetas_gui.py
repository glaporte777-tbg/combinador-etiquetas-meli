#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Combinar Etiquetas Mercado Libre - App con ventana (GUI)

Para el usuario final: abrir el programa, agregar los PDF de etiquetas que
manda Mercado Libre y apretar "Generar hoja A4". Entran 3 etiquetas por hoja.

Sin conocimientos tecnicos: no hay que tocar codigo ni linea de comandos.
"""
import os
import sys
import traceback

import pdfplumber
from pypdf import PdfReader, PdfWriter, Transformation, PageObject

# ----------------------------- MOTOR -----------------------------
# A4 APAISADA en puntos PDF (1 pt = 1/72")
A4L_W, A4L_H = 841.890, 595.276
COLS = 3        # etiquetas por hoja
MARGIN = 14     # margen exterior (pts)
GAP = 12        # separacion entre etiquetas (pts)
PAD = 5         # padding alrededor del recorte (pts)


def bbox_contenido(ruta):
    """Rect (left, bottom, right, top) en coords PDF que encierra el contenido
    real de la pagina 1 (para recortar el blanco sobrante)."""
    with pdfplumber.open(ruta) as pdf:
        p = pdf.pages[0]
        H = p.height
        objs = []
        for kind in ("chars", "lines", "rects", "curves", "images"):
            objs += getattr(p, kind)
        if not objs:
            return (0.0, 0.0, float(p.width), float(p.height))
        x0 = min(o["x0"] for o in objs)
        x1 = max(o["x1"] for o in objs)
        top = min(o["top"] for o in objs)
        bot = max(o["bottom"] for o in objs)
        left = max(0.0, x0 - PAD)
        right = min(float(p.width), x1 + PAD)
        y_bottom = max(0.0, H - (bot + PAD))
        y_top = min(H, H - (top - PAD))
        return (left, y_bottom, right, y_top)


def procesar(entradas, salida, log=lambda *_: None):
    """Combina los PDF de 'entradas' en 'salida'. Devuelve cantidad de hojas."""
    if not entradas:
        raise ValueError("No seleccionaste ninguna etiqueta.")

    n = len(entradas)
    total_paginas = (n + COLS - 1) // COLS
    etiquetas_ultima = n - (total_paginas - 1) * COLS

    cell_w = (A4L_W - 2 * MARGIN - (COLS - 1) * GAP) / COLS
    cell_h = A4L_H - 2 * MARGIN
    writer = PdfWriter()

    for i, ruta in enumerate(entradas):
        col = i % COLS
        page_idx = i // COLS
        if col == 0:
            writer.add_page(PageObject.create_blank_page(width=A4L_W, height=A4L_H))
        dest = writer.pages[-1]

        left, bottom, right, top = bbox_contenido(ruta)
        cw, ch = right - left, top - bottom

        src = PdfReader(ruta).pages[0]   # solo pagina 1 = la etiqueta
        scale = min(cell_w / cw, cell_h / ch)
        nw, nh = cw * scale, ch * scale

        # En la ultima pagina, alinear hacia la derecha si no esta completa
        if page_idx == total_paginas - 1 and etiquetas_ultima < COLS:
            col_real = col + (COLS - etiquetas_ultima)
        else:
            col_real = col

        cell_x = MARGIN + col_real * (cell_w + GAP)
        cell_y = MARGIN
        tx = cell_x + (cell_w - nw) / 2
        ty = cell_y + (cell_h - nh) / 2

        op = (Transformation()
              .translate(-left, -bottom)
              .scale(scale)
              .translate(tx, ty))
        dest.merge_transformed_page(src, op)
        log(f"Agregada: {os.path.basename(ruta)}")

    with open(salida, "wb") as f:
        writer.write(f)
    return len(writer.pages)


# ----------------------------- INTERFAZ (GUI) -----------------------------
def lanzar_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox

    BG = "#0f1115"
    CARD = "#1a1d24"
    FG = "#e8eaed"
    SUB = "#9aa0a6"
    ACCENT = "#ffe600"   # amarillo ML
    ACCENT_FG = "#1a1d24"

    root = tk.Tk()
    root.title("Combinar Etiquetas - Mercado Libre")
    root.configure(bg=BG)
    root.geometry("560x560")
    root.minsize(520, 520)

    archivos = []  # rutas seleccionadas, en orden

    # --- Encabezado ---
    tk.Label(root, text="Combinar Etiquetas", bg=BG, fg=FG,
             font=("Segoe UI", 18, "bold")).pack(pady=(18, 0))
    tk.Label(root, text="Junta tus etiquetas de Mercado Libre: 3 por hoja A4.",
             bg=BG, fg=SUB, font=("Segoe UI", 10)).pack(pady=(2, 12))

    # --- Lista de archivos ---
    cont = tk.Frame(root, bg=CARD, bd=0, highlightthickness=1,
                    highlightbackground="#2a2e37")
    cont.pack(fill="both", expand=True, padx=18, pady=(0, 8))

    tk.Label(cont, text="Etiquetas seleccionadas (en orden):", bg=CARD, fg=SUB,
             font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(10, 4))

    list_frame = tk.Frame(cont, bg=CARD)
    list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
    scroll = tk.Scrollbar(list_frame)
    scroll.pack(side="right", fill="y")
    lista = tk.Listbox(list_frame, bg="#11141a", fg=FG, bd=0,
                       highlightthickness=0, selectbackground=ACCENT,
                       selectforeground=ACCENT_FG, activestyle="none",
                       font=("Segoe UI", 10), yscrollcommand=scroll.set)
    lista.pack(side="left", fill="both", expand=True)
    scroll.config(command=lista.yview)

    def refrescar():
        lista.delete(0, tk.END)
        for i, r in enumerate(archivos, 1):
            lista.insert(tk.END, f"  {i}.  {os.path.basename(r)}")
        n = len(archivos)
        hojas = (n + COLS - 1) // COLS if n else 0
        estado.config(text=(f"{n} etiqueta(s)  -->  {hojas} hoja(s) A4"
                             if n else "Todavia no agregaste etiquetas."))

    def agregar():
        rutas = filedialog.askopenfilenames(
            title="Elegi los PDF de las etiquetas",
            filetypes=[("Archivos PDF", "*.pdf")])
        for r in rutas:
            if r not in archivos:
                archivos.append(r)
        refrescar()

    def quitar():
        sel = list(lista.curselection())
        for idx in reversed(sel):
            del archivos[idx]
        refrescar()

    def limpiar():
        archivos.clear()
        refrescar()

    def generar():
        if not archivos:
            messagebox.showwarning("Faltan etiquetas",
                                   "Primero agrega al menos una etiqueta PDF.")
            return
        carpeta = os.path.dirname(archivos[0]) or os.path.expanduser("~")
        salida = filedialog.asksaveasfilename(
            title="Guardar hoja combinada como...",
            defaultextension=".pdf",
            initialdir=carpeta,
            initialfile="etiquetas_combinadas.pdf",
            filetypes=[("Archivo PDF", "*.pdf")])
        if not salida:
            return
        try:
            estado.config(text="Procesando...")
            root.update_idletasks()
            hojas = procesar(archivos, salida)
            estado.config(text=f"Listo: {len(archivos)} etiqueta(s) en {hojas} hoja(s).")
            if messagebox.askyesno(
                    "Listo",
                    f"Se genero el PDF con {len(archivos)} etiqueta(s) "
                    f"en {hojas} hoja(s) A4.\n\n{salida}\n\n¿Abrirlo ahora?"):
                _abrir(salida)
        except Exception as e:
            messagebox.showerror(
                "Hubo un problema",
                f"No se pudo generar el PDF.\n\nDetalle:\n{e}\n\n"
                "Verifica que sean PDF de etiquetas de Mercado Libre.")
            traceback.print_exc()

    def _abrir(ruta):
        try:
            if sys.platform.startswith("win"):
                os.startfile(ruta)               # noqa
            elif sys.platform == "darwin":
                os.system(f'open "{ruta}"')
            else:
                os.system(f'xdg-open "{ruta}"')
        except Exception:
            pass

    # --- Botones secundarios ---
    barra = tk.Frame(root, bg=BG)
    barra.pack(fill="x", padx=18)

    def boton(parent, txt, cmd, primary=False):
        b = tk.Button(parent, text=txt, command=cmd, relief="flat",
                      cursor="hand2", font=("Segoe UI", 10, "bold"),
                      bg=(ACCENT if primary else "#2a2e37"),
                      fg=(ACCENT_FG if primary else FG),
                      activebackground=(ACCENT if primary else "#343943"),
                      activeforeground=ACCENT_FG if primary else FG,
                      bd=0, padx=14, pady=8)
        return b

    boton(barra, "+ Agregar etiquetas", agregar).pack(side="left")
    boton(barra, "Quitar seleccionada", quitar).pack(side="left", padx=6)
    boton(barra, "Limpiar", limpiar).pack(side="left")

    estado = tk.Label(root, text="Todavia no agregaste etiquetas.",
                      bg=BG, fg=SUB, font=("Segoe UI", 9))
    estado.pack(pady=(12, 6))

    boton(root, "Generar hoja A4", generar, primary=True).pack(pady=(0, 18),
                                                               ipadx=20)

    refrescar()
    root.mainloop()


if __name__ == "__main__":
    lanzar_gui()
