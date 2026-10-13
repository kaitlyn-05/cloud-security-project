import qrcode

# Data to encode
data = "http://138.47.154.232:8000/sudo"

# Create QR code instance
qr = qrcode.QRCode(
    version=1,  # Control the size of the QR code
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

qr.add_data(data)
qr.make(fit=True)

# Create an image from the QR Code instance
img = qr.make_image(fill="black", back_color="white")

# Save or display the QR code
img.save("qrcode.png")
img.show()