from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    return "✅ Microservicio activo para WhatsApp-Twilio."

@app.route('/webhook', methods=['POST'])
def webhook():
    mensaje = request.form.get('Body', '').strip()
    numero = request.form.get('From', '')

    print(f"📨 Mensaje recibido de {numero}: {mensaje}")

    # Respuesta de ejemplo
    if mensaje == "1":
        respuesta = "Elegiste la opción 1: Salud sexual. ¿Querés saber sobre métodos anticonceptivos?"
    elif mensaje == "2":
        respuesta = "Elegiste la opción 2: Diversidad de género. ¿Querés conocer recursos de acompañamiento?"
    elif mensaje == "csat":
        respuesta = "Gracias por tu calificación 😊"
    else:
        respuesta = (
            "👋 ¡Hola! ¿Qué querés consultar?\n"
            "1. Salud sexual\n"
            "2. Diversidad de género\n"
            "Escribí el número de la opción."
        )

    return f"<Response><Message>{respuesta}</Message></Response>", 200, {'Content-Type': 'text/xml'}
