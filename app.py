from flask import Flask, request
import requests
import os
import json

app = Flask(__name__)
contextos = {}

@app.route("/")
def index():
    return "✅ Microservicio conectado a Watson Assistant v1 con soporte de audio"

@app.route("/webhook", methods=["POST"])
def webhook():
    mensaje = request.form.get("Body", "").strip()
    numero_completo = request.form.get("From", "")
    numero_limpio = numero_completo.replace("whatsapp:", "")
    tipo_mensaje = request.form.get("NumMedia", "0")

    if tipo_mensaje != "0":
        media_url = request.form.get("MediaUrl0")
        content_type = request.form.get("MediaContentType0", "")
        print(f"🔊 Audio recibido: {media_url} ({content_type})")

        try:
            # Descargar el archivo desde Twilio
            audio_response = requests.get(media_url)
            with open("audio.ogg", "wb") as f:
                f.write(audio_response.content)

            # Enviar el archivo al microservicio de transcripción + respuesta
            with open("audio.ogg", "rb") as audio_file:
                transcripcion_response = requests.post(
                    "https://transcriptor-respondedor.onrender.com/transcripcion",
                    files={"audio": audio_file}
                )

            if transcripcion_response.status_code == 200:
                respuesta_json = transcripcion_response.json()
                texto_transcripto = respuesta_json.get("respuesta", "")

                # 🔄 Si es un dict, extraer el texto plano
                if isinstance(texto_transcripto, dict):
                    texto_transcripto = texto_transcripto.get("respuesta", "")

                if texto_transcripto.strip():
                    return f"<Response><Message>🎧 {texto_transcripto}</Message></Response>", 200, {'Content-Type': 'text/xml'}
                else:
                    return "<Response><Message>🧐 No pude entender lo que dijiste en el audio.</Message></Response>", 200, {'Content-Type': 'text/xml'}
            else:
                print("❌ Error transcribiendo:", transcripcion_response.text)
                return "<Response><Message>⚠️ Error al transcribir el audio.</Message></Response>", 200, {'Content-Type': 'text/xml'}

        except Exception as e:
            print("❌ Excepción al procesar audio:", str(e))
            return "<Response><Message>⚠️ Ocurrió un error procesando el audio.</Message></Response>", 200, {'Content-Type': 'text/xml'}

    else:
        print(f"📨 WhatsApp: {numero_limpio} dice: {mensaje}")
        respuesta_watson = enviar_a_watson(mensaje, numero_limpio)
        return f"<Response><Message>{respuesta_watson}</Message></Response>", 200, {'Content-Type': 'text/xml'}

def enviar_a_watson(mensaje, session_id):
    url = "https://api.us-south.assistant.watson.cloud.ibm.com/v1/workspaces/a17b54a3-ea98-4362-9766-c76e17484475/message?version=2021-06-14"
    auth = ("apikey", "O7cWhbMQ1oJPx-IpcxNVMXxy8nGa2L7fz873rOG_4bcA")
    contexto_prev = contextos.get(session_id, {})
    contexto_prev["telefono"] = session_id

    payload = {
        "input": {"text": mensaje},
        "context": contexto_prev
    }

    response = requests.post(url, json=payload, auth=auth)

    if response.status_code == 200:
        data = response.json()
        contextos[session_id] = data.get("context", {})
        try:
            return "\n".join(data["output"]["text"])
        except (KeyError, IndexError):
            return "⚠️ Watson no devolvió una respuesta válida."
    else:
        print("❌ Error al contactar a Watson:", response.status_code)
        return "⚠️ Ocurrió un error al contactar al bot."

if __name__ == "__main__":
    app.run()
