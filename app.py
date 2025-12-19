from flask import Flask, render_template, Response, request, jsonify
import mss
import pyautogui
import io
import socket
from PIL import Image

app = Flask(__name__)

pyautogui.FAILSAFE = False
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

def get_ip_addresses():
    """Retrieves all IPv4 addresses associated with the host."""
    ip_list = []
    tailscale_ips = []
    local_ips = []
    try:
        hostname = socket.gethostname()
        _, _, ips = socket.gethostbyname_ex(hostname)
        for ip in ips:
            if not ip.startswith("127."):
                ip_list.append(ip)
                # Tailscale IPs start with 100.x.x.x
                if ip.startswith("100."):
                    tailscale_ips.append(ip)
                else:
                    local_ips.append(ip)
    except Exception as e:
        print(f"Error getting IPs: {e}")
    return ip_list, tailscale_ips, local_ips

def gen_frames():
    """Captures the screen and streams it as video."""
    with mss.mss() as sct:
        monitor = {"top": 0, "left": 0, "width": SCREEN_WIDTH, "height": SCREEN_HEIGHT}
        while True:
            try:
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                new_width = int(SCREEN_WIDTH * 0.75)
                new_height = int(SCREEN_HEIGHT * 0.75)
                img = img.resize((new_width, new_height))
                frame_bytes = io.BytesIO()
                img.save(frame_bytes, format='JPEG', quality=70)
                frame = frame_bytes.getvalue()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                print(f"Stream Error: {e}")
                pass

@app.route('/')
def index():
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
    data = request.json
    x = int(data['x'] * SCREEN_WIDTH)
    y = int(data['y'] * SCREEN_HEIGHT)
    
    pyautogui.moveTo(x, y)
    pyautogui.click()
    
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
    """Opens Alt-Tab menu and keeps Alt key pressed."""
    try:
        pyautogui.keyDown('alt')
        pyautogui.press('tab')
        # Keep Alt key pressed - don't release it
        return jsonify({"status": "success", "message": "Alt-Tab menu opened"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/alttab_tab', methods=['POST'])
def alt_tab_navigate():
    """Presses Tab while Alt is held to navigate through windows."""
    try:
        pyautogui.press('tab')
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/alttab_release', methods=['POST'])
def alt_tab_release():
    """Releases Alt key to select the current window."""
    try:
        pyautogui.keyUp('alt')
        return jsonify({"status": "success", "message": "Window selected"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 LanPilot is Launching!")
    print("="*50 + "\n")
    
    ips, tailscale_ips, local_ips = get_ip_addresses()
    
    if not ips:
        print("⚠️  No network interface found! You might only be able to connect via localhost.")
    else:
        # Show Tailscale IPs first (if available) for remote access
        if tailscale_ips:
            print("🌍 Tailscale VPN (Remote Access):")
            for ip in tailscale_ips:
                print(f"   🔒 http://{ip}:5000")
            print()
        
        # Show local network IPs
        if local_ips:
            print("📱 Local Network (Same WiFi):")
            for ip in local_ips:
                print(f"   👉 http://{ip}:5000")
            print()
            
    print("   💻 Local access: http://127.0.0.1:5000")
    print("="*50 + "\n")

    app.run(host='0.0.0.0', port=5000, threaded=True)
