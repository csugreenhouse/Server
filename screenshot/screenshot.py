import requests
from datetime import datetime
import time

CAMERA_IPs = ["192.168.0.56"]

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

while True:
    print(f"http://{CAMERA_IPs[0]}/")
    save_image(1,f"http://{CAMERA_IPs[0]}/capture","")
    time.sleep(60)