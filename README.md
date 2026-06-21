# Combinador de Etiquetas - Mercado Libre

Herramienta de escritorio para combinar etiquetas PDF de Mercado Libre en hojas A4, con **3 etiquetas por página**, listas para imprimir.

---

## Español

### Requisitos

- Python 3.8 o superior
- Las dependencias listadas en `requirements.txt`

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/Fox-TBG/combinador-etiquetas-meli.git
cd combinador-etiquetas-meli

# 2. (Opcional) Crear un entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Instalar dependencias
pip install -r requirements.txt
```

### Uso

```bash
python combinar_etiquetas_gui.py
```

1. Hacé clic en **"+ Agregar etiquetas"** y seleccioná los PDF de etiquetas de Mercado Libre.
2. Revisá el orden en la lista (podés quitar alguna con **"Quitar seleccionada"**).
3. Hacé clic en **"Generar hoja A4"**, elegí dónde guardar el archivo y listo.

El programa genera un PDF con las etiquetas organizadas de a 3 por hoja A4 apaisada (horizontal), optimizadas para imprimir y recortar.

### Notas

- Solo se usa la primera página de cada PDF (que es la etiqueta).
- Si la última hoja no está completa, las etiquetas se alinean a la derecha para facilitar el corte.
- Compatible con Windows, macOS y Linux.

---

## English

### Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Fox-TBG/combinador-etiquetas-meli.git
cd combinador-etiquetas-meli

# 2. (Optional) Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
```

### Usage

```bash
python combinar_etiquetas_gui.py
```

1. Click **"+ Agregar etiquetas"** and select your Mercado Libre label PDF files.
2. Review the order in the list (you can remove any entry with **"Quitar seleccionada"**).
3. Click **"Generar hoja A4"**, choose where to save the file, and you're done.

The app generates a PDF with labels arranged 3 per landscape A4 page, ready to print and cut.

### Notes

- Only the first page of each PDF is used (which is the label itself).
- If the last page is not full, labels are right-aligned to make cutting easier.
- Compatible with Windows, macOS, and Linux.

---

## Licencia / License

MIT © [Fox-TBG](https://github.com/Fox-TBG)
