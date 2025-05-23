from app import mysql,swagger,app
from flask import request, jsonify
from datetime import datetime
from model.protocoloModel import db,Imagem
import os
from werkzeug.utils import secure_filename
import os
import uuid
import json

@app.route('/protocolos', methods=['GET'])
def get_protocolos():    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            p.*,
            JSON_ARRAYAGG(
                JSON_OBJECT(
                    'id', i.id,
                    'url', i.url,
                    'created_at', i.created_at,
                    'updated_at', i.updated_at
                )
            ) AS imagens
        FROM protocolo p
        LEFT JOIN imagem i ON p.id = i.protocolo_id AND i.deleted_at IS NULL
        WHERE p.deleted_at IS NULL
        GROUP BY p.id
        ORDER BY p.created_at DESC
    """,)
    
    protocolos = cur.fetchall()
    return jsonify(protocolos), 200
  

@app.route('/add_protocolo/', methods=['POST'])
def add_protocolo():    
    data = request.form.to_dict()

    # Recebendo arquivos imagens
    imagens = request.files.getlist('imagens')  # campo 'imagens' com múltiplos arquivos

    # Extração de dados do formulário
    titulo = request.form.get('titulo')
    nome = request.form.get('nome')
    cpf = request.form.get('cpf')
    email = request.form.get('email')
    telefone = request.form.get('telefone')
    descricao = request.form.get('descricao')
    latitude = float(request.form['latitude']) if 'latitude' in data else None
    longitude = float(request.form['longitude']) if 'longitude' in data else None
    id_usuario = int(request.form['id_usuario']) if 'id_usuario' in data else None

    cur = mysql.connection.cursor()

    # Inserir protocolo
    cur.execute("""
        INSERT INTO protocolo 
        (titulo, nome, cpf, email, telefone, descricao,latitude, longitude, id_usuario)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        titulo, nome, cpf, email, telefone, descricao,
        latitude, longitude, id_usuario
    ))

    mysql.connection.commit()

    protocolo_id = cur.lastrowid  # << ID do protocolo recém-criado

    # Salvar imagens no disco e no banco
    urls_salvas = []
    for img in imagens:
        if img.filename == '':
            continue

        filename = secure_filename(img.filename)
        filename = f"{uuid.uuid4().hex}_{filename}"  # Evitar conflito de nomes
        caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img.save(caminho_salvar)

        url_img = f'/static/uploads/{filename}'  # URL pública da imagem

        # Salvar imagem no banco
        cur.execute("""
            INSERT INTO imagem (url, protocolo_id)
            VALUES (%s, %s)
        """, (url_img, protocolo_id))
        
        urls_salvas.append(url_img)

    mysql.connection.commit()
    cur.close()

    return jsonify({
        "mensagem": "protocolo criado com sucesso!",
        "id_protocolo": protocolo_id,
        "imagens": urls_salvas
    }), 201
    
@app.route('/protocolos_usuario/<int:id>', methods=['GET'])
def protocolos_usuario(id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            p.*,
            JSON_ARRAYAGG(
                JSON_OBJECT(
                    'id', i.id,
                    'url', i.url,
                    'created_at', i.created_at,
                    'updated_at', i.updated_at
                )
            ) AS imagens
        FROM protocolo p
        LEFT JOIN imagem i ON p.id = i.protocolo_id AND i.deleted_at IS NULL
        WHERE p.deleted_at IS NULL AND id_usuario = %s
        GROUP BY p.id
        ORDER BY p.created_at DESC
    """,
        (id,)
    )
    
    protocolos = cur.fetchall()
    return jsonify(protocolos), 200
      
@app.route('/protocolo/<int:id>', methods=['PUT'])
def update_protocolo(id):
  data = request.form.to_dict()

  # Recebendo arquivos imagens
  imagens = request.files.getlist('imagens')
  print(data)
  # Extração de dados do formulário
  titulo = request.form.get('titulo')
  nome = request.form.get('nome')
  cpf = request.form.get('cpf')
  email = request.form.get('email')
  telefone = request.form.get('telefone')
  descricao = request.form.get('descricao')
  latitude = float(request.form['latitude']) if 'latitude' in data else None
  longitude = float(request.form['longitude']) if 'longitude' in data else None
  id_usuario = int(request.form['id_usuario']) if 'id_usuario' in data else None

  cur = mysql.connection.cursor()

  # Atualizar protocolo
  cur.execute("""
      UPDATE protocolo
      SET titulo=%s, nome=%s, cpf=%s, email=%s, telefone=%s,
          descricao=%s, latitude=%s, longitude=%s, id_usuario=%s
      WHERE id=%s AND deleted_at IS NULL
  """, (
      titulo, nome, cpf, email, telefone,
      descricao, latitude, longitude, id_usuario, id
  ))

  protocolo_id = id

  # Verificar quantas imagens já existem
  cur.execute("SELECT COUNT(*) AS total FROM imagem WHERE protocolo_id = %s", (id,))
  resultado = cur.fetchone()
  quantidade_existente = resultado['total'] if resultado else 0

  # Filtrar apenas imagens válidas (nome de arquivo não vazio)
  imagens_validas = [img for img in imagens if img.filename != '']

  # Verifica limite de 5 imagens
  if quantidade_existente + len(imagens_validas) > 5:
      return jsonify({"error": "Limite de 5 imagens por protocolo excedido"}), 400

  # Salvar novas imagens
  for img in imagens_validas:
      filename = secure_filename(img.filename)
      filename = f"{uuid.uuid4().hex}_{filename}"
      caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], filename)
      img.save(caminho_salvar)

      url_img = f'/static/uploads/{filename}'
      cur.execute("""
          INSERT INTO imagem (url, protocolo_id)
          VALUES (%s, %s)
      """, (url_img, protocolo_id))

  mysql.connection.commit()
  return jsonify({"message": "Protocolo atualizado com sucesso"}), 200

@app.route('/protocolo/<int:id>', methods=['DELETE'])
def delete_protocolo(id):

    deleted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur = mysql.connection.cursor()
    cur.execute("UPDATE protocolo SET deleted_at = %s WHERE id = %s", (deleted_at, id))
    mysql.connection.commit()
    return jsonify({"message": "Protocolo excluído com sucesso"}), 200

@app.route('/protocolo/<int:id>', methods=['GET'])
def get_protocolo(id):
  
  cur = mysql.connection.cursor()
  cur.execute("""
      SELECT 
          p.*,
          JSON_ARRAYAGG(
              JSON_OBJECT(
                  'id', i.id,
                  'url', i.url,
                  'created_at', i.created_at,
                  'updated_at', i.updated_at
              )
          ) AS imagens
      FROM protocolo p
      LEFT JOIN imagem i ON p.id = i.protocolo_id AND i.deleted_at IS NULL
      WHERE p.deleted_at IS NULL AND p.id = %s
      GROUP BY p.id
      ORDER BY p.created_at DESC
  """,(id,))
    
  row = cur.fetchone()
  if row and 'imagens' in row and isinstance(row['imagens'], str):
      try:
          row['imagens'] = json.loads(row['imagens'])
      except json.JSONDecodeError:
          row['imagens'] = []

  return jsonify(row), 200
    

