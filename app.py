from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return "✅ Microservicio conectado a Watson Assistant v1"

@app.route('/webhook', methods=['POST'])
def webhook():
    mensaje = request.form.get('Body', '').strip()
    numero = request.form.get('From', '')

    print(f"📨 WhatsApp: {numero} dice: {mensaje}")

    respuesta_watson = enviar_a_watson(mensaje, numero)
    return f"<Response><Message>{respuesta_watson}</Message></Response>", 200, {'Content-Type': 'text/xml'}

def enviar_a_watson(mensaje, session_id):
    url = "https://api.us-south.assistant.watson.cloud.ibm.com/v1/workspaces/a17b54a3-ea98-4362-9766-c76e17484475/message?version=2021-06-14"
    
    auth = ("apikey", "O7cWhbMQ1oJPx-IpcxNVMXxy8nGa2L7fz873rOG_4bcA")  # ← Tu API Key

    payload = {
        "input": {"text": mensaje},
        "context": {
            "conversation_id": session_id
        }
    }

    response = requests.post(url, json=payload, auth=auth)

    if response.status_code == 200:
        try:
            return response.json()["output"]["text"][0]
        except (KeyError, IndexError):
            return "Watson no devolvió una respuesta válida."
    else:
        print(f"❌ Error al contactar a Watson: {response.status_code}")
        return "Ocurrió un error al contactar al bot."
