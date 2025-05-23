import os
from flask import request, jsonify
from werkzeug.utils import secure_filename
from app import app, mysql
from flask_bcrypt import Bcrypt
from datetime import datetime

bcrypt = Bcrypt(app)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/usuarios', methods=['GET'])
def get_usuarios():    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuario WHERE deleted_at IS NULL ORDER BY created_at DESC")
    usuarios = cur.fetchall()
    return jsonify(usuarios), 200




@app.route('/usuarios', methods=['POST'])
def add_usuario():
    try:
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        CPF = request.form.get('CPF')
        telefone = request.form.get('telefone')
        password = request.form.get('password')
        username = request.form.get('username')

        if not (first_name and last_name and email and CPF and telefone and password):
            return jsonify({'error': 'Todos os campos são obrigatórios'}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Lida com a foto se enviada
        foto_path = None
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto and allowed_file(foto.filename):
                filename = secure_filename(f"{datetime.utcnow().timestamp()}_{foto.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                foto.save(filepath)
                foto_path = filepath  # ou apenas o nome do arquivo, se preferir salvar no banco

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO usuario 
            (first_name, last_name, email, cpf, telefone, password, username, foto_perfil, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            first_name, last_name, email, CPF, telefone,
            hashed_password, username, foto_path, datetime.utcnow()
        ))
        mysql.connection.commit()

        return jsonify({'message': 'Usuário criado com sucesso!'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/login', methods=['POST'])
def login_usuario():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuario WHERE email = %s", (email,))
    usuario = cur.fetchone()

    if not usuario:
        return jsonify({"error": "Usuário não encontrado."}), 404

    senha_correta = bcrypt.check_password_hash(usuario['password'], senha)

    if senha_correta:
        return jsonify({"message": "Login realizado com sucesso!","usuario":usuario}), 200
    else:
        return jsonify({"error": "Senha incorreta."}), 401