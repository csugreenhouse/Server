import cv2
import numpy as np
import matplotlib.pyplot as plt
import warnings
import numpy as np
from plant_requests.utils.line_util import get_equation_of_line, get_vertical_line, fractional_height_between_lines, get_intercept_of_lines

def plot_height_request_graph_info(image, out_path, graph_info):
    estimed_heights = graph_info["estimated_heights"]
    estimated_heights_info = graph_info["estimated_heights_info"]
    camera_parameters = graph_info["camera_parameters"]
    
    # Initialize the graph
    graph_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    W,H = graph_rgb.shape[1], graph_rgb.shape[0]
    fig, ax = plt.subplots()
    ax.imshow(graph_rgb)
    ax.axis('on')
        
    title_string = ""
    color_pallet = ['cyan', 'yellow', 'magenta', 'orange', 'pink', 'lime', 'aqua']
    
    for i, (estimated_height, estimated_height_info) in enumerate(zip(estimed_heights, estimated_heights_info)):
        title_string += f"Estimated Height for tag {estimated_height_info['reference_tag']['data']}: {100*estimated_height:.2f} cm \n"
        color = color_pallet[i % len(color_pallet)]
        add_estimate_height_graph_info(ax, W, H, estimated_height_info, color=color)
        #add_tag_displacement_relative_to_camera(ax, W, H, estimated_height_info["reference_tag"], color=color)
        add_camera_view_frustum(ax, estimated_height_info["heighest_green_pixel"], camera_parameters, estimated_height_info["reference_tag"], color=color)
    
    ax.set_title(title_string)
    ax.title.set_ha('left')
    ax.title.set_position([0.05, 0.95])
    
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),ncol=2)
    plt.savefig(str(out_path), bbox_inches="tight")
    plt.close(fig)
    
def plot_estimate_height_graph_info(image, out_path, graph_info):
    # Initialize the graph
    graph_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    W,H = graph_rgb.shape[1], graph_rgb.shape[0]
    fig, ax = plt.subplots()
    ax.imshow(graph_rgb)
    ax.axis('on')
    
    # initialize title string
    estimated_height = graph_info["estimated_height"]
    fractional_height = graph_info["fractional_height"]
    reference_tag = graph_info["reference_tag"]
    
    title_string = ""
    title_string += f"Estimated Height: {100*estimated_height:.2f} cm \n"
    title_string += f"Fractional Height: {fractional_height} cm \n"
    title_string += f"Reference Tag ID: {reference_tag['data']} \n"
    title_string += f"Scale Units (m): {reference_tag['scale_units_m']} \n"
    title_string += f"Bias Units (m): {reference_tag['bias_units_m']} \n"
    title_string += f"Color Bounds: {reference_tag['color_bounds'][0]},{reference_tag['color_bounds'][1]} \n"
    ax.set_title(title_string)
    ax.title.set_ha('left')
    ax.title.set_position([0.05, 0.95])

    add_estimate_height_graph_info(ax, W, H, graph_info)
    
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),ncol=2)
    plt.savefig(str(out_path), bbox_inches="tight")
    plt.close(fig)
    
def plot_calculated_displacements_graph_info(image, out_path, reference_tag):
    # Initialize the graph
    graph_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    W,H = graph_rgb.shape[1], graph_rgb.shape[0]
    fig, ax = plt.subplots()
    ax.imshow(graph_rgb)
    ax.axis('on')
    
    # initialize title string

    add_tag_displacement_relative_to_camera(ax, W, H, reference_tag)
    
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),ncol=2)
    plt.savefig(str(out_path), bbox_inches="tight")
    plt.close(fig)

def add_estimate_height_graph_info(ax, W, H,graph_info, color='cyan'):
    try :
        estimated_height = graph_info["estimated_height"]
        heighest_green_pixel = graph_info["heighest_green_pixel"]
        equation_top = graph_info["equation_top"]
        equation_bottom = graph_info["equation_bottom"]
        fractional_height = graph_info["fractional_height"]
        reference_tag = graph_info["reference_tag"]
        plant_bounds = reference_tag["plant_bounds"]
    except KeyError as e:
        raise KeyError(f"Missing key in graph_info: {e}")
    
    
    # plot the reference tag
    # a good color for the tag would be red
    add_tag(ax, reference_tag, color=color)
    # plot lines
    #add_line(ax, equation_top, color=color2, linestyle='--', label='Top Line of Reference Tag')
    #add_line(ax, equation_bottom, color=color2, linestyle='--', label='Bottom Line of Reference Tag')
    # plot the heighest green pixel
    add_point(ax, heighest_green_pixel, color='green', size=10)
    # plot plant bounds
    for width_percent in plant_bounds:
        x_coordinate = width_percent * W
        bound_line = get_vertical_line(x_coordinate)
        add_line(ax, bound_line, color=color, linestyle='-.', label='Plant Bound Line')
    # plot the green blobs
    add_green_blobs(ax, graph_info["green_blob_list"], color='lime')
    # add legend
    
    
def plot_heighest_green_pixel_graph_info(image, out_path, graph_info):
    # Initialize the graph
    graph_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    W,H = graph_rgb.shape[1], graph_rgb.shape[0]
    fig, ax = plt.subplots()
    ax.imshow(graph_rgb)
    ax.axis('on')

    # initialize title string
    heighest_green_pixel = graph_info["heighest_green_pixel"]
    green_blob_list = graph_info["green_blob_list"]
    
    title_string = ""
    title_string += f"Heighest Green Pixel: {heighest_green_pixel} \n"
    ax.set_title(title_string)
    ax.title.set_ha('left')
    ax.title.set_position([0.05, 0.95])

    add_point(ax, heighest_green_pixel, color='green', size=10)
    add_green_blobs(ax, green_blob_list, color='lime')
    
    plt.savefig(str(out_path), bbox_inches="tight")
    plt.close(fig)
        
def add_tag_displacement_relative_to_camera(ax, W, H, reference_tag, color=None):
    if color is None:
        color = ['red', 'green', 'blue']
    else:
        color = [color]*3
        
    displacement_d = reference_tag['displacements']['d']
    displacement_z = reference_tag['displacements']['z']
    displacement_x = reference_tag['displacements']['x']
    displacement_y = reference_tag['displacements']['y']
    center_x_image = W / 2
    center_y_image = H / 2
    center_x_ref = reference_tag['center'][0]
    center_y_ref = reference_tag['center'][1]

    ax.plot([center_x_image, center_x_ref], [center_y_image, center_y_ref], color=color[0], linewidth=2)
    ax.plot([center_x_image, center_x_ref], [center_y_ref, center_y_ref], color=color[1], linewidth=2)
    ax.plot([center_x_ref, center_x_ref], [center_y_image, center_y_ref], color=color[2], linewidth=2)

    ax.plot([], [], color=color[0], label='Depth Displacement(z)\n %.6f cm' % (displacement_z*100))
    ax.plot([], [], color=color[1], label='Horizontal Displacement (x)\n %.6f cm' % (displacement_x*100))
    ax.plot([], [], color=color[2], label='Vertical Displacement (y)\n %.6f cm' % (displacement_y*100))
    ax.plot([], [], color='black', label='Distance to QR Code (d)\n %.6f cm' % (displacement_d*100))

def add_camera_view_frustum(ax, heighest_green_pixel,camera_parameters, reference_tag, color='yellow'):
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

    
def add_tag(ax, tag, color='cyan', center_size=20):
    try:
        corners = tag["corners"]
        tl = corners["top_left"]
        tr = corners["top_right"]
        br = corners["bottom_right"]
        bl = corners["bottom_left"]
    except KeyError:
        warnings.warn("Tag corners not found, cannot plot tag.")
        return
    # add small text in center with tag data
    ax.add_patch(plt.Polygon([tl, tr, br, bl], fill=None, edgecolor=color, linewidth=2))
    cx, cy = tag["center"]
    ax.add_patch(plt.Circle((cx, cy), center_size, color=color, fill=True))
    ax.text(tag["center"][0], tag["center"][1], str(tag["data"]), fontsize=8, ha='center', va='center')

def add_green_blobs(ax, plant_blob_list, color='lime'):
    for blob in plant_blob_list:
        contours, _ = cv2.findContours(blob["mask"], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            contour = contour.squeeze()
            ax.plot(contour[:, 0], contour[:, 1], color=color, linewidth=2)

def add_point(ax, point, color='blue', size=5):
    x, y = point
    ax.add_patch(plt.Circle((x, y), size, color=color, fill=True))

'''
def add_tag_offsets(W,H, ax, reference_tag, color='cyan'):
    displacement_d = reference_tag['displacements']['d']
    displacement_z = reference_tag['displacements']['z']
    displacement_x = reference_tag['displacements']['x']
    displacement_y = reference_tag['displacements']['y']
    center_x_image = W / 2
    center_y_image = H / 2
    center_x_ref = reference_tag['center'][0]
    center_y_ref = reference_tag['center'][1]

    ax.plot([center_x_image, center_x_ref], [center_y_image, center_y_ref], color=color, linewidth=2)
    ax.plot([center_x_image, center_x_ref], [center_y_ref, center_y_ref], color=color, linewidth=2)
    ax.plot([center_x_ref, center_x_ref], [center_y_image, center_y_ref], color=color, linewidth=2)

    ax.plot([], [], color='red', label='Depth Displacement(z)\n %.6f cm' % (displacement_z*100))
    ax.plot([], [], color='green', label='Horizontal Displacement (x)\n %.6f cm' % (displacement_x*100))
    ax.plot([], [], color='blue', label='Vertical Displacement (y)\n %.6f cm' % (displacement_y*100))
    ax.plot([], [], color='black', label='Distance to QR Code (d)\n %.6f cm' % (displacement_d*100))
'''
def add_line(ax, equation, color='yellow', linestyle='--', label=None):
    slope, intercept = equation
    x_vals = np.array(ax.get_xlim())
    if slope == float('inf'):
        x_line = np.full_like(x_vals, intercept)
        y_line = np.array(ax.get_ylim())
    else:
        y_vals = slope * x_vals + intercept
        x_line = x_vals
        y_line = y_vals
    ax.plot(x_line, y_line, color=color, linestyle=linestyle, label=label)

   



    