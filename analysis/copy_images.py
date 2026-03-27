import os
import cv2
import numpy as np
from pathlib import Path

import sys
sys.path.append('/srv/samba/Server')

import plant_requests.height_request.height_request as hr
import plant_requests.utils.reference_tag_util as reference_tag_util
import plant_requests.utils.graph_util as gu
import database.database_util as database_util


def create_slideshow_of_plants(plant_id):

    file_path = f"/srv/samba/plants/image/by_plant/plant{plant_id}/"
    new_path = f"/var/www/html/plant{plant_id}"
    Path(new_path).mkdir(parents=True, exist_ok=True)
    #touch the folder to make sure it exists: 
    for i, image_name in enumerate(sorted(os.listdir(file_path))):
        if (image_name=="processed"):
            continue
        image = cv2.imread(file_path+image_name)
        cv2.imwrite(new_path+f"/{i}.jpg",image)


create_slideshow_of_plants(18)