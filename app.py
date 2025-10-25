# import library

from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS

# inisiasi object flask

app = Flask(__name__)

# inisiasi object flask_restful

api = Api(app)

# inisiasi object flask_cors

CORS(app)
# inisiasi variable kosong bertipe dictionary
identitas = {} # variable global , dictionary = json

# Membuat class resource
class ContohResource(Resource):
    # membuat methode get dan post
    def get(self):

        return identitas
    def post(self):
        nama = request.form["nama"]
        umur = request.form["umur"]
        identitas["nama"] = nama
        identitas["umur"] = umur
        responce = {"msg": "Data berhasil di masukkan"}
        return responce
    
# setup resourcenya
api.add_resource(ContohResource, "/api", methods=["GET", "POST"])

if __name__=="__main__":
    app.run(debug=True, port=5005)