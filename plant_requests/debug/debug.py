import cv2
import numpy as np
import matplotlib.pyplot as plt
import warnings

def plot_image(image, out_path, qr_list=None, april_list=None, green_blob_list=None, heighest_green_pixel=None, estimated_height=None):
    graph_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    W,H = graph_rgb.shape[1], graph_rgb.shape[0]
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
            ax.add_patch(plt.Polygon([tl, tr, br, bl], fill=None, edgecolor='cyan', linewidth=2))
            cx, cy = qr["center"]
            ax.add_patch(plt.Circle((cx, cy), 5, color='cyan', fill=True)) 
    if april_list is not None:
        for april in april_list:
            corners = april["corners"]
            tl = corners["top_left"]
            tr = corners["top_right"]
            br = corners["bottom_right"]
            bl = corners["bottom_left"]
            ax.add_patch(plt.Polygon([tl, tr, br, bl], fill=None, edgecolor='magenta', linewidth=2))
            #add dot at center
            cx, cy = april["center"]
            ax.add_patch(plt.Circle((cx, cy), 5, color='magenta', fill=True))
            #print(f"Plotted AprilTag center at ({cx}, {cy}) with color cyan")

    if green_blob_list is not None:
        for green_blob in green_blob_list:
            mask = green_blob["mask"]
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                contour = contour.squeeze()
                ax.plot(contour[:, 0], contour[:, 1], color='lime', linewidth=2)
        
            #print(f"Plotted plant contour with {len(contour)} points")
    if heighest_green_pixel is not None:    
        x, y = heighest_green_pixel
        ax.add_patch(plt.Circle((x, y), 5, color='blue', fill=True))
        #print(f"Plotted heighest green pixel at ({x}, {y}) with color blue")
    
    if estimated_height is not None:
        ax.set_title(f"Estimated Height: {100*estimated_height:.2f} cm")

    #plot from a sideview, what the camera sees should look like a cone
    
            
    plt.savefig(str(out_path), bbox_inches="tight")
    plt.close(fig)

def plot_image_dimensions(image, out_path, reference):
    fig, ax = plt.subplots()
    ax.imshow(image)
    ax.axis('on')
    displacement = reference['displacements']['d']
    displacement_z = reference['displacements']['z']
    displacement_x = reference['displacements']['x']
    displacement_y = reference['displacements']['y']
    #draw line between center of image and center of reference
    center_x_image = image.shape[1] / 2
    center_y_image = image.shape[0] / 2
    center_x_ref = reference['center'][0]
    center_y_ref = reference['center'][1]
    ax.plot([center_x_image, center_x_ref], [center_y_image, center_y_ref], color='red', linewidth=2)
    #add horizontal line and label for displacement_x on side of image
    ax.plot([center_x_image, center_x_ref], [center_y_ref, center_y_ref], color='green', linewidth=2)
    ax.plot([center_x_ref, center_x_ref], [center_y_image, center_y_ref], color='blue', linewidth=2)
    #create a legend
    ax.plot([], [], color='red', label='Depth Displacement(z)\n %.6f cm' % (displacement_z*100))
    ax.plot([], [], color='green', label='Horizontal Displacement (x)\n %.6f cm' % (displacement_x*100))
    ax.plot([], [], color='blue', label='Vertical Displacement (y)\n %.6f cm' % (displacement_y*100))
    ax.legend(loc='upper right')

    # set title with displacement z
    ax.set_title(f'Distance to QR Code (d): {displacement*100:.6f} cm')
    plt.savefig(str(out_path), bbox_inches="tight")
    plt.close(fig)

    
    