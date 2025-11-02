# app.py
from flask import Flask, send_from_directory,render_template
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os
import sys

# tambahkan project root ke path agar import modul internal berjalan
sys.path.append(os.path.dirname(__file__))

# import db & resource (modular)
from models.user import db              # models/user.py harus define `db = SQLAlchemy()` (tidak meng-import app)
from resources.auth import AuthRegister, AuthLogin
from resources.user import UserResource

def create_app():
    app = Flask(__name__, static_folder="static")
    api = Api(app)
    CORS(app)

    # konfigurasi DB via env var (MySQL) — fallback ke sqlite jika tidak ada
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_NAME = os.getenv("DB_NAME")

    if DB_USER and DB_PASS and DB_NAME:
        # gunakan pymysql driver
        app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"
    else:
        basedir = os.path.dirname(os.path.abspath(__file__))
        app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/flask_modular"


    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # JWT config
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)

    # init extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # register resource routes (flask-restful)
    api.add_resource(AuthRegister, "/auth/register")
    api.add_resource(AuthLogin, "/auth/login")
    api.add_resource(UserResource, '/api/users', '/api/users/<int:user_id>')

    # serve frontend index.html (optional)
    @app.route('/')
    def index():
        return render_template('index.html')

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    print(app.url_map)
    app.run(debug=True, port=5005)
