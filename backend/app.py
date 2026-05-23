from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

@app.route('/analiz', methods=['POST'])
def analiz_yap():
    gelen_veri = request.json
    sonuc = {"durum": "basarili", "mesaj": "Python kodlari sorunsuz calisiyor!"}
    return jsonify(sonuc)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
