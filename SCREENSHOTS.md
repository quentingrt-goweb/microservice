# Captures d'écran du Projet

## 1. Interface ActiveMQ

### Console Web ActiveMQ
- URL: http://localhost:8161
- Identifiants: admin/admin
- Capture d'écran des files d'attente
- Capture d'écran des messages en transit

## 2. Tests de Paiement

### Requête de Paiement
- Capture d'écran de la requête curl/PowerShell
- Capture d'écran de la réponse

### Logs des Services
- Capture d'écran des logs du Gateway Service
- Capture d'écran des logs du Card Validation Service
- Capture d'écran des logs du Client Bank Service
- Capture d'écran des logs du Merchant Bank Service
- Capture d'écran des logs du Notification Service

## 3. Base de Données

### État Initial
- Capture d'écran des données clients
- Capture d'écran des données marchands

### Après Transaction
- Capture d'écran des soldes mis à jour
- Capture d'écran des transactions

## 4. Docker

### État des Conteneurs
- Capture d'écran de `docker-compose ps`
- Capture d'écran des logs Docker

## 5. Tests d'Intégration

### Scénarios de Test
- Capture d'écran des tests réussis
- Capture d'écran des tests d'erreur
- Capture d'écran des timeouts

## 6. Monitoring

### Métriques
- Capture d'écran des temps de réponse
- Capture d'écran des taux de succès
- Capture d'écran des erreurs

## Instructions pour les Captures d'écran

Pour prendre des captures d'écran pertinentes :

1. **ActiveMQ Console**
   ```bash
   # Accéder à la console
   http://localhost:8161
   ```

2. **Logs des Services**
   ```bash
   # Voir les logs en temps réel
   docker-compose logs -f
   ```

3. **Base de Données**
   ```bash
   # Vérifier les données
   docker-compose exec postgres psql -U postgres -d payment_db -c "SELECT * FROM clients; SELECT * FROM merchants;"
   ```

4. **État des Conteneurs**
   ```bash
   # Vérifier l'état des services
   docker-compose ps
   ```

## Format des Captures d'écran

Pour chaque capture d'écran :
1. Inclure un titre descriptif
2. Ajouter une légende explicative
3. Masquer les informations sensibles
4. Utiliser un format clair et lisible

## Exemple de Capture d'écran

```
[Capture d'écran de la console ActiveMQ]
Titre: Console Web ActiveMQ - Files d'attente
Description: Vue des files d'attente actives dans ActiveMQ
Date: [Date de la capture]
```

## Notes

- Les captures d'écran doivent être prises dans un environnement de test
- Masquer les informations sensibles (mots de passe, clés API, etc.)
- Inclure des annotations pour expliquer les points importants
- Utiliser un format d'image compressé pour le partage 