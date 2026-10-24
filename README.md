# ✈️ LanPilot: Local Network Remote Desktop

<p align="center">
  <a href="https://github.com/basaranbaran/LanPilot/actions/workflows/ci.yml"><img src="https://github.com/basaranbaran/LanPilot/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/Version-2.1-brightgreen.svg" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Flask-2.0+-green.svg" alt="Flask">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"></a>
  <br>
  <strong>Wireless • Low Latency • Tailscale VPN Support</strong>
</p>

[English](#english) | [Türkçe](#türkçe)

---

<a name="english"></a>
## 🇺🇸 English

**LanPilot** is an open-source tool that allows you to fully control your computer via your smartphone over a local network (Wi-Fi) or through Tailscale VPN.


### 🎯 The Story Behind LanPilot


Sometimes the best projects are born from necessity (or a bit of laziness). LanPilot started when I wanted to control my PC from the kitchen without walking back to my desk. Existing tools like TeamViewer were too heavy for such a simple task and required internet. So, I decided to build my own lightweight solution running entirely on the local network.

As demonstrated in the [demo video](https://github.com/basaranbaran/LanPilot/releases/download/v2.1.0/sample-video.mp4), I tested it by picking a League of Legends champion. Yes, sometimes you develop software just so you don't miss your pick during the draft phase while grabbing a snack 😁




### 🎯 Purpose


Developed to solve the need to control your PC when you are away from the keyboard (in the kitchen, balcony, or bed). Unlike TeamViewer/AnyDesk:

- **No Internet Required (Local Mode):** Works entirely on your local network.
- **Global Access (Tailscale Mode):** Control from anywhere using Tailscale VPN without port forwarding.
- **No Installation:** Just run the Python script.
- **High Quality:** 75% resolution scaling with high-quality streaming for clear visuals.
- **Low Latency:** Optimized for instant reactions, fast enough even for gaming menus.


### ✨ Features


The most exciting technical details that make this project special:

- 🖱️ **Aspect Ratio Mapping:** The most challenging part of the project. Mathematically calculates the aspect ratio difference between your phone and monitor to ensure pixel-perfect clicking accuracy. This ensures that when you tap on your phone screen, the click lands exactly where you intended on your PC screen, regardless of screen size differences.

- ⚡ **Low Latency:** Optimized for instant reactions, fast enough even for time-sensitive tasks like gaming champion selection. Uses `mss` library for high-performance screen capture and MJPEG streaming.

- 📱 **PWA Support:** Works like a native app on your phone. Add it to your home screen for quick access.

- ⌨️ **Keyboard Support:** Type text, press Enter, Backspace, and Alt-Tab for full control.

- 🛡️ **Security & Privacy:** 
  - **PIN Login:** Nothing is reachable without a PIN. A random 6-digit PIN is printed in the terminal on every start (or set your own with `LANPILOT_PIN`). Wrong guesses are rate-limited and locked out.
  - **Local Network Mode:** Data never leaves your local network (Localhost/WiFi). Traffic is plain HTTP there, so use a network you trust.
  - **Tailscale VPN Mode:** When using Tailscale, data travels through an encrypted private network. Only devices logged into your account can access.
  - **Restricted Input:** Typed text is capped, and only a short list of keys can be pressed from the phone.
  - See [SECURITY.md](SECURITY.md) for the full threat model and how to report a vulnerability.


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
   Open your phone's browser and go to `http://YOUR_PC_IP:5000` (e.g., `192.168.1.20:5000`), then enter the **PIN** printed in the terminal.
   > 💡 **Tip:** The app will automatically detect and display all available connection URLs when it starts, including Tailscale VPN IPs (if installed) and local network IPs.

**Options:**

| What | How |
|------|-----|
| Keep the same PIN between runs | `LANPILOT_PIN=my-secret-pin python app.py` (at least 6 characters) |
| Listen on one interface only | `python app.py --host 100.x.y.z` (e.g. your Tailscale IP) |
| Use another port | `python app.py --port 8080` |


### 📱 How to Connect (Remote Control)


#### 🏠 Local Network (Same WiFi)

1. Ensure your phone and PC are connected to the same WiFi router.
2. Run `python app.py`.
3. Enter the **Network** URL shown in the terminal into your phone's browser.

#### 🌍 Global Access (Tailscale & VPN)

Controls your PC from anywhere (4G, Office, Vacation) without port forwarding.

**Step-by-Step Setup:**

1.  **Install:**
    *   **PC:** Download [Tailscale for Windows](https://tailscale.com/download/windows).
    *   **Phone:** Download Tailscale from App Store / Google Play.
2.  **Login:** Open Tailscale on both devices and log in with the **same** Google/Microsoft account.
3.  **Verify:** You should see your computer's name in the "Machines" list on your phone.
4.  **Run:** Start LanPilot (`python app.py`).
5.  **Connect:** The app will automatically detect and display your secure **Tailscale IP** (starts with `100.x`) with a 🔒 icon. Use that link on your phone to connect from anywhere in the world.

> **🔒 Security Note:** Tailscale creates a private encrypted network. Only devices logged into **your** account can access this IP. Strangers cannot connect, and the PIN adds a second layer.


### 🛠️ Technical Details


#### Architecture

- **Backend:** Flask (Python) with MJPEG streaming
- **Screen Capture:** `mss` library for high-performance screen grabbing
- **Input Control:** `PyAutoGUI` for mouse and keyboard simulation
- **Frontend:** Vanilla JavaScript with PWA support
- **Network:** Supports both local network (WiFi) and Tailscale VPN (100.x.x.x IP range)


#### Key Algorithms


**Aspect Ratio Mapping:**

The core challenge was ensuring pixel-perfect clicking accuracy when the phone and PC have different aspect ratios. The algorithm:

1. Calculates the PC screen aspect ratio
2. Calculates the phone screen/container aspect ratio
3. Determines how the PC screen is rendered (letterboxed or pillarboxed)
4. Maps touch coordinates to the correct relative position on the PC screen
5. Converts relative coordinates to absolute pixel coordinates

This ensures that tapping anywhere on your phone screen results in an accurate click on the corresponding location on your PC screen.


### 🧪 Development

The web layer talks to the desktop through a small `Controller` interface, so the tests use a fake one and never move your real mouse.

```bash
pip install -r requirements-dev.txt
python -m pytest
```

CI runs the same tests on Python 3.9 and 3.12 for every push and pull request.


### 🙏 Acknowledgments


Special thanks to [Mert Okuyaz](https://www.linkedin.com/in/mert-okuyaz-6a18b1147/) for suggesting Tailscale VPN integration, which made this project accessible from anywhere in the world! 🌍

---

<a name="türkçe"></a>
## 🇹🇷 Türkçe

**LanPilot**, bilgisayarınızı yerel ağ (Wi-Fi) veya Tailscale VPN üzerinden akıllı telefonunuzla tam kontrollü bir şekilde yönetmenizi sağlayan açık kaynaklı bir araçtır.


### 🎯 LanPilot'un Hikayesi


Bazen en iyi projeler kendi ihtiyacımdan veya "tembelliğimizden" doğar derler. LanPilot tam da böyle başladı. 🚀

Bilgisayar başından kalkıp mutfağa gittiğimde, arka plandaki işlemleri kontrol etmek için tekrar odaya dönmek zor geliyordu. TeamViewer gibi uygulamalar hem internet gerektiriyor hem de bu basit ihtiyaç için hantal kalıyordu. Ben de "Neden kendi hafif (lightweight) çözümümü yazmıyorum?" dedim ve ortaya yerel ağ üzerinden çalışan bu aracı çıkardım.

[Demo videoda](https://github.com/basaranbaran/LanPilot/releases/download/v2.1.0/sample-video.mp4) göreceğiniz üzere sistemi League of Legends karakter seçim ekranında test ettim. Evet, bazen sırf şampiyon seçimini mutfaktan yapabilmek ve sırayı kaçırmamak için bile yazılım geliştirebiliyorsunuz 😁


### 🎯 Projenin Amacı


Bilgisayar başında değilken (balkonda, mutfakta veya yatakta) bilgisayarınızı kontrol etme ihtiyacını çözmek için geliştirilmiştir. TeamViewer/AnyDesk gibi çözümlerin aksine:

- **İnternet Gerektirmez (Yerel Mod):** Tamamen yerel ağda çalışır.
- **Küresel Erişim (Tailscale Modu):** Port açma derdi olmadan, Tailscale VPN ile dünyanın her yerinden erişim.
- **Kurulum Gerektirmez:** Sadece Python scriptini çalıştırmanız yeterlidir.
- **Yüksek Kalite:** %75 çözünürlük ölçekleme ve yüksek kalite ile net görüntü.
- **Düşük Gecikme (Low Latency):** Anlık tepki gerektiren işleri bile telefondan yapabilecek kadar seri çalışıyor.


### ✨ Özellikler


İşin mutfağında beni en çok heyecanlandıran detaylar:

- 🖱️ **Aspect Ratio Mapping (En-Boy Oranı Eşleştirme):** Projenin en zorlu kısmıydı. Telefon ve monitör arasındaki en-boy oranı farkını matematiksel olarak hesaplayıp piksel hassasiyetinde tıklama sağlıyor. Bu sayede telefon ekranınızda dokunduğunuz nokta, bilgisayar ekranında tam olarak istediğiniz yere denk geliyor.

- ⚡ **Low Latency (Düşük Gecikme):** Anlık tepki gerektiren işleri bile telefondan yapabilecek kadar seri çalışıyor. `mss` kütüphanesi ile yüksek performanslı ekran yakalama ve MJPEG streaming kullanılıyor.

- 📱 **Mobil Uyumlu Arayüz (PWA):** Telefonunuzda doğal bir uygulama gibi çalışır. Ana ekrana ekleyerek hızlı erişim sağlayabilirsiniz.

- ⌨️ **Klavye Desteği:** Metin yazma, Enter, Backspace ve Alt-Tab ile tam kontrol.

- 🛡️ **Güvenlik & Gizlilik:**
  - **PIN ile Giriş:** PIN olmadan hiçbir şeye erişilemez. Her başlangıçta terminalde rastgele 6 haneli bir PIN yazılır (kendi PIN'inizi `LANPILOT_PIN` ile belirleyebilirsiniz). Yanlış denemeler sınırlandırılır ve kilitlenir.
  - **Yerel Ağ Modu:** Verileriniz dış internete çıkmaz, tamamen yerel ağda (Localhost/WiFi) döner. Bu modda trafik düz HTTP'dir, bu yüzden güvendiğiniz bir ağ kullanın.
  - **Tailscale VPN Modu:** Tailscale kullanırken veriler şifreli özel ağ üzerinden iletilir. Sadece sizin hesabınızla giriş yapılmış cihazlar erişebilir.
  - **Kısıtlı Girdi:** Yazılan metin sınırlıdır ve telefondan yalnızca kısa bir tuş listesine basılabilir.
  - Tehdit modelinin tamamı ve açık bildirme yöntemi için [SECURITY.md](SECURITY.md) dosyasına bakın.


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
   Telefonunuzun tarayıcısından `http://BILGISAYAR_IP_ADRESI:5000` adresine gidin (Örn: `192.168.1.20:5000`) ve terminalde yazan **PIN**'i girin.
   > İpucu: Uygulama başladığında kullanabileceğiniz tüm adresleri ekrana yazdırır.

**Seçenekler:**

| Ne | Nasıl |
|----|-------|
| PIN'i her çalıştırmada aynı tutmak | `LANPILOT_PIN=gizli-pin python app.py` (en az 6 karakter) |
| Yalnızca tek bir arayüzü dinlemek | `python app.py --host 100.x.y.z` (örn. Tailscale IP'niz) |
| Başka bir port kullanmak | `python app.py --port 8080` |


### 📱 Nasıl Bağlanılır?


#### 🏠 Aynı Evde (WiFi)

1. Telefonunuzun ve bilgisayarınızın aynı modeme bağlı olduğundan emin olun.
2. `python app.py` komutunu çalıştırın.
3. Uygulama ekranında çıkan **Network** adresini (örn: `192.168.1.25:5000`) telefon tarayıcısına yazın.

#### 🌍 Ev Dışından Erişim (Tailscale & 4G)

Port açma derdi olmadan, marketten veya başka bir şehirden bilgisayarınızı yönetin.

**Adım Adım Kurulum:**

1.  **İndir:**
    *   **PC:** [Windows için Tailscale](https://tailscale.com/download/windows) indirin ve kurun.
    *   **Telefon:** App Store veya Play Store'dan Tailscale uygulamasını indirin.
2.  **Giriş:** Her iki cihazda da **aynı** Google/Microsoft hesabı ile giriş yapın.
3.  **Kontrol:** Telefonda "Machines" listesinde bilgisayarınızın adını (örn: `baran-pc`) gördüğünüzden emin olun.
4.  **Başlat:** LanPilot'u çalıştırın (`python app.py`).
5.  **Bağlan:** Uygulama güvenli **Tailscale IP** adresinizi ( `100.x` ile başlar) 🔒 ikonu ile otomatik gösterir. Dünyanın her yerinden o adrese girerek bağlanabilirsiniz.

> **🔒 Güvenlik Notu:** Tailscale size özel şifreli bir ağ kurar. Sadece **sizin** hesabınızla giriş yapılmış cihazlar bu IP'ye erişebilir. Başkası giremez, PIN ise ikinci bir katman ekler.


### 🛠️ Teknik Detaylar


#### Mimari

- **Backend:** Flask (Python) ile MJPEG streaming
- **Ekran Yakalama:** Yüksek performanslı ekran yakalama için `mss` kütüphanesi
- **Giriş Kontrolü:** Fare ve klavye simülasyonu için `PyAutoGUI`
- **Frontend:** PWA desteği ile Vanilla JavaScript
- **Ağ:** Hem yerel ağ (WiFi) hem de Tailscale VPN (100.x.x.x IP aralığı) desteği


#### Ana Algoritmalar


**Aspect Ratio Mapping (En-Boy Oranı Eşleştirme):**

Piksel hassasiyetinde tıklama doğruluğu sağlamak, telefon ve PC'nin farklı en-boy oranlarına sahip olması durumunda projenin en zorlu kısmıydı. Algoritma:

1. PC ekran en-boy oranını hesaplar
2. Telefon ekranı/kapsayıcı en-boy oranını hesaplar
3. PC ekranının nasıl render edildiğini belirler (letterboxed veya pillarboxed)
4. Dokunma koordinatlarını PC ekranındaki doğru göreceli konuma eşler
5. Göreceli koordinatları mutlak piksel koordinatlarına dönüştürür

Bu sayede telefon ekranınızda herhangi bir yere dokunduğunuzda, PC ekranınızda karşılık gelen konuma doğru bir tıklama yapılır.


### 🧪 Geliştirme

Web katmanı masaüstü ile küçük bir `Controller` arayüzü üzerinden konuşur. Testler sahte bir controller kullanır, gerçek farenizi hareket ettirmez.

```bash
pip install -r requirements-dev.txt
python -m pytest
```

CI, her push ve pull request'te aynı testleri Python 3.9 ve 3.12 üzerinde çalıştırır.


### 🙏 Teşekkürler


Tailscale VPN entegrasyonunu önerdiği için [Mert Okuyaz](https://www.linkedin.com/in/mert-okuyaz-6a18b1147/)'a özel teşekkürler! Bu öneri sayesinde proje dünyanın her yerinden erişilebilir hale geldi! 🌍
