from flask import Flask, request
import requests

app = Flask(__name__)

# Diccionario global para guardar el contexto de cada usuario
contextos = {}

@app.route('/')
def index():
    return "✅ Microservicio conectado a Watson Assistant v1 con contexto"

@app.route('/webhook', methods=['POST'])
def webhook():
    mensaje = request.form.get('Body', '').strip()
    numero_completo = request.form.get('From', '')  # Ejemplo: whatsapp:+5491123456789
    numero_limpio = numero_completo.replace("whatsapp:", "")

    print(f"📨 WhatsApp: {numero_limpio} dice: {mensaje}")

    respuesta_watson = enviar_a_watson(mensaje, numero_limpio)
    return f"<Response><Message>{respuesta_watson}</Message></Response>", 200, {'Content-Type': 'text/xml'}

def enviar_a_watson(mensaje, session_id):
    url = "https://api.us-south.assistant.watson.cloud.ibm.com/v1/workspaces/a17b54a3-ea98-4362-9766-c76e17484475/message?version=2021-06-14"
    
    auth = ("apikey", "O7cWhbMQ1oJPx-IpcxNVMXxy8nGa2L7fz873rOG_4bcA")

    # Usar el contexto anterior si existe
    contexto_prev = contextos.get(session_id, {})

    # Agregar el número al contexto como 'telefono'
    contexto_prev['telefono'] = session_id

    payload = {
        "input": {"text": mensaje},
        "context": contexto_prev
    }

    response = requests.post(url, json=payload, auth=auth)

    if response.status_code == 200:
        data = response.json()

        # Guardar el nuevo contexto para ese número de WhatsApp
        contextos[session_id] = data.get("context", {})

        try:
            # ✅ Unir todas las líneas en una sola respuesta para WhatsApp
            lineas = data["output"]["text"]
            return "\n".join(lineas)
        except (KeyError, IndexError):
            return "⚠️ Watson no devolvió una respuesta válida."
    else:
        print(f"❌ Error al contactar a Watson: {response.status_code}")
        return "⚠️ Ocurrió un error al contactar al bot."
