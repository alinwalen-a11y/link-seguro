import os
from urllib.parse import urlparse
from flask import Flask, render_template, request

app = Flask(__name__)

def analizar(url_original):
    url = url_original.strip()
    # Si el usuario no puso http/https, asumimos https (no lo castigamos)
    if not url.startswith("http"):
        url = "https://" + url

    parsed = urlparse(url)
    dominio = parsed.netloc.lower().replace("www.", "")
    puntaje = 0
    motivos = []

    # Solo castigamos si ESCRIBIÓ http:// a propósito
    if parsed.scheme == "http":
        puntaje += 25
        motivos.append("Usa http y no https, tus datos viajarían sin cifrar")

    palabras = ["gratis", "premio", "gano", "banco", "verificar", "urgente", "sorteo", "oferta", "login", "cuenta"]
    for p in palabras:
        if p in url.lower():
            puntaje += 15
            motivos.append(f"Contiene la palabra sospechosa: '{p}'")
            break

    if dominio.count("-") >= 2 or any(c.isdigit() for c in dominio):
        puntaje += 20
        motivos.append("El dominio tiene números o muchos guiones, típico de copias falsas")

    if len(dominio) > 25:
        puntaje += 15
        motivos.append("Dominio demasiado largo, los sitios reales son cortos")

    if dominio.endswith((".xyz", ".top", ".click", ".online", ".tk")):
        puntaje += 25
        motivos.append("Usa una extensión barata muy usada para estafas")

    if puntaje == 0:
        motivos.append("No encontramos señales de estafa. Se ve limpio.")

    puntaje = min(puntaje, 100)
    if puntaje >= 60:
        nivel, color = "PELIGROSO", "red"
    elif puntaje >= 30:
        nivel, color = "SOSPECHOSO", "yellow"
    else:
        nivel, color = "SEGURO", "green"

    return {"puntaje": puntaje, "nivel": nivel, "color": color, "dominio": dominio, "motivos": motivos}

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    if request.method == "POST":
        resultado = analizar(request.form.get("url", ""))
    return render_template("index.html", resultado=resultado)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)