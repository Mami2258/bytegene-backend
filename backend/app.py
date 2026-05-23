// Bu kodu kullanıcının butona bastığı anı tetikleyen fonksiyonun içine yaz

// Kullanıcının girdiği veriyi alıyoruz (Örnek: input id'si "veriGirdisi" olsun)
const kullaniciVerisi = document.getElementById("veriGirdisi").value;

fetch('https://SENIN-RENDER-LINKIN.onrender.com/analiz', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ veri: kullaniciVerisi }) 
})
.then(response => response.json())
.then(data => {
    // Python'dan gelen sonucu HTML'deki bir yere yazdır (Örnek id: "sonucEkrani")
    document.getElementById("sonucEkrani").innerText = data.mesaj;
})
.catch(error => {
    console.error("Hata oluştu:", error);
});