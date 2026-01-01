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
    try:
        corners = tag["corners"]
        tl = corners["top_left"]
        tr = corners["top_right"]
        br = corners["bottom_right"]
        bl = corners["bottom_left"]
    except KeyError:
        warnings.warn("Tag corners not found, cannot plot tag.")
        return
    ax.add_patch(plt.Polygon([tl, tr, br, bl], fill=None, edgecolor=color, linewidth=2))
    cx, cy = tag["center"]
    ax.add_patch(plt.Circle((cx, cy), center_size, color=color, fill=True))

def plot_green_blobs(ax, blobs, color='lime'):
    for blob in blobs:
        contours, _ = cv2.findContours(blob["mask"], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
        plot_tag_offsets(W, H, ax, tag)
    
    # make it so that the graph is forced to be the size of the image
    plt.savefig(str(out_path), bbox_inches="tight")
    plt.close(fig)

def plot_line(ax, equation, color='yellow', linestyle='--', label=None):
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

def plot_image_height(image, out_path, debug_info):
    # unpack debug info. If there is anything missing, raise an error
    try:
        # From debug info
        estimated_height = debug_info["estimated_height"]
        heighest_green_pixel = debug_info["heighest_green_pixel"]
        equation_top = debug_info["equation_top"]
        equation_bottom = debug_info["equation_bottom"]
        fractional_height = debug_info["fractional_height"]
        reference_tag = debug_info["reference_tag"]
        green_blob_list = debug_info["green_blob_list"]
        # From reference tag, included in debug info
        reference_tag_id = reference_tag["data"]
        scale_units_m = reference_tag["scale_units_m"]
        bias_units_m = reference_tag["bias_units_m"]
        color_bounds = reference_tag["color_bounds"]
        
    except KeyError as e:
        raise KeyError(f"Missing key in debug_info: {e}")
    
    # Initialize the graph
    graph_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    W,H = graph_rgb.shape[1], graph_rgb.shape[0]
    fig, ax = plt.subplots()
    ax.imshow(graph_rgb)
    ax.axis('on')
    
    # initialize title string
    title_string = ""
    title_string += f"Estimated Height: {100*estimated_height:.2f} cm \n"
    title_string += f"Fractional Height: {fractional_height} cm \n"
    title_string += f"Reference Tag ID: {reference_tag_id} \n"
    title_string += f"Reference Tag Scale: {scale_units_m*100:.2f} cm \n"
    title_string += f"Bias Correction: {bias_units_m*100:.2f} cm \n"
    title_string += f"Color Bounds: {color_bounds[0]},{color_bounds[1]} \n"
    title_string += f"Plant_ID: ** \n"
    ax.set_title(title_string)
    ax.title.set_ha('left')
    ax.title.set_position([0.05, 0.95])

    # plot the reference tag
    plot_tag(ax, reference_tag, color='red', center_size=10)

    # plot lines
    plot_line(ax, equation_top, color='red', linestyle='--', label='Top Line of Reference Tag')
    plot_line(ax, equation_bottom, color='red', linestyle='--', label='Bottom Line of Reference Tag')

    # plot the heighest green pixel
    plot_point(ax, heighest_green_pixel, color='green', size=10)

    #plot the green blobs
    plot_green_blobs(ax, green_blob_list, color='lime')

    # add legend
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),ncol=2)
    plt.savefig(str(out_path), bbox_inches="tight")
    plt.close(fig)




    