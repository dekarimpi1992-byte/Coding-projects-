

 

try:
    import qrcode
except ImportError:
    print("Error: qrcode module not found. Install it using: pip install qrcode[pil]")
    exit()

url = input("Enter the URL: ").strip()
file_path = "C:\\Users\\amar\\Desktop\\qrcode.png"

qr = qrcode.QRCode()
qr.add_data(url)

img = qr.make_image()
img.save(file_path)

print("QR code was generated!")
