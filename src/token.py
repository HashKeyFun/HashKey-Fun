from flask import Blueprint, request, jsonify
from .db import get_db

bp = Blueprint('token', __name__, url_prefix='/token')


@bp.route('', methods=['GET'])
def read_token():
    request_id = request.args.get('request_id')
    contract_address = request.args.get('contract_address')
    is_approved = request.args.get('isApproved')
    creator = request.args.get('creator')
    
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
    if creator:
        query += ' AND creator = ?'
        params.append(creator)
        
    token = db.execute(query, params).fetchone()
    
    if token is None:
        return jsonify({"error": "Token not found"}), 404
    
    return jsonify({
        "request_id": token['request_id'],
        "contract_address": token['contract_address'],
        "image": token['image'],
        "description": token['description'],
        "isApproved": token['isApproved'],
        "creator": token['creator'],
        "createdAt": token['createdAt'],
        "updatedAt": token['updatedAt']
    })


@bp.route('all', methods=['GET'])
def read_token_all():
    is_approved = request.args.get('isApproved')
    creator = request.args.get('creator')
    db = get_db()
    query = 'SELECT * FROM Token WHERE 1=1'
    params = []
    
    if is_approved is not None:
        query += ' AND isApproved = ?'
        params.append(1 if is_approved == 'true' else 0)
    if creator:
        query += ' AND creator = ?'
        params.append(creator)
    
    tokens = db.execute(query, params).fetchall()
    
    return jsonify([{
        "request_id": token['request_id'],
        "contract_address": token['contract_address'],
        "image": token['image'],
        "description": token['description'],
        "isApproved": token['isApproved'],
        "creator": token['creator'],
        "createdAt": token['createdAt'],
        "updatedAt": token['updatedAt']
    } for token in tokens])


@bp.route('create', methods=['POST'])
def create_token():
    data = request.get_json()
    request_id = data.get('request_id')
    image = data.get('image')
    description = data.get('description')
    creator = data.get('creator')
    
    db = get_db()
    db.execute(
        'INSERT INTO Token (request_id, image, description, creator) VALUES (?, ?, ?, ?)',
        (request_id, image, description, creator)
    )
    db.commit()

    # Call the external API
    response = requests.post('http://0.0.0.0:8000/approve', json={"request_id": request_id, "description": description})
    result = response.json().get('result', {})
    violentness = result.get('violentness', 0)
    sensationality = result.get('sensationality', 0)

    is_approved = 1 if violentness <= 60 and sensationality <= 60 else 0
    
    db.execute(
        'UPDATE Token SET isApproved = ? WHERE request_id = ?',
        (is_approved, request_id)
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
        "creator": token['creator'],
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
    creator = data.get('creator')
    
    db = get_db()
    db.execute(
        'UPDATE Token SET image = ?, description = ?, isApproved = ?, contract_address = ?, creator = ?, updatedAt = CURRENT_TIMESTAMP WHERE request_id = ?',
        (image, description, isApproved, contract_address, creator, request_id)
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
        "creator": token['creator'],
        "createdAt": token['createdAt'],
        "updatedAt": token['updatedAt']
    })