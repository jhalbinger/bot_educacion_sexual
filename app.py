from flask import Flask, request
import requests

app = Flask(__name__)

# Diccionario global para guardar el contexto de cada usuario
contextos = {}

@app.route('/')
def index():
    return "✅ Microservicio conectado a Watson Assistant v1 con contexto y audio"

@app.route('/webhook', methods=['POST'])
def webhook():
    mensaje = request.form.get('Body', '').strip()
    numero_completo = request.form.get('From', '')
    numero_limpio = numero_completo.replace("whatsapp:", "")

    print(f"📨 WhatsApp: {numero_limpio} dice: {mensaje}")

    # Verificar si es un audio
    if 'MediaUrl0' in request.form and request.form.get('MediaContentType0', '').startswith('audio'):
        media_url = request.form.get('MediaUrl0')
        print(f"🔊 Audio recibido: {media_url}")

        # Descargar y reenviar el audio al microservicio de transcripción
        try:
            audio_response = requests.get(media_url)
            files = {'audio': ('audio.ogg', audio_response.content, 'audio/ogg')}
            transcripcion_response = requests.post('https://transcripcion-ahub.onrender.com/transcripcion', files=files)

            if transcripcion_response.status_code == 200:
                texto_transcripto = transcripcion_response.json().get("transcription", "No se pudo transcribir el audio.")
                return f"<Response><Message>🎧 Transcripción: {texto_transcripto}</Message></Response>", 200, {'Content-Type': 'text/xml'}
            else:
                print("❌ Error transcribiendo:", transcripcion_response.text)
                return f"<Response><Message>⚠️ Error al transcribir el audio.</Message></Response>", 200, {'Content-Type': 'text/xml'}

        except Exception as e:
            print("❌ Excepción al procesar audio:", str(e))
            return f"<Response><Message>⚠️ No se pudo procesar el audio.</Message></Response>", 200, {'Content-Type': 'text/xml'}

    # Si no es audio, proceder como texto
    respuesta_watson = enviar_a_watson(mensaje, numero_limpio)
    return f"<Response><Message>{respuesta_watson}</Message></Response>", 200, {'Content-Type': 'text/xml'}

def enviar_a_watson(mensaje, session_id):
    url = "https://api.us-south.assistant.watson.cloud.ibm.com/v1/workspaces/a17b54a3-ea98-4362-9766-c76e17484475/message?version=2021-06-14"
    auth = ("apikey", "O7cWhbMQ1oJPx-IpcxNVMXxy8nGa2L7fz873rOG_4bcA")

    contexto_prev = contextos.get(session_id, {})
    contexto_prev['telefono'] = session_id

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
        print(f"❌ Error al contactar a Watson: {response.status_code}")
        return "⚠️ Ocurrió un error al contactar al bot."
