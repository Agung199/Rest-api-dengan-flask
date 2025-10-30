# resources/user.py
import traceback
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt_identity
from models.user import User, db


class UserResource(Resource):
    def get(self, user_id=None):
        if user_id:
            user = User.query.get(user_id)
            if not user:
                return {"msg": "User tidak ditemukan"}, 404
            return user.to_dict(), 200
        else:
            users = User.query.all()
            return {"users": [u.to_dict() for u in users]}, 200


    @jwt_required()
    def put(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"msg": "User tidak ditemukan."}, 404

        identity = get_jwt_identity()
        if identity["id"] != user.id:
            return {"msg": "Tidak boleh mengubah data user lain."}, 403

        data = request.get_json() if request.is_json else request.form.to_dict()
        nama = data.get("nama")
        umur = data.get("umur")
        alamat = data.get("alamat")

        if nama:
            user.nama = nama.strip()
        if umur:
            try:
                user.umur = int(umur)
            except:
                return {"msg": "Field 'umur' harus angka."}, 400
        if alamat is not None:
            user.alamat = alamat

        try:
            db.session.commit()
            return {"msg": "Data berhasil diperbarui.", "user": user.to_dict()}, 200
        except Exception:
            traceback.print_exc()
            db.session.rollback()
            return {"msg": "Terjadi kesalahan update data."}, 500

    @jwt_required()   # atau pakai verify_jwt_in_request() di dalam try
    def delete(self, user_id):
        try:
            # debug prints
            print("=== DELETE called ===")
            print("headers:", dict(request.headers))
            try:
                # ini akan raise kalau token invalid/missing
                verify_jwt_in_request()
                print("jwt identity:", get_jwt_identity())
            except Exception as e:
                print("JWT verify error:", repr(e))
                raise

            user = User.query.get(user_id)
            if not user:
                return {"msg":"User tidak ditemukan."}, 404
            db.session.delete(user)
            db.session.commit()
            return {"msg":"User berhasil dihapus."}, 200

        except Exception as e:
            db.session.rollback()
            import traceback; traceback.print_exc()
            return {"msg": "Terjadi kesalahan: "+str(e)}, 500
