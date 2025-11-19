import apriltag
import argparse
import cv2
import matplotlib.pyplot as plt
from pathlib import Path
from ultralytics import YOLO
def scan_apriltag(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"could not load image: {image_path}")

    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    options = apriltag.DetectorOptions(families="tag25h9")
    detector = apriltag.Detector(options)
    results = detector.detect(gray)
    
    DECISION_MARGIN = 40

    valid_april_tags = []

    tag = None

    for r in results:
        print(r[1])
        print(f"TAG ID {r.tag_id} with decision margin {r.decision_margin}")

        if (r.decision_margin>DECISION_MARGIN):
            tag = r
            valid_april_tags.append(apriltag)

    if (len(valid_april_tags)==0):
        if (len(results)!=0):
            raise ValueError(f"No Valid april tag has been detected, but a non valid one has been found")
        else:
            raise ValueError(f"No april tags at all have been found")
        
    if (len(valid_april_tags)>1):
        raise ValueError(f"More then one valid tag has been detected")
    
    top_left, top_right, bottom_right, bottom_left = tag.corners

    return {
        "tag_id": tag.tag_id,
        "decision_margin": tag.decision_margin,
        "center": tuple(tag.center),
        "corners": {
            "top_left": tuple(top_left),
            "top_right": tuple(top_right),
            "bottom_right": tuple(bottom_right),
            "bottom_left": tuple(bottom_left),
        }
}

def plot_image(image_path, out_path):
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"could not load image: {image_path}")    
    graph_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    tag_info = scan_apriltag(image_path)
    
    corners = tag_info["corners"]
    tl = corners["top_left"]
    tr = corners["top_right"]
    br = corners["bottom_right"]
    bl = corners["bottom_left"]
    
    fig, ax = plt.subplots()
    ax.imshow(graph_rgb)
    ax.axis('on')
    
    for corner, color in zip([tl, tr, br, bl], ['red', 'green', 'blue', 'yellow']):
        x, y = corner
        ax.add_patch(plt.Circle((x, y), 10, color=color, fill=True))
        print(f"Plotted corner at ({x}, {y}) with color {color}")
    
    plant_info = find_plant(image_path)
    
    plt.savefig(str(out_path), bbox_inches="tight")
    plt.close(fig)

def find_plant(image_path):
    model = YOLO("yolov8n.pt")
    results = model.predict(source=image_path, conf=0.25, save=False, save_txt=False)
    for box in results[0].boxes:
        x1, y1, x2, y2 = box.xyxy[0]
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        print(f"Detected class {cls} with confidence {conf:.2f} at [{x1}, {y1}, {x2}, {y2}]")
        return {x1, y1, x2, y2}
    return False
    