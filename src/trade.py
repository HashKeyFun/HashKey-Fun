from flask import Blueprint, request, jsonify
from .db import get_db
from datetime import datetime 

bp = Blueprint('trade', __name__, url_prefix='/trade')

@bp.route('create', methods=['POST'])
def create_trade():
    data = request.get_json()
    transaction_id = data.get('transaction_id')
    price = data.get('price')
    amount = data.get('amount')
    address = data.get('address')
    token_address = data.get('token_address')
    trade_type = data.get('type')  # 'BUY' or 'SELL'
    
    if trade_type not in ['BUY', 'SELL']:
        return jsonify({"error": "Invalid trade type"}), 400
    
    db = get_db()
    db.execute(
        'INSERT INTO Trade (transaction_id, price, amount, address, type, token_address) VALUES (?, ?, ?, ?, ?, ?)',
        (transaction_id, price, amount, address, trade_type, token_address)
    )
    db.commit()
    
    return jsonify({
        "transaction_id": transaction_id,
        "price": price,
        "amount": amount,
        "address": address,
        "type": trade_type,
        "token_address": token_address,
        "tradedAt": datetime.now()
    }), 201

@bp.route('', methods=['GET'])
def read_trade():
    transaction_id = request.args.get('transaction_id')
    
    db = get_db()
    trade = db.execute(
        'SELECT * FROM Trade WHERE transaction_id = ?', (transaction_id,)
    ).fetchone()
    
    if trade is None:
        return jsonify({"error": "Trade not found"}), 404
    
    return jsonify({
        "transaction_id": trade['transaction_id'],
        "price": trade['price'],
        "amount": trade['amount'],
        "address": trade['address'],
        "type": trade['type'],
        "token_address": trade['token_address'],
        "tradedAt": trade['tradedAt']
    })