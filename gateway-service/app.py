import os
import json
import stomp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import time

# Chargement des variables d'environnement
load_dotenv()

app = FastAPI(title="Gateway Service")

# Configuration ActiveMQ
ACTIVEMQ_HOST = os.getenv("ACTIVEMQ_HOST", "localhost")
ACTIVEMQ_PORT = int(os.getenv("ACTIVEMQ_PORT", "61613"))
PAYMENT_REQUEST_QUEUE = "payment.request"

# Modèle de données pour la requête de paiement
class PaymentRequest(BaseModel):
    paymentId: str
    amount: float
    currency: str
    cardNumber: str
    expiryDate: str
    clientId: str
    merchantId: str

# Connexion à ActiveMQ avec retry
max_retries = 10
for attempt in range(max_retries):
    try:
        conn = stomp.Connection([(ACTIVEMQ_HOST, ACTIVEMQ_PORT)])
        conn.connect(wait=True)
        break
    except Exception as e:
        print(f"[WARN] ActiveMQ not ready, retrying in 3s... ({attempt+1}/{max_retries})")
        time.sleep(3)
else:
    print("[ERROR] Could not connect to ActiveMQ after several attempts. Exiting.")
    exit(1)

@app.post("/payment")
async def process_payment(payment: PaymentRequest):
    try:
        # Conversion du paiement en JSON
        payment_json = payment.json()
        
        # Envoi du message à ActiveMQ
        conn.send(
            body=payment_json,
            destination=f"/queue/{PAYMENT_REQUEST_QUEUE}",
            headers={'content-type': 'application/json'}
        )
        
        return {"status": "success", "message": "Payment request sent for processing"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 