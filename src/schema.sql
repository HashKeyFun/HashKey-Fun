-- Create the Token table
CREATE TABLE IF NOT EXISTS Token (
    request_id TEXT PRIMARY KEY,
    contract_address TEXT,
    image TEXT NOT NULL,
    description TEXT NOT NULL,
    isApproved INTEGER DEFAULT 0,           -- 0 = false, 1 = true
    creator TEXT NOT NULL,
    createdAt TEXT DEFAULT CURRENT_TIMESTAMP,
    updatedAt TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Create the Trade table
CREATE TABLE IF NOT EXISTS Trade (
    transaction_id TEXT PRIMARY KEY,
    price TEXT NOT NULL,
    amount TEXT NOT NULL,
    token_address TEXT NOT NULL,
    address TEXT NOT NULL,
    type TEXT CHECK (type IN ('BUY', 'SELL')),
    tradedAt TEXT DEFAULT CURRENT_TIMESTAMP
);
