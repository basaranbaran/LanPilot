# ✈️ LanPilot: Yerel Ağ Uzak Masaüstü Kontrolcüsü

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.7+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Flask-2.0+-green.svg" alt="Flask">
  <img src="https://img.shields.io/badge/Lisans-MIT-yellow.svg" alt="License">
  <br>
  <strong>Kablosuz • Hızlı • Kurulum Gerektirmez</strong>
</p>

<p align="center">
  LanPilot, bilgisayarınızı yerel ağ (Wi-Fi) üzerinden akıllı telefonunuzla tam kontrollü bir şekilde yönetmenizi sağlayan açık kaynaklı bir araçtır.
</p>

---

## 🎯 Projenin Amacı

Bilgisayar başında değilken (balkonda, mutfakta veya yatakta) bilgisayarınızı kontrol etme ihtiyacını çözmek için geliştirilmiştir. Piyasadaki TeamViewer/AnyDesk gibi çözümlerin aksine:
- **İnternet gerektirmez** (Tamamen yerel ağda çalışır).
- **Kurulum gerektirmez** (Sadece Python scriptini çalıştırmanız yeterlidir).
- **Düşük gecikme (Low Latency)** sunar (Oyun şampiyon seçim ekranları, medya kontrolü vb. için idealdir).

## ✨ Özellikler

- 📱 **Mobil Uyumlu Arayüz (PWA):** Telefonunuzda doğal bir uygulama gibi tam ekran çalışır.
- 🖱️ **Akıllı Tıklama Sistemi:** Telefon ekranı ile bilgisayar ekranı arasındaki oran farkını (aspect ratio) otomatik hesaplar, tıklamaları piksel hassasiyetinde iletir.
- ⚡ **Yüksek Performans:** `mss` kütüphanesi ile yüksek FPS'li ekran yakalama ve MJPEG yayını.
- ⌨️ **Klavye Desteği:** Metin yazma, Enter, Backspace ve Alt-Tab gibi özel tuş kombinasyonları.
- 🛡️ **Güvenli:** Verileriniz dış internete çıkmaz, her şey modeminiz içinde kalır.

## 🛠️ Kullanılan Teknolojiler

Bu proje full-stack bir yaklaşımla geliştirilmiştir:

| Alan | Teknoloji | Kullanım Amacı |
|------|-----------|----------------|
| **Backend** | Python, Flask | Web sunucusu ve API yönetimi |
| **Görüntü İşleme** | MSS, Pillow (PIL) | Ekran yakalama ve sıkıştırma |
| **Otomasyon** | PyAutoGUI | Fare ve klavye simülasyonu |
| **Frontend** | HTML5, CSS3, JS | Responsive arayüz ve touch event yönetimi |

## 🚀 Kurulum ve Kullanım

### 1. Projeyi Klonlayın
```bash
git clone https://github.com/kullaniciadiniz/lanpilot.git
cd lanpilot
```

### 2. Gereksinimleri Yükleyin
```bash
pip install -r requirements.txt
```

### 3. Uygulamayı Başlatın
```bash
python app.py
```

### 4. Bağlanın!
Bilgisayarınızın IP adresini terminalde göreceksiniz veya `ipconfig` (Windows) / `ifconfig` (Linux/Mac) ile öğrenebilirsiniz. Telefonunuzun tarayıcısını açın ve adrese gidin:

```
http://192.168.1.XX:5000
```

> **İpucu:** Tam ekran deneyimi için tarayıcı menüsünden **"Ana Ekrana Ekle"** seçeneğini kullanın.

## 📸 Ekran Görüntüleri

*(Buraya projenin çalışır haldeki ekran görüntülerini ekleyebilirsiniz)*

## 🤝 Katkıda Bulunma

Pull request'ler kabul edilir. Büyük değişiklikler için lütfen önce tartışma başlatın.

## 📝 Lisans

[MIT](https://choosealicense.com/licenses/mit/)
