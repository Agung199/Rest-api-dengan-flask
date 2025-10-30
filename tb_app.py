# resources/auth.py
import traceback
from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from models.user import User, db


class AuthRegister(Resource):
    def post(self):
        """
        Register user baru.
        body: { "nama": "agus", "password": "12345", "umur": 20, "alamat": "Surabaya" }
        """
        data = request.get_json() if request.is_json else request.form.to_dict()
        nama = (data.get("nama") or "").strip()
        password = data.get("password")
        umur = data.get("umur")
        alamat = data.get("alamat")

        if not nama or not password:
            return {"msg": "Field 'nama' dan 'password' wajib diisi."}, 400

        if User.query.filter_by(nama=nama).first():
            return {"msg": "Nama sudah digunakan."}, 400

        umur_int = None
        if umur:
            try:
                umur_int = int(umur)
            except:
                return {"msg": "Field 'umur' harus angka."}, 400

        user = User(nama=nama, umur=umur_int, alamat=alamat)
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            return {"msg": "Registrasi berhasil.", "user": user.to_dict()}, 201
        except Exception:
            traceback.print_exc()
            db.session.rollback()
            return {"msg": "Terjadi kesalahan saat menyimpan data."}, 500


class AuthLogin(Resource):
    def post(self):
        """
        Login user — mengembalikan JWT token
        """
        data = request.get_json() if request.is_json else request.form.to_dict()
        nama = (data.get("nama") or "").strip()
        password = data.get("password")

        if not nama or not password:
            return {"msg": "Field 'nama' dan 'password' wajib diisi."}, 400

        user = User.query.filter_by(nama=nama).first()
        if not user or not user.check_password(password):
            return {"msg": "Nama atau password salah."}, 401

        token = create_access_token(identity={"id": user.id, "nama": user.nama})
        return {"access_token": token, "user": user.to_dict()}, 200
