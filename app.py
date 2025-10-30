from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os

import sys, os
sys.path.append(os.path.dirname(__file__))  # menambahkan root project ke PYTHONPATH


# ✅ import db dan resource
from models.user import db
from resources.auth import AuthRegister, AuthLogin
from resources.user import UserResource

# inisialisasi app
app = Flask(__name__)
api = Api(app)
CORS(app)

# konfigurasi database
basedir = os.path.dirname(os.path.abspath(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "db.sqlite")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# konfigurasi JWT
app.config["JWT_SECRET_KEY"] = "super-secret-key"  # ubah di produksi
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)

# inisialisasi ekstensi
db.init_app(app)
jwt = JWTManager(app)

# endpoint
api.add_resource(AuthRegister, "/auth/register")
api.add_resource(AuthLogin, "/auth/login")
api.add_resource(UserResource, '/api/users', '/api/users/<int:user_id>')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print(app.url_map)
    app.run(debug=True, port=5005)

