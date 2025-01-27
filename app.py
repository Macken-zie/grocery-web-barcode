import cv2
from flask import Flask, render_template, request, jsonify
import qrcode
import io
import base64

app = Flask(__name__)

# Route for the homepage
@app.route('/')
def home():
    return render_template('index.html')

# Route to generate a QR code
@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    data = request.json.get('data')
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Generate the QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)

    # Save QR code as an image
    img = qr.make_image(fill="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return jsonify({"qr_code": f"data:image/png;base64,{img_base64}"}), 200

# Route to scan a QR code
@app.route('/scan_qr', methods=['POST'])
def scan_qr():
    # Access the webcam and scan QR codes
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()
    scanned_data = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect and decode QR codes in the frame
        data, bbox, _ = detector.detectAndDecode(frame)
        if data:
            scanned_data = data
            break

        # Show the video feed with OpenCV
        cv2.imshow("QR Code Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if scanned_data:
        return jsonify({"data": scanned_data}), 200
    else:
        return jsonify({"error": "No QR code detected"}), 400

if __name__ == '__main__':
    app.run(debug=True)


