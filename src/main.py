# app.py

# 1) Carrega as variáveis do .env antes de tudo
from dotenv import load_dotenv
load_dotenv()

import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS

# Permite imports relativos à raiz do projeto (ajuste conforme sua estrutura)
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 2) Cria a app Flask e configura a pasta de front-end estático
app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), 'static')
)

# 3) Configurações gerais carregadas do .env (ou fallback local, se não houver)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'changeme123!')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    # Fallback local apenas para dev; em produção use sempre DATABASE_URL
    'postgresql://postgres:190702Carlos@localhost:5432/postgres'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 4) Habilita CORS para todas as rotas
CORS(app)

# 5) Importa db e blueprints **após** criar a app
from src.models.user      import db
from src.routes.user      import user_bp
from src.routes.cliente   import cliente_bp
from src.routes.visita    import visita_bp
from src.routes.campanha  import campanha_bp
from src.routes.resgate   import resgate_bp
from src.routes.dashboard import dashboard_bp

# 6) Registra todos os blueprints sob /api
for bp in (user_bp, cliente_bp, visita_bp, campanha_bp, resgate_bp, dashboard_bp):
    app.register_blueprint(bp, url_prefix='/api')

# 7) Inicializa o banco e cria as tabelas se ainda não existirem
db.init_app(app)
with app.app_context():
    db.create_all()

# 8) Rota “catch-all” para servir seu SPA (index.html + assets estáticos)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    target = os.path.join(app.static_folder, path)
    if path and os.path.exists(target):
        return send_from_directory(app.static_folder, path)
    # se não for um arquivo estático, serve index.html
    return send_from_directory(app.static_folder, 'index.html')

# 9) Executa o servidor local quando rodar diretamente
if __name__ == '__main__':
    host  = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port  = int(os.getenv('FLASK_RUN_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('true','1','t')
    print("⚙️  Starting app with:")
    print("   SECRET_KEY:", app.config['SECRET_KEY'])
    print("   DATABASE_URI:", app.config['SQLALCHEMY_DATABASE_URI'])
    app.run(host=host, port=port, debug=debug)
