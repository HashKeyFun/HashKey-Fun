from flask import Blueprint, request, jsonify
from .db import get_db
from datetime import datetime, timedelta

bp = Blueprint('chart', __name__, url_prefix='/chart')

@bp.route('ohlcv', methods=['GET'])
def get_ohlcv():
    interval = request.args.get('interval', '1m')  # Default to 1 minute
    token_address = request.args.get('token_address')
    
    if not token_address:
        return jsonify({"error": "Token address is required"}), 400
    
    db = get_db()
    
    # Define the time interval in seconds
    interval_map = {
        '1m': 60,
        '10m': 600,
        '30m': 1800,
        '1h': 3600,
        '1d': 86400
    }
    
    if interval not in interval_map:
        return jsonify({"error": "Invalid interval"}), 400
    
    interval_seconds = interval_map[interval]
    
    # Calculate the OHLCV data
    query = f"""
    SELECT 
        strftime('%Y-%m-%d %H:%M:00', tradedAt) AS period,
        MIN(price) AS low,
        MAX(price) AS high,
        (SELECT price FROM Trade WHERE token_address = t.token_address AND strftime('%Y-%m-%d %H:%M:00', tradedAt) = strftime('%Y-%m-%d %H:%M:00', t.tradedAt) ORDER BY tradedAt ASC LIMIT 1) AS open,
        (SELECT price FROM Trade WHERE token_address = t.token_address AND strftime('%Y-%m-%d %H:%M:00', tradedAt) = strftime('%Y-%m-%d %H:%M:00', t.tradedAt) ORDER BY tradedAt DESC LIMIT 1) AS close,
        SUM(amount) AS volume
    FROM Trade t
    WHERE token_address = ? AND tradedAt >= datetime('now', '-{interval_seconds} seconds')
    GROUP BY strftime('%Y-%m-%d %H:%M:00', tradedAt)
    ORDER BY period;
    """
    
    trades = db.execute(query, (token_address,)).fetchall()
    
    ohlcv_data = [{
        "period": trade['period'],
        "open": trade['open'],
        "high": trade['high'],
        "low": trade['low'],
        "close": trade['close'],
        "volume": trade['volume']
    } for trade in trades]
    
    return jsonify(ohlcv_data)
