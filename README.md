# ✈️ LanPilot: Local Network Remote Desktop

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.7+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Flask-2.0+-green.svg" alt="Flask">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <br>
  <strong>Wireless • Low Latency • No Installation</strong>
</p>

[English](#english) | [Türkçe](#türkçe)

---

<a name="english"></a>
## 🇺🇸 English

**LanPilot** is an open-source tool that allows you to fully control your computer via your smartphone over a local network (Wi-Fi).

### 🎯 Purpose
Developed to solve the need to control your PC when you are away from the keyboard (in the kitchen, balcony, or bed). Unlike TeamViewer/AnyDesk:
- **No Internet Required:** Works entirely on your local network.
- **No Installation:** Just run the Python script.
- **Low Latency:** Optimized for gaming (champion selection etc.) and media control.

### ✨ Features
- 📱 **PWA Support:** Works like a native app on your phone.
- 🖱️ **Pixel-Perfect Control:** Automatically calculates aspect ratio for accurate clicking.
- ⚡ **High Performance:** Uses `mss` for fast screen capture and MJPEG streaming.
- ⌨️ **Keyboard Support:** Type text, press Enter, Backspace, and Alt-Tab.
- 🛡️ **Secure:** Data stays within your local network.

### 🚀 Setup

1. **Clone the Repo:**
   ```bash
   git clone https://github.com/basaranbaran/lanpilot.git
   cd lanpilot
   ```

2. **Install Requirements:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run:**
   ```bash
   python app.py
   ```

4. **Connect:**
   Open your phone's browser and go to `http://YOUR_PC_IP:5000` (e.g., `192.168.1.20:5000`).

---

<a name="türkçe"></a>
## 🇹🇷 Türkçe

**LanPilot**, bilgisayarınızı yerel ağ (Wi-Fi) üzerinden akıllı telefonunuzla tam kontrollü bir şekilde yönetmenizi sağlayan açık kaynaklı bir araçtır.

### 🎯 Projenin Amacı
Bilgisayar başında değilken (balkonda, mutfakta veya yatakta) bilgisayarınızı kontrol etme ihtiyacını çözmek için geliştirilmiştir. TeamViewer/AnyDesk gibi çözümlerin aksine:
- **İnternet Gerektirmez:** Tamamen yerel ağda çalışır.
- **Kurulum Gerektirmez:** Sadece Python scriptini çalıştırmanız yeterlidir.
- **Düşük Gecikme (Low Latency):** Oyun şampiyon seçim ekranları ve medya kontrolü için idealdir.

### ✨ Özellikler
- 📱 **Mobil Uyumlu Arayüz (PWA):** Telefonunuzda doğal bir uygulama gibi çalışır.
- 🖱️ **Akıllı Tıklama Sistemi:** Telefon ekranı ile bilgisayar ekranı arasındaki oran farkını otomatik hesaplar, tıklamaları piksel hassasiyetinde iletir.
- ⚡ **Yüksek Performans:** `mss` kütüphanesi ile yüksek FPS'li ekran yakalama.
- ⌨️ **Klavye Desteği:** Metin yazma, Enter, Backspace ve Alt-Tab.
- 🛡️ **Güvenli:** Verileriniz dış internete çıkmaz.

### 🚀 Kurulum

1. **Projeyi İndirin:**
   ```bash
   git clone https://github.com/basaranbaran/lanpilot.git
   cd lanpilot
   ```

2. **Gereksinimleri Yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Uygulamayı Başlatın:**
   ```bash
   python app.py
   ```

4. **Bağlanın:**
   Telefonunuzun tarayıcısından `http://BILGISAYAR_IP_ADRESI:5000` adresine gidin (Örn: `192.168.1.20:5000`).

---

## 📝 License / Lisans

[MIT](https://choosealicense.com/licenses/mit/)
