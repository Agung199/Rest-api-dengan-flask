from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models.user import db, User

class AuthRegister(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nama', required=True)
        parser.add_argument('password', required=True)
        parser.add_argument('umur', type=int)
        parser.add_argument('alamat')
        data = parser.parse_args()

        if User.query.filter_by(nama=data['nama']).first():
            return {"msg": "User sudah terdaftar"}, 400

        hashed_pw = generate_password_hash(data['password'])
        new_user = User(
            nama=data['nama'],
            password=hashed_pw,
            umur=data['umur'],
            alamat=data['alamat']
        )
        db.session.add(new_user)
        db.session.commit()
        return {"msg": "Registrasi berhasil"}, 201


class AuthLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nama', required=True)
        parser.add_argument('password', required=True)
        data = parser.parse_args()

        user = User.query.filter_by(nama=data['nama']).first()
        if not user or not check_password_hash(user.password, data['password']):
            return {"msg": "Nama atau password salah"}, 401

        token = create_access_token(identity=str(user.id))
        return {"msg": "Login berhasil", "token": token}, 200
