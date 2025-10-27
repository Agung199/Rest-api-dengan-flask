# app.py

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
import traceback

app = Flask(__name__)
api = Api(app)
CORS(app)

# konfigurasi database (gunakan satu konfigurasi)
basedir = os.path.dirname(os.path.abspath(__file__))
database = "sqlite:///" + os.path.join(basedir, "db.sqlite")
app.config['SQLALCHEMY_DATABASE_URI'] = database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    umur = db.Column(db.Integer, nullable=True)
    alamat = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<User {self.nama}>'

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            # cetak stack trace untuk debugging
            traceback.print_exc()
            db.session.rollback()
            return False

    def to_dict(self):
        return {"id": self.id, "nama": self.nama, "umur": self.umur, "alamat": self.alamat}


# jangan panggil db.create_all() di sini (di luar app context) — itu sumber error

# variabel global sederhana (tetap jika diperlukan)
identitas = {}

class UserResource(Resource):
    """
    Satu resource untuk:
    - GET /api           -> list semua user
    - POST /api          -> buat user baru
    - GET /api/<id>      -> ambil user tertentu
    - PUT /api/<id>      -> update user
    - DELETE /api/<id>   -> hapus user
    """

    def get(self, user_id=None):
        if user_id is None:
            # return list semua user
            users = User.query.all()
            return {"users": [u.to_dict() for u in users]}, 200
        else:
            # return single user
            user = User.query.get(user_id)
            if not user:
                return {"msg": "User tidak ditemukan."}, 404
            return {"user": user.to_dict()}, 200
        
    
    def post(self):
        # create new user (POST ke /api)
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        nama = (data.get("nama") or "").strip()
        umur = data.get("umur")
        alamat = data.get("alamat")

        if not nama:
            return {"msg": "Field 'nama' wajib diisi."}, 400
        if len(nama) > 100:
            return {"msg": "Field 'nama' terlalu panjang (max 100)."}, 400

        umur_int = None
        if umur is not None and umur != "":
            try:
                umur_int = int(umur)
                if umur_int < 0:
                    return {"msg": "Field 'umur' harus bilangan bulat tidak negatif."}, 400
            except (ValueError, TypeError):
                return {"msg": "Field 'umur' harus angka."}, 400

        user = User(nama=nama, umur=umur_int, alamat=alamat)
        try:
            db.session.add(user)
            db.session.commit()
            return {"msg": "Data berhasil dimasukkan", "user": user.to_dict()}, 201
        except Exception:
            traceback.print_exc()
            db.session.rollback()
            return {"msg": "Terjadi kesalahan saat menyimpan data."}, 500
    
        
    def put(self, user_id: None):
        """
        update user(partial allowed) Menerima JSON atau form-data
        field yang tidak disertakan tidak diubah. untuk mengosongkan umur kirim.
        """
        users = User.query.get(user_id)
        if not users:
            return {"msg": "user tidak ditemukan."},404
        
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        nama = data.get("nama")
        umur = data.get("umur")
        alamat = data.get("alamat")

        # validate dan assign nama
        if nama is not None:
            nama = nama.strip()
            if not nama:
                return {"msg":"field 'nama' tidak boleh kosong."}, 400
            if len(nama)> 100:
                return {"msg": "field 'nama' terlalu panjang(max:100)."}, 400
            users.nama = nama
        
        # validate dan assign umur
        if umur is not None:
            if umur == "":
                users.umur = None
            else:
                try:
                    umur_int = int(umur)
                    if umur_int < 0:
                        return {"msg": "filed 'umur' harus bilangan bulat tidak boleh negatif."}, 400
                    users.umur = umur_int
                except(ValueError, TypeError):
                    return {"msg": "field 'nama' harus angka."}, 400
                
        # assign alamat(boleh kosong string)
        if alamat is not None:
            users.alamat = alamat

        try:
            db.session.commit()
            return {"msg": "Data berhasil diperbarui.", "user": users.to_dict()}, 200
        except Exception:
            traceback.print_exc()
            db.session.rollback()
            return {"msg": "terjadi kesalahan penambahan."}, 500
        
    def delete(self, user_id=None):
        # delete user (DELETE ke /api/<id>)
        if user_id is None:
            return {"msg": "User id diperlukan untuk menghapus."}, 400

        user = User.query.get(user_id)
        if not user:
            return {"msg": "User tidak ditemukan."}, 404

        try:
            db.session.delete(user)
            db.session.commit()
            return {"msg": "User berhasil dihapus."}, 200
        except Exception:
            traceback.print_exc()
            db.session.rollback()
            return {"msg": "Terjadi kesalahan saat menghapus user."}, 500
#api.add_resource(ContohResource, "/api", methods=["GET", "POST"])

api.add_resource(UserResource, "/api", "/api/<int:user_id>")



if __name__ == "__main__":
    # buat tabel dalam konteks aplikasi
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5005)
