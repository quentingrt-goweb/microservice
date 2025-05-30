import os
import json
import stomp
from datetime import datetime
from dotenv import load_dotenv
import time

# Chargement des variables d'environnement
load_dotenv()

# Configuration ActiveMQ
ACTIVEMQ_HOST = os.getenv("ACTIVEMQ_HOST", "localhost")
ACTIVEMQ_PORT = int(os.getenv("ACTIVEMQ_PORT", "61613"))
PAYMENT_REQUEST_QUEUE = "payment.request"
CARD_VALIDATED_QUEUE = "card.validated"
PAYMENT_FAILED_QUEUE = "payment.failed"

class CardValidator:
    @staticmethod
    def validate_card(card_number: str, expiry_date: str) -> bool:
        # Vérification basique du format de la carte
        if not card_number.replace("-", "").isdigit():
            return False
        
        # Vérification de la date d'expiration
        try:
            exp_month, exp_year = expiry_date.split("/")
            exp_date = datetime.strptime(f"20{exp_year}-{exp_month}-01", "%Y-%m-%d")
            if exp_date < datetime.now():
                return False
        except:
            return False
        
        return True

class PaymentListener(stomp.ConnectionListener):
    def __init__(self, conn):
        self.conn = conn
        self.validator = CardValidator()

    def on_message(self, frame):
        try:
            # Décodage du message
            payment_data = json.loads(frame.body)
            
            # Validation de la carte
            is_valid = self.validator.validate_card(
                payment_data["cardNumber"],
                payment_data["expiryDate"]
            )
            
            # Envoi du résultat
            if is_valid:
                self.conn.send(
                    body=frame.body,
                    destination=f"/queue/{CARD_VALIDATED_QUEUE}",
                    headers={'content-type': 'application/json'}
                )
            else:
                self.conn.send(
                    body=json.dumps({
                        "paymentId": payment_data["paymentId"],
                        "error": "Invalid card"
                    }),
                    destination=f"/queue/{PAYMENT_FAILED_QUEUE}",
                    headers={'content-type': 'application/json'}
                )
                
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            # En cas d'erreur, on envoie un message d'échec
            self.conn.send(
                body=json.dumps({
                    "paymentId": payment_data.get("paymentId", "unknown"),
                    "error": str(e)
                }),
                destination=f"/queue/{PAYMENT_FAILED_QUEUE}",
                headers={'content-type': 'application/json'}
            )

def main():
    # Connexion à ActiveMQ avec retry
    max_retries = 10
    for attempt in range(max_retries):
        try:
            conn = stomp.Connection([(ACTIVEMQ_HOST, ACTIVEMQ_PORT)])
            conn.set_listener('', PaymentListener(conn))
            conn.connect(wait=True)
            break
        except Exception as e:
            print(f"[WARN] ActiveMQ not ready, retrying in 3s... ({attempt+1}/{max_retries})")
            time.sleep(3)
    else:
        print("[ERROR] Could not connect to ActiveMQ after several attempts. Exiting.")
        exit(1)
    
    # Abonnement à la queue de paiement
    conn.subscribe(f"/queue/{PAYMENT_REQUEST_QUEUE}", id=1, ack='auto')
    
    print("Card validation service started. Waiting for payment requests...")
    
    # Boucle principale
    try:
        while True:
            pass
    except KeyboardInterrupt:
        conn.disconnect()

if __name__ == "__main__":
    main() 