import os
import json
import stomp
from sqlalchemy import create_engine, Column, String, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import time

# Chargement des variables d'environnement
load_dotenv()

# Configuration ActiveMQ
ACTIVEMQ_HOST = os.getenv("ACTIVEMQ_HOST", "localhost")
ACTIVEMQ_PORT = int(os.getenv("ACTIVEMQ_PORT", "61613"))
FUNDS_VALIDATED_QUEUE = "funds.validated"
PAYMENT_PROCESSED_QUEUE = "payment.processed"
PAYMENT_FAILED_QUEUE = "payment.failed"

# Configuration Base de données
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "payment_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# Configuration SQLAlchemy
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modèles de données
class Client(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True)
    name = Column(String)
    card_number = Column(String)
    expiry_date = Column(String)
    balance = Column(Numeric(10, 2))

class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(String, primary_key=True)
    name = Column(String)
    balance = Column(Numeric(10, 2))

# Création des tables
Base.metadata.create_all(bind=engine)

class PaymentListener(stomp.ConnectionListener):
    def __init__(self, conn):
        self.conn = conn
        self.db = SessionLocal()

    def process_transfer(self, client_id: str, merchant_id: str, amount: float) -> bool:
        try:
            # Récupération du client et du marchand
            client = self.db.query(Client).filter(Client.id == client_id).first()
            merchant = self.db.query(Merchant).filter(Merchant.id == merchant_id).first()
            
            if not client or not merchant:
                return False
            
            # Vérification du solde client
            if float(client.balance) < amount:
                return False
            
            # Mise à jour des soldes
            client.balance = float(client.balance) - amount
            merchant.balance = float(merchant.balance) + amount
            
            # Commit de la transaction
            self.db.commit()
            return True
            
        except Exception as e:
            print(f"Error processing transfer: {str(e)}")
            self.db.rollback()
            return False

    def on_message(self, frame):
        try:
            # Décodage du message
            payment_data = json.loads(frame.body)
            
            # Traitement du transfert
            transfer_success = self.process_transfer(
                payment_data["clientId"],
                payment_data["merchantId"],
                float(payment_data["amount"])
            )
            
            # Envoi du résultat
            if transfer_success:
                self.conn.send(
                    body=frame.body,
                    destination=f"/queue/{PAYMENT_PROCESSED_QUEUE}",
                    headers={'content-type': 'application/json'}
                )
            else:
                self.conn.send(
                    body=json.dumps({
                        "paymentId": payment_data["paymentId"],
                        "error": "Transfer failed"
                    }),
                    destination=f"/queue/{PAYMENT_FAILED_QUEUE}",
                    headers={'content-type': 'application/json'}
                )
                
        except Exception as e:
            print(f"Error processing message: {str(e)}")
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
    
    # Abonnement à la queue de validation des fonds
    conn.subscribe(f"/queue/{FUNDS_VALIDATED_QUEUE}", id=1, ack='auto')
    
    print("Merchant bank service started. Waiting for funds validation...")
    
    # Boucle principale
    try:
        while True:
            pass
    except KeyboardInterrupt:
        conn.disconnect()

if __name__ == "__main__":
    main() 