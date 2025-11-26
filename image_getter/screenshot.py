import requests
from datetime import datetime
import time
import processing.height as ph



def save_image(camera_num, url,image_dir):
    print(url)
    try:
        response = requests.get(url,timeout=10)
        response.raise_for_status()
        filename = datetime.now().strftime(f"{image_dir}/esp32_{camera_num}_cam_%Y%m%d_%H%M%S.jpg")
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Image sucessfully saved as {filename}")
    except requests.exceptions.RequestException as e:
        print(f"failed to get image: {e}")
    return filename

CAMERA_IPs = [
    "192.168.0.56"
]



file_path = save_image(1,f"http://{CAMERA_IPs[0]}/capture","/srv/samba/plants/image/test")

print("Processing image for QR tags and height estimation...")

scan_qrtags = ph.scan_qrtags(file_path)
estimated_height = ph.estimated_height(file_path,scale_units_m=.070,bias_correction_m=0.01)


print(f"Qr tag data: {scan_qrtags[0]['data']}")
print(f"Estimated height: {estimated_height} m")









while True:
    print(f"http://{CAMERA_IPs[0]}/")
    save_image(1,f"http://{CAMERA_IPs[0]}/capture","/srv/samba/plants/image/test")
    time.sleep(60)