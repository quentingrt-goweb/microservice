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
PAYMENT_PROCESSED_QUEUE = "payment.processed"
PAYMENT_FAILED_QUEUE = "payment.failed"

class NotificationListener(stomp.ConnectionListener):
    def __init__(self, conn):
        self.conn = conn

    def send_notification(self, payment_data: dict, status: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if status == "success":
            message = f"""
            [{timestamp}] Payment Successful
            Payment ID: {payment_data['paymentId']}
            Amount: {payment_data['amount']} {payment_data['currency']}
            Client ID: {payment_data['clientId']}
            Merchant ID: {payment_data['merchantId']}
            """
        else:
            message = f"""
            [{timestamp}] Payment Failed
            Payment ID: {payment_data['paymentId']}
            Error: {payment_data.get('error', 'Unknown error')}
            """
        
        print(message)
        # Dans un environnement réel, on pourrait envoyer un email ou une notification push ici

    def on_message(self, frame):
        try:
            # Décodage du message
            payment_data = json.loads(frame.body)
            
            # Détermination du statut basé sur la queue
            status = "success" if frame.headers.get('destination', '').endswith(PAYMENT_PROCESSED_QUEUE) else "failed"
            
            # Envoi de la notification
            self.send_notification(payment_data, status)
                
        except Exception as e:
            print(f"Error processing notification: {str(e)}")

def main():
    # Connexion à ActiveMQ avec retry
    max_retries = 10
    for attempt in range(max_retries):
        try:
            conn = stomp.Connection([(ACTIVEMQ_HOST, ACTIVEMQ_PORT)])
            conn.set_listener('', NotificationListener(conn))
            conn.connect(wait=True)
            break
        except Exception as e:
            print(f"[WARN] ActiveMQ not ready, retrying in 3s... ({attempt+1}/{max_retries})")
            time.sleep(3)
    else:
        print("[ERROR] Could not connect to ActiveMQ after several attempts. Exiting.")
        exit(1)
    
    # Abonnement aux queues de paiement
    conn.subscribe(f"/queue/{PAYMENT_PROCESSED_QUEUE}", id=1, ack='auto')
    conn.subscribe(f"/queue/{PAYMENT_FAILED_QUEUE}", id=2, ack='auto')
    
    print("Notification service started. Waiting for payment notifications...")
    
    # Boucle principale
    try:
        while True:
            pass
    except KeyboardInterrupt:
        conn.disconnect()

if __name__ == "__main__":
    main() 