import requests
from datetime import datetime
import time
import tempfile
# below i will import processing functions
import sys
sys.path.append('/srv/samba/Server')
import processing.height as ph
import database_interface.database_interface as db

"""
SAVER 
- functions to get and save images from the ESP32-CAMs
- saves images at a specified interval into respective directories
"""

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

def get_averages(iteration=5, delay_between_iterations_s=1):
    averages = []
    for i in range(iteration):
        file_path = save_image(1,f"http://{CAMERA_IPs[0]}/capture","/srv/samba/Server/image_getter/temp")
        estimated_height = ph.estimated_height(file_path,scale_units_m=.070,bias_correction_m=0.01)
        green_pixel = ph.get_heighest_green_pixel(file_path)
        averages.append((estimated_height, green_pixel))
        time.sleep(delay_between_iterations_s)
    #        in the averages list, delete any outliers of height that are more than 20% away from the median, and dletele the corresponding green pixel
    averages = sorted(averages, key=lambda x: x[0])
    median_index = len(averages) // 2
    median_height = averages[median_index][0]
    filtered_averages = [item for item in averages if abs(item[0] - median_height) / median_height <= 0.2]
    if not filtered_averages:
        raise ValueError("All height measurements were considered outliers.")
    avg_height = sum(item[0] for item in filtered_averages) / len(filtered_averages)
    avg_green_pixel_x = sum(item[1][0] for item in filtered_averages) / len(filtered_averages)
    avg_green_pixel_y = sum(item[1][1] for item in filtered_averages) / len(filtered_averages)
    avg_green_pixel = (int(avg_green_pixel_x), int(avg_green_pixel_y))
    return avg_height, avg_green_pixel      



#print("WARNING")
#print("MAKE SURE THAT THE CAMERA IS FACING THE PLAN PROPERLY")
#print("MAKE SURE THAT THE CAMERA HAS THE CORRECT SETTINGS ON THE WEBSITE")
'''
while True:
    file_path = save_image(1,f"http://{CAMERA_IPs[0]}/capture","/srv/samba/plants/image/test")
    print("Processing image for QR tags and height estimation...")
    try :
        print("QR TAG IS GOOD")
        scan_qrtags = ph.scan_qrtags(file_path)
        ph.plot_image(file_path, "image_getter/test.png", qr_list=scan_qrtags)
    except Exception as e:
        print("QR TAG TO FAR AWAY OR NOT DETECTED")
        print(f"Error scanning QR tags: {e}")
        continue
    time.sleep(1)
'''

while True:
    file_path = save_image(1,f"http://{CAMERA_IPs[0]}/capture","/srv/samba/plants/image/test")
    print("Processing image for QR tags and height estimation...")
    scan_qrtags = ph.scan_qrtags(file_path)
    scan_apriltags = ph.scan_apriltags(file_path)
    estimated_height, highest_green_pixel  = get_averages(iteration=5, delay_between_iterations_s=1)


    ph.plot_image(file_path, "image_getter/test.png", qr_list=scan_qrtags, april_list=scan_qrtags, estimated_height=estimated_height, heighest_green_pixel=highest_green_pixel)

    print(f"Qr tag data: {scan_qrtags[0]['data']}")
    print(f"Estimated height: {estimated_height} m")
    print("Storing height in database...")
    query = db.generate_query(estimated_height, 1)
    plant_id = 1
    print(f"Generated query: {query}")
    db.execute_query(query)
    print("Height stored successfully.")
    time.sleep(30)  # wait for 5 minutes before taking another image

