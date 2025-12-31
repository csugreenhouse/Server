import cv2
import numpy as np
import matplotlib.pyplot as plt
import warnings

def get_equation_of_line(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    if x2 - x1 == 0:
        m = float('inf')
        b = x1
    else:
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1
    return m, b


def plot_camera_view_frustum(ax, heighest_green_pixel,camera_parameters, reference_tag, color='yellow'):
    width = camera_parameters["width"]
    height = camera_parameters["height"]
    fx = (camera_parameters["focal_length_mm"] / camera_parameters["sensor_width_mm"]) * width
    fy = (camera_parameters["focal_length_mm"] / camera_parameters["sensor_height_mm"]) * height
    displacement_z = reference_tag['displacements']['z']
    displacement_x = reference_tag['displacements']['x']
    displacement_y = reference_tag['displacements']['y']
    # find the difference between the x cordinate of the tallest pixel and the x cordinate of the center of the reference tag
    difference_x = reference_tag['center'][0] - heighest_green_pixel[0]
    point_x_camera = (displacement_z * (fx / displacement_z)) + (width / 2) - difference_x
    point_y_camera = height/2

    m, b = get_equation_of_line(heighest_green_pixel, (point_x_camera, point_y_camera))
    y_point = m * width + b 
    x_point = width - 1

    ax.plot([heighest_green_pixel[0], x_point], [heighest_green_pixel[1], y_point], color=color, linewidth=1)
    ax.plot([], [], color=color, label='Camera View to Heighest Plant Pixel \n (May indicate occlusion or steep angle)')
    # add text below the graph as a warning

    
def plot_tag(ax, tag, color='red', center_size=5):
    corners = tag["corners"]
    tl = corners["top_left"]
    tr = corners["top_right"]
    br = corners["bottom_right"]
    bl = corners["bottom_left"]
    ax.add_patch(plt.Polygon([tl, tr, br, bl], fill=None, edgecolor=color, linewidth=2))
    cx, cy = tag["center"]
    ax.add_patch(plt.Circle((cx, cy), center_size, color=color, fill=True))

def plot_mask(ax, mask, color='lime'):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        contour = contour.squeeze()
        ax.plot(contour[:, 0], contour[:, 1], color=color, linewidth=2)
        
def plot_point(ax, point, color='blue', size=5):
    x, y = point
    ax.add_patch(plt.Circle((x, y), size, color=color, fill=True))
    
def plot_tag_offsets(W,H, ax, reference_tag, color='red'):
    displacement_d = reference_tag['displacements']['d']
    displacement_z = reference_tag['displacements']['z']
    displacement_x = reference_tag['displacements']['x']
    displacement_y = reference_tag['displacements']['y']
    center_x_image = W / 2
    center_y_image = H / 2
    center_x_ref = reference_tag['center'][0]
    center_y_ref = reference_tag['center'][1]
    
    ax.plot([center_x_image, center_x_ref], [center_y_image, center_y_ref], color='red', linewidth=2)
    ax.plot([center_x_image, center_x_ref], [center_y_ref, center_y_ref], color='green', linewidth=2)
    ax.plot([center_x_ref, center_x_ref], [center_y_image, center_y_ref], color='blue', linewidth=2)
    
    ax.plot([], [], color='red', label='Depth Displacement(z)\n %.6f cm' % (displacement_z*100))
    ax.plot([], [], color='green', label='Horizontal Displacement (x)\n %.6f cm' % (displacement_x*100))
    ax.plot([], [], color='blue', label='Vertical Displacement (y)\n %.6f cm' % (displacement_y*100))
    ax.plot([], [], color='black', label='Distance to QR Code (d)\n %.6f cm' % (displacement_d*100))
    
    # make it so legend appears below the graph

def plot_image_tag_detection(image, out_path, tag_list, reference_tag=None):
    graph_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    fig, ax = plt.subplots()
    W,H = graph_rgb.shape[1], graph_rgb.shape[0]
    
    if reference_tag is not None:
        plot_tag_offsets(W,H, ax, reference_tag)
    
    ax.imshow(graph_rgb)
    ax.axis('on')
    for tag in tag_list:
        plot_tag(ax, tag, color='red', center_size=10)
    
    # make it so that the graph is forced to be the size of the image
    plt.savefig(str(out_path), bbox_inches="tight")
    plt.close(fig)


def plot_image_height(image, out_path, debug_info):
    reference_tag = debug_info["reference_tag"]
    green_blob_list = debug_info["green_blob_list"]
    heighest_green_pixel = debug_info.get("heighest_green_pixel", None)
    qr_list = debug_info.get("qr_list", None)
    april_list = debug_info.get("april_list", None)
    estimated_height = debug_info.get("estimated_height", None)
    camera_parameters = debug_info.get("camera_parameters", None)
    graph_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    W,H = graph_rgb.shape[1], graph_rgb.shape[0]
    fig, ax = plt.subplots()
    ax.imshow(graph_rgb)
    ax.axis('on')

    plot_tag(ax, reference_tag, color='red', center_size=10)

    for qr_tag in qr_list:
        plot_tag(ax, qr_tag, color='cyan', center_size=5)
    
    for april_tag in april_list:
        plot_tag(ax, april_tag, color='magenta', center_size=5)
        
    for plant_blob in green_blob_list:
        mask = plant_blob["mask"]
        plot_mask(ax, mask, color='lime')

    if heighest_green_pixel is not None:
        plot_point(ax, heighest_green_pixel, color='blue', size=7)

    if estimated_height is not None:
        ax.set_title(f"Estimated Height: {100*estimated_height:.2f} cm")
        
    plot_tag_offsets(W,H, ax, reference_tag)

    if camera_parameters and heighest_green_pixel is not None:
        plot_camera_view_frustum(ax, heighest_green_pixel, camera_parameters, reference_tag, color='yellow')
    
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)
    
    plt.savefig(str(out_path), bbox_inches="tight")
    plt.close(fig)
    

    