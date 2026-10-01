import qrcode

asset_code = "EW-001"

laptop_ip = "10.187.185.235"

url = f"http://{laptop_ip}:8000/ewaste/{asset_code}"

qr = qrcode.make(url)

qr.save(f"{asset_code}.png")

print(f"QR generated for {asset_code}")
print(f"QR URL: {url}")
