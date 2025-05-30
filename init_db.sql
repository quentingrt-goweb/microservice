-- Création des tables si elles n'existent pas
CREATE TABLE IF NOT EXISTS clients (
    id VARCHAR PRIMARY KEY,
    name VARCHAR,
    card_number VARCHAR,
    expiry_date VARCHAR,
    balance NUMERIC(10, 2)
);

CREATE TABLE IF NOT EXISTS merchants (
    id VARCHAR PRIMARY KEY,
    name VARCHAR,
    balance NUMERIC(10, 2)
);

-- Insertion des données de test
INSERT INTO clients (id, name, card_number, expiry_date, balance) VALUES
('cli001', 'John Doe', '1234-5678-9012-3456', '12/26', 1000.00)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    card_number = EXCLUDED.card_number,
    expiry_date = EXCLUDED.expiry_date,
    balance = EXCLUDED.balance;

INSERT INTO merchants (id, name, balance) VALUES
('mer001', 'Amazon Store', 5000.00)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    balance = EXCLUDED.balance; 