# app.py
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from flasgger import Swagger

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuração do MySQL
app.config['MYSQL_HOST'] = 'mysqldb'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'protocolodb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['UPLOAD_FOLDER'] = '/app/uploads/'  
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  

# Configuração Swagger
app.config['SWAGGER'] = {
    'title': 'Task API',
    'uiversion': 3,
    "description": "Serviço de API para gerenciamento de tarefas",
    "version": "25.05.10.01",
}
swagger = Swagger(app)

mysql = MySQL(app)
CORS(app)

from controller.usuario_controller.usuarioController import *
from controller.protocolo_controller.protocoloController import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 