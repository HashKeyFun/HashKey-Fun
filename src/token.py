from flask import Blueprint, request, jsonify
from .db import get_db

bp = Blueprint('token', __name__, url_prefix='/token')


@bp.route('', methods=['GET'])
def read_token():
    request_id = request.args.get('request_id')
    contract_address = request.args.get('contract_address')
    is_approved = request.args.get('isApproved')
    
    db = get_db()
    query = 'SELECT * FROM Token WHERE 1=1'
    params = []
    
    if request_id:
        query += ' AND request_id = ?'
        params.append(request_id)
    if contract_address:
        query += ' AND contract_address = ?'
        params.append(contract_address)
    if is_approved is not None:
        query += ' AND isApproved = ?'
        params.append(1 if is_approved == 'true' else 0)
    
    token = db.execute(query, params).fetchone()
    
    if token is None:
        return jsonify({"error": "Token not found"}), 404
    
    return jsonify({
        "request_id": token['request_id'],
        "contract_address": token['contract_address'],
        "image": token['image'],
        "description": token['description'],
        "isApproved": token['isApproved'],
        "createdAt": token['createdAt'],
        "updatedAt": token['updatedAt']
    })


@bp.route('all', methods=['GET'])
def read_token_all():
    is_approved = request.args.get('isApproved')
    
    db = get_db()
    query = 'SELECT * FROM Token WHERE 1=1'
    params = []
    
    if is_approved is not None:
        query += ' AND isApproved = ?'
        params.append(1 if is_approved == 'true' else 0)
    
    tokens = db.execute(query, params).fetchall()
    
    return jsonify([{
        "request_id": token['request_id'],
        "contract_address": token['contract_address'],
        "image": token['image'],
        "description": token['description'],
        "isApproved": token['isApproved'],
        "createdAt": token['createdAt'],
        "updatedAt": token['updatedAt']
    } for token in tokens])


@bp.route('create', methods=['POST'])
def create_token():
    data = request.get_json()
    request_id = data.get('request_id')
    image = data.get('image')
    description = data.get('description')
    
    db = get_db()
    db.execute(
        'INSERT INTO Token (request_id, image, description) VALUES (?, ?, ?)',
        (request_id, image, description)
    )
    db.commit()
    
    token = db.execute(
        'SELECT * FROM Token WHERE request_id = ?', (request_id,)
    ).fetchone()
    
    return jsonify({
        "request_id": token['request_id'],
        "contract_address": token['contract_address'],
        "image": token['image'],
        "description": token['description'],
        "isApproved": token['isApproved'],
        "createdAt": token['createdAt'],
        "updatedAt": token['updatedAt']
    }), 201


@bp.route('update', methods=['PUT'])
def update_token():
    data = request.get_json()
    request_id = data.get('request_id')
    image = data.get('image')
    description = data.get('description')
    isApproved = data.get('isApproved', False)
    contract_address = data.get('contract_address')
    
    db = get_db()
    db.execute(
        'UPDATE Token SET image = ?, description = ?, isApproved = ?, contract_address = ?, updatedAt = CURRENT_TIMESTAMP WHERE request_id = ?',
        (image, description, isApproved, contract_address, request_id)
    )
    db.commit()
    
    token = db.execute(
        'SELECT * FROM Token WHERE request_id = ?', (request_id,)
    ).fetchone()
    
    return jsonify({
        "request_id": token['request_id'],
        "contract_address": token['contract_address'],
        "image": token['image'],
        "description": token['description'],
        "isApproved": token['isApproved'],
        "createdAt": token['createdAt'],
        "updatedAt": token['updatedAt']
    })
