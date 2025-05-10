# app.py
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from flasgger import Swagger
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuração do MySQL
app.config['MYSQL_HOST'] = 'mysqldb'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'taskdb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Configuração Swagger
app.config['SWAGGER'] = {
    'title': 'Task API',
    'uiversion': 3,
    "description": "Serviço de API para gerenciamento de tarefas",
    "version": "25.05.10.01",
}
swagger = Swagger(app)

mysql = MySQL(app)

@app.route('/tasks', methods=['GET'])
def get_tasks():
    """
    Retorna todas as tarefas não deletadas
    ---
    responses:
      200:
        description: Lista de tarefas
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              task:
                type: string
              created_at:
                type: string
              updated_at:
                type: string
              deleted_at:
                type: string
                nullable: true
    """
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tasks WHERE deleted_at IS NULL ORDER BY created_at DESC")
    tasks = cur.fetchall()
    return jsonify(tasks), 200

@app.route('/tasks', methods=['POST'])
def add_task():
    """
    Cria uma nova tarefa
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - task
          properties:
            task:
              type: string
    responses:
      201:
        description: Tarefa criada com sucesso
      400:
        description: Campo obrigatório não fornecido
    """
    data = request.get_json()
    task = data.get('task')
    if not task:
        return jsonify({"error": "Campo 'task' é obrigatório"}), 400

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO tasks (task) VALUES (%s)", (task,))
    mysql.connection.commit()
    return jsonify({"message": "Tarefa criada com sucesso"}), 201

@app.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    """
    Atualiza uma tarefa existente
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - task
          properties:
            task:
              type: string
    responses:
      200:
        description: Tarefa atualizada com sucesso
      400:
        description: Campo obrigatório não fornecido
    """
    data = request.get_json()
    task = data.get('task')
    if not task:
        return jsonify({"error": "Campo 'task' é obrigatório"}), 400

    cur = mysql.connection.cursor()
    cur.execute("UPDATE tasks SET task = %s WHERE id = %s AND deleted_at IS NULL", (task, id))
    mysql.connection.commit()
    return jsonify({"message": "Tarefa atualizada com sucesso"}), 200

@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    """
    Exclui logicamente uma tarefa
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Tarefa excluída com sucesso
    """
    deleted_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    cur = mysql.connection.cursor()
    cur.execute("UPDATE tasks SET deleted_at = %s WHERE id = %s", (deleted_at, id))
    mysql.connection.commit()
    return jsonify({"message": "Tarefa excluída com sucesso"}), 200

@app.route('/tasks/<int:id>', methods=['GET'])
def get_task(id):
    """
    Retorna uma tarefa específica
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Tarefa encontrada
        schema:
          type: object
          properties:
            id:
              type: integer
            task:
              type: string
            created_at:
              type: string
            updated_at:
              type: string
            deleted_at:
              type: string
              nullable: true
      404:
        description: Tarefa não encontrada
    """
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = %s AND deleted_at IS NULL", (id,))
    task = cur.fetchone()
    if not task:
        return jsonify({"error": "Tarefa não encontrada"}), 404
    return jsonify(task), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
