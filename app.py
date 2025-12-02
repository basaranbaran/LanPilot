from flask import Flask, render_template, Response, request, jsonify
import mss
import pyautogui
import io
from PIL import Image

app = Flask(__name__)

# PyAutoGUI ayarları
pyautogui.FAILSAFE = False
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# --- ANA UYGULAMA KODLARI ---

def gen_frames():
    """Bilgisayar ekranını yakalayıp video akışı olarak yayınlar."""
    with mss.mss() as sct:
        monitor = {"top": 0, "left": 0, "width": SCREEN_WIDTH, "height": SCREEN_HEIGHT}
        while True:
            try:
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                new_width = int(SCREEN_WIDTH / 2)
                new_height = int(SCREEN_HEIGHT / 2)
                img = img.resize((new_width, new_height))
                frame_bytes = io.BytesIO()
                img.save(frame_bytes, format='JPEG', quality=40)
                frame = frame_bytes.getvalue()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                print(f"Yayın Hatası: {e}")
                pass

# --- URL Rotaları (Şifresiz) ---

@app.route('/')
def index():
    """
    DÜZELTME 1: Ana HTML sayfasını sunarken, tıklama doğruluğu için
    bilgisayarın ekran boyutlarını da gönderir.
    """
    return render_template(
        'index.html',
        pc_screen_width=SCREEN_WIDTH,
        pc_screen_height=SCREEN_HEIGHT
    )

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/click', methods=['POST'])
def click():
    """
    Fare tıklama işlemini gerçekleştirir.
    Önce tıklama yapılır, SONRA Alt tuşu bırakılır.
    Böylece Alt-Tab menüsünden seçim yapılabilir.
    """
    data = request.json
    x = int(data['x'] * SCREEN_WIDTH)
    y = int(data['y'] * SCREEN_HEIGHT)
    
    # 1. Önce fareyi hareket ettir ve tıkla
    pyautogui.moveTo(x, y)
    pyautogui.click()
    
    # 2. Sonra (varsa) basılı kalan Alt tuşunu bırak
    pyautogui.keyUp('alt')
    
    return jsonify({"status": "success"})

@app.route('/type', methods=['POST'])
def type_text():
    data = request.json
    text = data.get('text', '')
    if text:
        pyautogui.write(text, interval=0.05)
    return jsonify({"status": "success"})

@app.route('/key', methods=['POST'])
def press_key():
    data = request.json
    key = data.get('key', '')
    if key:
        pyautogui.press(key)
    return jsonify({"status": "success"})

@app.route('/alttab', methods=['POST'])
def alt_tab():
    try:
        # Alt-Tab menüsünün ekranda açık kalmasını sağlayan kod
        pyautogui.keyDown('alt')
        pyautogui.press('tab')
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)