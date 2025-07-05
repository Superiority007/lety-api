from flask import Flask, request, jsonify
import pandas as pd
import re
import requests

app = Flask(__name__)

# URL del Google Sheet en formato CSV
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1JaLgqMJ8U1NEHPUnLs4RYKkO9oAVhhkqHNYPcxLi-KQ/export?format=csv"

def cargar_datos():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        return df
    except Exception as e:
        return None

@app.route("/reporte", methods=["POST"])
def responder():
    mensaje = request.json.get("mensaje", "").lower()

    usuario_match = re.search(r"usuario\s+es\s+([a-zA-Z0-9_.-]+)", mensaje)
    pin_match = re.search(r"pin\s+es\s+(\d{6})", mensaje)

    if not usuario_match or not pin_match:
        return jsonify({
            "respuesta": "Por favor envíame tu usuario y PIN en el formato correcto. Ejemplo: 'mi usuario es camilamelo_01 y mi PIN es 123456'"
        })

    usuario = usuario_match.group(1)
    pin = int(pin_match.group(1))

    df = cargar_datos()
    if df is None:
        return jsonify({"respuesta": "No se pudo acceder al archivo de reportes. Intenta más tarde."})

    creador = df[df["Nombre de usuario del creador"].str.lower() == usuario]

    if creador.empty:
        return jsonify({"respuesta": f"No encontré ningún creador con el usuario '{usuario}'."})

    if int(creador.iloc[0]["PIN"]) != pin:
        return jsonify({"respuesta": "El PIN no es correcto para ese usuario. Inténtalo de nuevo."})

    respuesta = (
        f"✅ Reporte de @{usuario}:\n"
        f"- Diamantes: {creador.iloc[0]['Diamantes']}\n"
        f"- Días en LIVE: {creador.iloc[0]['Días válidos de emisiones LIVE']}\n"
        f"- Horas en LIVE: {creador.iloc[0]['Duración de LIVE']}\n"
        f"- Ingresos por suscripciones: ${creador.iloc[0]['Ingresos por suscripciones']:.2f}\n"
        f"- Nuevos seguidores: {creador.iloc[0]['Suscriptores']}\n"
        "\n✨ Aqui tienes tu reporte  ✨"
    )

    return jsonify({"respuesta": respuesta})

# Endpoint raíz para evitar error 404
@app.route("/")
def inicio():
    return "✅ API de reportes de Superiority está activa."

if __name__ == "__main__":
    app.run(debug=True)
