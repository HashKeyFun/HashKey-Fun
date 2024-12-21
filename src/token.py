from flask import Blueprint, request, jsonify
from .db import get_db

bp = Blueprint('token', __name__, url_prefix='/token')


@bp.route('', methods=['GET'])
def read_token():
    request_id = request.args.get('request_id')
    contract_address = request.args.get('contract_address')
    
    db = get_db()
    token = None
    if request_id:
        token = db.execute(
            'SELECT * FROM tokens WHERE request_id = ?', (request_id,)
        ).fetchone()
    elif contract_address:
        token = db.execute(
            'SELECT * FROM tokens WHERE contract_address = ?', (contract_address,)
        ).fetchone()
    
    if token is None:
        return jsonify({"error": "Token not found"}), 404
    
    return jsonify({
        "request_id": token['request_id'],
        "contract_address": token['contract_address'],
        "image": token['image'],
        "description": token['description']
    })


@bp.route('all', methods=['GET'])
def read_token_all():
    db = get_db()
    tokens = db.execute('SELECT * FROM tokens').fetchall()
    
    return jsonify([{
        "request_id": token['request_id'],
        "contract_address": token['contract_address'],
        "image": token['image'],
        "description": token['description']
    } for token in tokens])


@bp.route('create', methods=['POST'])
def create_token():
    data = request.get_json()
    request_id = data.get('request_id')
    image = data.get('image')
    description = data.get('description')
    
    db = get_db()
    db.execute(
        'INSERT INTO tokens (request_id, image, description) VALUES (?, ?, ?)',
        (request_id, image, description)
    )
    db.commit()
    
    return jsonify({
        "request_id": request_id,
        "contract_address": None,
        "image": image,
        "description": description
    }), 201


@bp.route('update', methods=['PUT'])
def update_token():
    data = request.get_json()
    request_id = data.get('request_id')
    image = data.get('image')
    description = data.get('description')
    
    db = get_db()
    db.execute(
        'UPDATE tokens SET image = ?, description = ? WHERE request_id = ?',
        (image, description, request_id)
    )
    db.commit()
    
    token = db.execute(
        'SELECT * FROM tokens WHERE request_id = ?', (request_id,)
    ).fetchone()
    
    return jsonify({
        "request_id": token['request_id'],
        "contract_address": token['contract_address'],
        "image": token['image'],
        "description": token['description']
    })
