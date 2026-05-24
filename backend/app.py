import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from Bio.Blast import NCBIWWW, NCBIXML

# Render'da hata vermemesi için dotenv modülünü güvenli yüklüyoruz
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from google import genai
from google.genai import types

app = Flask(__name__)
# Hostinger'ın bu sunucuya veri göndermesine izin veriyoruz
CORS(app)

api_key = os.getenv("GOOGLE_API_KEY")
try:
    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        client = None
        print("Uyarı: GOOGLE_API_KEY bulunamadı!")
except Exception as e:
    client = None
    print(f"Kritik Hata: API Anahtarı yüklenemedi! {e}")

# --- GEN ANALİZ FONKSİYONU ---
def havuzda_gen_ara(fasta_sequence):
    organizmalar = [
        "Escherichia coli", "Mus musculus", "Arabidopsis thaliana",
        "Caenorhabditis elegans", "Drosophila melanogaster", "Saccharomyces cerevisiae"
    ]
    filtre_sorgusu = " OR ".join([f"{org}[ORGN]" for org in organizmalar])
    try:
        result_handle = NCBIWWW.qblast("blastn", "nt", fasta_sequence, entrez_query=filtre_sorgusu, short_query=True)
        blast_record = NCBIXML.read(result_handle)
        if not blast_record.alignments:
            return {"hata": "Maalesef, seçili organizma havuzunda bu diziye rastlanmadı."}
        bulunan_sonuclar = []
        for alignment in blast_record.alignments:
            organizma_adi = "Bilinmiyor"
            for org in organizmalar:
                if org in alignment.title:
                    organizma_adi = org
                    break
            ncbi_url = f"https://www.ncbi.nlm.nih.gov/nuccore/{alignment.accession}"
            for hsp in alignment.hsps:
                bulunan_sonuclar.append({
                    "organizma": organizma_adi,
                    "gen_tanimi": alignment.title[:65] + "...",
                    "ncbi_url": ncbi_url,
                    "eslesme_skoru": hsp.score,
                    "e_degeri": hsp.expect,
                    "kimlik_orani": round((hsp.identities / hsp.align_length) * 100, 2)
                })
        return {"sonuclar": bulunan_sonuclar}
    except Exception as e:
        return {"hata": str(e)}

# --- SADECE ARKA PLAN (API) ROTALARI ---

@app.route("/analiz", methods=["POST"])
def analyze():
    gene_sequence = request.form.get("gene", "").strip().upper()
    if not gene_sequence:
        return render_template("results.html", dizi="GİRİLMEDİ", veri={"hata": "Lütfen bir gen dizisi girin."})
    
    analiz_verisi = havuzda_gen_ara(gene_sequence)
    return render_template("results.html", dizi=gene_sequence, veri=analiz_verisi)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    if not user_message:
        return jsonify({"reply": "Lütfen bir mesaj yazın."})
    if not client:
        return jsonify({"reply": "Sistem Hatası: GOOGLE_API_KEY bulunamadı veya geçersiz!"})
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction="Sen Byte&Gene platformunun asistanı ByteBot'sun. Biyoloji ve genetik hakkında kısa, profesyonel ama arkadaş canlısı cevaplar ver.",
                temperature=0.7,
            )
        )
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": f"Google Gemini API Hatası: {str(e)}"})

if __name__ == "__main__":
    # Render'ın verdiği portu dinamik olarak dinliyoruz
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
