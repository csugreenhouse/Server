import apriltag
import argparse
import cv2
import matplotlib.pyplot as plt

def scan_apriltag(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"could not load image: {image_path}")

    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    options = apriltag.DetectorOptions(families="tag25h9")
    detector = apriltag.Detector(options)
    results = detector.detect(gray)
    
    DECISION_MARGIN = 40 # THIS ALLOWS FOR THE 

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
    

    return {
        "tag_id": tag[1],
        "decision_margin": tag[4],
        "center": tag[6],
        "tag_corners": tag[7]
    }

def plot_image(image_path, out_path="processing/test/images/output.png"):
    image = cv2.imread(image_path)
    try:
        apriltag = scan_apriltag(image_path)
    except ValueError as e:
        print(f"Apriltag detection failed: {e}")
        return
    for key in ["blp", "brp", "trp", "tlp"]:
        x, y = res[key]
        ax.add_patch(plt.Circle((x, y), 50, color='purple', fill=True))
    graph_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    fig, ax = plt.subplots()
    ax.imshow(graph_rgb)
    ax.axis('on')
    plt.savefig(out_path, bbox_inches="tight")
    plt.close(fig)

    



