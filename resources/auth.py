# resources/auth.py
from flask_restful import Resource
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models.user import User, db

# REGISTER
class AuthRegister(Resource):
    def post(self):
        data = request.get_json()
        nama = data.get("nama")
        password = data.get("password")
        umur = data.get("umur")
        alamat = data.get("alamat")

        if User.query.filter_by(nama=nama).first():
            return {"msg": "Nama sudah terdaftar."}, 400

        hashed_pw = generate_password_hash(password)
        user = User(nama=nama, password=hashed_pw, umur=umur, alamat=alamat)
        db.session.add(user)
        db.session.commit()

        return {
            "msg": "Registrasi berhasil.",
            "user": {
                "id": user.id,
                "nama": user.nama,
                "umur": user.umur,
                "alamat": user.alamat
            }
        }, 201


# LOGIN
class AuthLogin(Resource):
    def post(self):
        data = request.get_json()
        nama = data.get("nama")
        password = data.get("password")

        user = User.query.filter_by(nama=nama).first()
        if not user or not check_password_hash(user.password, password):
            return {"msg": "Nama atau password salah."}, 401

        # Penting: sub JWT harus string
        access_token = create_access_token(identity=str(user.id),
                                           additional_claims={"nama": user.nama})

        return {
            "msg": "Login berhasil.",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "nama": user.nama,
                "umur": user.umur,
                "alamat": user.alamat
            }
        }, 200
