from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secre_key_protection_token'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tarefas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo
class Tarefa(db.Model):
    id = db.Column(db.String(8), primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='pendente')

# Autenticação
USERNAME = 'admin'
PASSWORD_HASH = generate_password_hash('123_base64')

def check_auth(username, password):
    return username == USERNAME and check_password_hash(PASSWORD_HASH, password)

def authenticate():
    return Response('Login necessário', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_basic_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'message': 'Token ausente!'}), 401
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido!'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
@requires_basic_auth
def login():
    token = jwt.encode({
        'user': USERNAME,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token})

# CRUD integrado com banco de dados
@app.route('/tarefas', methods=['GET'])
def listar_tarefas():
    tarefas = Tarefa.query.all()
    resultado = [{"id": t.id, "descricao": t.descricao, "status": t.status} for t in tarefas]
    return jsonify(tarefas=resultado, total=len(resultado))

@app.route('/tarefas', methods=['POST'])
def adicionar_tarefa():
    data = request.get_json()
    nova_tarefa = Tarefa(id=secrets.token_hex(2), descricao=data['descricao'])
    db.session.add(nova_tarefa)
    db.session.commit()
    return jsonify(message="Tarefa adicionada com sucesso!", tarefa={
        "id": nova_tarefa.id,
        "descricao": nova_tarefa.descricao,
        "status": nova_tarefa.status
    }), 201

@app.route('/tarefas/<string:id>', methods=['PUT'])
@token_required
def atualizar_tarefa(id):
    tarefa = Tarefa.query.get(id)
    if not tarefa:
        return jsonify(message="Tarefa não encontrada."), 404
    data = request.get_json()
    tarefa.descricao = data.get('descricao', tarefa.descricao)
    tarefa.status = data.get('status', tarefa.status)
    db.session.commit()
    return jsonify(message="Tarefa atualizada!", tarefa={
        "id": tarefa.id, "descricao": tarefa.descricao, "status": tarefa.status
    })

@app.route('/tarefas/<string:id>/pendente', methods=['PATCH'])
@token_required
def marcar_como_pendente(id):
    tarefa = Tarefa.query.get(id)
    if not tarefa:
        return jsonify(message="Tarefa não encontrada."), 404
    tarefa.status = 'pendente'
    db.session.commit()
    return jsonify(message="Tarefa marcada como pendente!", tarefa={
        "id": tarefa.id, "descricao": tarefa.descricao, "status": tarefa.status
    })

@app.route('/tarefas/<string:id>/concluida', methods=['PATCH'])
@token_required
def marcar_como_concluida(id):
    tarefa = Tarefa.query.get(id)
    if not tarefa:
        return jsonify(message="Tarefa não encontrada."), 404
    tarefa.status = 'concluída'
    db.session.commit()
    return jsonify(message="Tarefa marcada como concluída!", tarefa={
        "id": tarefa.id, "descricao": tarefa.descricao, "status": tarefa.status
    })

@app.route('/tarefas/<string:id>', methods=['DELETE'])
@token_required
def remover_tarefa(id):
    tarefa = Tarefa.query.get(id)
    if not tarefa:
        return jsonify(message="Tarefa não encontrada."), 404
    db.session.delete(tarefa)
    db.session.commit()
    return jsonify(message=f"Tarefa '{tarefa.descricao}' removida com sucesso!")

