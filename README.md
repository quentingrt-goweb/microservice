# Distributed Payment System

## Description
Ce projet implémente un système de paiement distribué utilisant une architecture microservices. Le système permet de traiter des paiements en ligne de manière sécurisée et fiable, en coordonnant plusieurs services spécialisés via ActiveMQ.

## Architecture
Le système est composé des services suivants :
- **Gateway Service** (Port 8000) : Point d'entrée pour les requêtes de paiement
- **Card Validation Service** : Vérifie la validité des cartes de paiement
- **Client Bank Service** : Gère les comptes clients et les transactions
- **Merchant Bank Service** : Gère les comptes marchands et les transactions
- **Notification Service** : Envoie des notifications aux clients et marchands

## Prérequis
- Docker et Docker Compose
- Python 3.8+
- PowerShell (pour Windows) ou Terminal (pour Linux/Mac)

## Installation

1. Cloner le repository :
```bash
git clone <repository-url>
cd distributed-payment
```

2. Construire et démarrer les services :
```bash
docker-compose build --no-cache
docker-compose up -d
```

3. Initialiser la base de données avec les données de test :
```bash
docker-compose exec postgres psql -U postgres -d payment_db -f /docker-entrypoint-initdb.d/init_db.sql
```

## Test du système

### 1. Vérification des services
Vérifiez que tous les services sont en cours d'exécution :
```bash
docker-compose ps
```

### 2. Envoi d'une requête de paiement
#### Pour Windows (PowerShell) :
```powershell
$body = @{
    paymentId = "abc123"
    amount = 100.50
    currency = "EUR"
    cardNumber = "1234-5678-9012-3456"
    expiryDate = "12/26"
    clientId = "cli001"
    merchantId = "mer001"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/payment" -ContentType "application/json" -Body $body
```

#### Pour Linux/Mac :
```bash
curl -X POST http://localhost:8000/payment \
-H "Content-Type: application/json" \
-d '{
    "paymentId": "abc123",
    "amount": 100.50,
    "currency": "EUR",
    "cardNumber": "1234-5678-9012-3456",
    "expiryDate": "12/26",
    "clientId": "cli001",
    "merchantId": "mer001"
}'
```

### 3. Vérification du traitement
1. **Vérifier les logs** :
```bash
docker-compose logs -f
```

2. **Vérifier les soldes** :
```bash
docker-compose exec postgres psql -U postgres -d payment_db -c "SELECT * FROM clients; SELECT * FROM merchants;"
```

3. **Vérifier les messages dans ActiveMQ** :
- Accéder à http://localhost:8161
- Identifiants : admin/admin
- Vérifier les files d'attente dans l'onglet "Queues"

### 4. Vérification des notifications
Les notifications sont envoyées via le service de notification. Vérifiez les logs du service de notification pour voir les messages envoyés.

## Structure des données de test

### Client de test
- ID: cli001
- Nom: John Doe
- Carte: 1234-5678-9012-3456
- Date d'expiration: 12/26
- Solde initial: 1000.00 EUR

### Marchand de test
- ID: mer001
- Nom: Amazon Store
- Solde initial: 5000.00 EUR

## Dépannage

### Problèmes courants

1. **Services non démarrés** :
```bash
docker-compose down
docker-compose up -d
```

2. **Erreurs de connexion ActiveMQ** :
- Attendre quelques secondes que ActiveMQ soit complètement démarré
- Vérifier les logs : `docker-compose logs activemq`

3. **Erreurs de base de données** :
- Vérifier la connexion : `docker-compose exec postgres psql -U postgres -d payment_db`
- Réinitialiser les données : `docker-compose exec postgres psql -U postgres -d payment_db -f /docker-entrypoint-initdb.d/init_db.sql`

## Arrêt du système
```bash
docker-compose down
``` 