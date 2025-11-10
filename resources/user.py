import traceback
from flask import request, jsonify, Blueprint
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User, db


# ----------- RESOURCE BERBASIS FLASK-RESTFUL ------------
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

        # --- DEBUG PRINT ---
        identity = get_jwt_identity()
        print("DEBUG JWT identity:", repr(identity))
        print("DEBUG target user.id:", user.id)

        # --- NORMALISASI identity ---
        if isinstance(identity, dict):
            uid = identity.get("id") or identity.get("user_id") or identity.get("sub")
            role = identity.get("role")
        else:
            uid = identity
            role = None

        # --- CEK IZIN AKSES ---
        if str(uid) != str(user.id) and role != "admin":
            return {"msg": "Tidak boleh mengubah data user lain."}, 403

        # --- PROSES UPDATE DATA ---
        data = request.get_json() if request.is_json else request.form.to_dict()
        nama = data.get("nama")
        umur = data.get("umur")
        alamat = data.get("alamat")

        if nama is not None:
            if isinstance(nama, str) and nama.strip() == "":
                return {"msg": "Nama tidak boleh kosong."}, 400
            user.nama = nama.strip()

        if umur is not None and umur != "":
            try:
                user.umur = int(umur)
                if user.umur < 0:
                    return {"msg": "Umur tidak boleh negatif."}, 400
            except (ValueError, TypeError):
                return {"msg": "Field 'umur' harus angka."}, 400

        if alamat is not None:
            user.alamat = alamat

        try:
            db.session.commit()
            return {"msg": "Data berhasil diperbarui.", "user": user.to_dict()}, 200
        except Exception as e:
            traceback.print_exc()
            db.session.rollback()
            return {"msg": "Terjadi kesalahan update data.", "error": str(e)}, 500

    @jwt_required()
    def delete(self, user_id):
        try:
            user = User.query.get(int(user_id))
            if not user:
                return {"msg": "User tidak ditemukan."}, 404

            db.session.delete(user)
            db.session.commit()
            return {"msg": "User berhasil dihapus."}, 200

        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            return {"msg": f"Terjadi kesalahan saat menghapus user: {str(e)}"}, 500


# ----------- BLUEPRINT API TAMBAHAN (JIKA PAKAI FLASK NATIVE ROUTE) ------------
users_bp = Blueprint("users", __name__)

@users_bp.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "nama": user.nama,
        "umur": user.umur,
        "alamat": user.alamat
    }), 200


@users_bp.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """Route versi native Flask (bisa dihapus jika pakai Resource di atas)"""
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}

    nama = data.get("nama")
    umur = data.get("umur")
    alamat = data.get("alamat")

    if not nama or nama.strip() == "":
        return jsonify({"error": "Nama wajib diisi"}), 400

    try:
        if umur is not None:
            umur = int(umur)
            if umur < 0:
                return jsonify({"error": "Umur tidak valid"}), 400
    except ValueError:
        return jsonify({"error": "Umur harus angka"}), 400

    user.nama = nama.strip()
    user.umur = umur
    user.alamat = alamat

    db.session.commit()

    return jsonify({
        "message": "User updated",
        "user": {
            "id": user.id,
            "nama": user.nama,
            "umur": user.umur,
            "alamat": user.alamat
        }
    }), 200
