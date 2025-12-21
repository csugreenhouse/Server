import cv2
import numpy as np
import matplotlib.pyplot as plt
import warnings


def plot_image(image_path, out_path, qr_list=None, april_list=None, mask=None, heighest_green_pixel=None, estimated_height=None):
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"could not load image: {image_path}")    
    graph_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    fig, ax = plt.subplots()
    ax.imshow(graph_rgb)
    ax.axis('on')   
        
    if qr_list is not None:
        for qr in qr_list:
            corners = qr["corners"]
            tl = corners["top_left"]
            tr = corners["top_right"]
            br = corners["bottom_right"]
            bl = corners["bottom_left"]
            for corner, color in zip([tl, tr, br, bl], ['red', 'green', 'blue', 'yellow']):
                x, y = corner
                ax.add_patch(plt.Circle((x, y), 10, color=color, fill=True))
                #print(f"Plotted corner at ({x}, {y}) with color {color}")
            
    if april_list is not None:
        for april in april_list:
            corners = april["corners"]
            tl = corners["top_left"]
            tr = corners["top_right"]
            br = corners["bottom_right"]
            bl = corners["bottom_left"]
            for corner, color in zip([tl, tr, br, bl], ['red', 'green', 'blue', 'yellow']):
                x, y = corner
                ax.add_patch(plt.Circle((x, y), 10, color=color, fill=True))
                #print(f"Plotted corner at ({x}, {y}) with color {color}")
                
    if heighest_green_pixel is not None:    
        x, y = heighest_green_pixel
        ax.add_patch(plt.Circle((x, y), 5, color='blue', fill=True))
        #print(f"Plotted heighest green pixel at ({x}, {y}) with color blue")
    
    if estimated_height is not None:
        ax.set_title(f"Estimated Height: {100*estimated_height:.2f} cm")
            
    plt.savefig(str(out_path), bbox_inches="tight")
    plt.close(fig)