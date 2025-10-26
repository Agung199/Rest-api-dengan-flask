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

class ContohResource(Resource):
    def get(self):
        # contoh: kembalikan semua user dari DB
        users = User.query.all()
        return {"users": [u.to_dict() for u in users]}, 200

    def post(self):
        # dukung form-data atau JSON
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        nama = data.get("nama")
        umur = data.get("umur")
        alamat = data.get("alamat")

        if not nama:
            return {"msg": "Field 'nama' wajib diisi."}, 400

        # jika umur diberikan sebagai string, coba ubah ke int (jaga safety)
        umur_int = None
        if umur:
            try:
                umur_int = int(umur)
            except ValueError:
                return {"msg": "Field 'umur' harus angka."}, 400

        user = User(nama=nama, umur=umur_int, alamat=alamat)
        ok = user.save()
        if ok:
            return {"msg": "Data berhasil dimasukkan", "user": user.to_dict()}, 201
        else:
            return {"msg": "Terjadi kesalahan saat menyimpan data."}, 500

api.add_resource(ContohResource, "/api", methods=["GET", "POST"])

if __name__ == "__main__":
    # buat tabel dalam konteks aplikasi
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5005)
