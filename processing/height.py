import cv2
import matplotlib.pyplot as plt
import zxingcpp
import psycopg2

def find_image(file_path):
    img = cv2.imread(file_path)
    if (img is None):
        raise ValueError(f"could not load image: {file_path}")
    return img


def get_barcode_metrics(file_path):
    img = find_image(file_path)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = zxingcpp.read_barcodes(rgb)
    if (len(results) != 1):
        raise ValueError(f"Multiple or no barcodes detected")
    results[0]
    return results[0]

def get_barcode_points(barcode):
    points = []
    for position in str(barcode.position).split():
        x_str, y_str = position.replace('\x00','').split('x')
        x, y = int(x_str),int(y_str)
        points.append([x,y])
    return points

def is_black_pixel(pixel):
    return pixel[0]<50 and pixel[1]<50 and pixel[2]<50

def is_white_pixel(pixel):
    return pixel[0]>170 and pixel[1]>170 and pixel[2]>170



def find_top(image,point):
    h,w,_ = image.shape
    x = point[0]
    y = point[1]
    found_black = False
    for y in range(point[1],0,-1):
        if not found_black and is_black_pixel(image[y,x]):
            found_black = True
        if found_black and is_white_pixel(image[y,x]):
            return x,y

def find_bot(image,point):
    h,w,_ = image.shape
    x = point[0]
    y = point[1]
    found_black = False
    for y in range(point[1],h,1):
        if not found_black and is_black_pixel(image[y,x]):
            found_black = True
        if found_black and is_white_pixel(image[y,x]):
            return x,y

def print_graph_from_metrics(res, out_path="processing/test/images/output.png"):
    image = res["image"]
    graph_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width = res["height"], res["width"]

    fig, ax = plt.subplots()
    ax.imshow(graph_rgb)
    ax.axis('on')

    # IMPORTANT: y-down to match image coordinates

    ax.set_xlabel("x axis")
    ax.set_ylabel("y axis")

    # circles for the detected points
    for key in ["blp", "brp", "trp", "tlp"]:
        x, y = res[key]
        ax.add_patch(plt.Circle((x, y), 50, color='purple', fill=True))

    plt.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


            
            


#def find_top_right(image,point):

#def find_bot_right(image,point):

#def find_bot_left(image,point):

def get_height_metrics(file_path, scale_units=5.0):
    image = find_image(file_path)
    h,w,_ = image.shape
    barcode = get_barcode_metrics(file_path)
    barcode_point = get_barcode_points(barcode)
    tlp = find_top(image,barcode_point[0])
    trp = find_top(image,barcode_point[1])
    brp = find_bot(image, barcode_point[2])
    blp = find_bot(image, barcode_point[3])
    top_green = (2500,1500)

    for name, pt in [("tlp", tlp), ("trp", trp), ("blp", blp), ("brp", brp), ("top_green", top_green)]:
        if pt is None:
            raise ValueError(f"Missing detection: {name}")

    (x1, y1) = tlp
    (x2, y2) = trp
    (x3, y3) = blp
    (x4, y4) = brp
    (xg, yg) = top_green

    m_top = (y2 - y1) / (x2 - x1)
    b_top = y1 - m_top * x1

    m_bot = (y4 - y3) / (x4 - x3)
    b_bot = y3 - m_bot * x3

    y_top = m_top * xg + b_top
    y_low = m_bot * xg + b_bot

    denom = (y_top - y_low)
    if abs(denom) < 1e-9:
        raise ZeroDivisionError("Top and bottom lines coincide at xg; cannot compute height.")

    if x2 == x1:
        raise ZeroDivisionError("Top edge is vertical; cannot compute slope.")
    if x4 == x3:
        raise ZeroDivisionError("Bottom edge is vertical; cannot compute slope.")

    m_top = (y2 - y1) / (x2 - x1)
    b_top = y1 - m_top * x1

    m_bot = (y4 - y3) / (x4 - x3)
    b_bot = y3 - m_bot * x3

    y_top = m_top * xg + b_top
    y_low = m_bot * xg + b_bot

    denom = (y_top - y_low)
    if abs(denom) < 1e-9:
        raise ZeroDivisionError("Top and bottom lines coincide at xg; cannot compute height.")

    percent = (yg - y_low) / denom
    percent = max(0.0, min(1.0, percent))
    height_est = scale_units * percent

    # Intersection of the two edges (infinite lines)
    xi = (b_bot - b_top) / (m_top - m_bot)
    yi = m_top * xi + b_top

    h, w = image.shape[:2]

    return {
        "image": image,
        "width": w,
        "height": h,

        # edges
        "m_top": m_top, "b_top": b_top,
        "m_bot": m_bot, "b_bot": b_bot,

        # points
        "tlp": (x1, y1),
        "trp": (x2, y2),
        "blp": (x3, y3),
        "brp": (x4, y4),
        "top_green": (xg, yg),

        # useful derived values
        "y_top_at_xg": y_top,
        "y_low_at_xg": y_low,
        "intersection": (xi, yi),

        # outputs
        "percent": percent,
        "height_est": height_est,
    }

def draw_line_from_mb(ax, m, b, width, height, color='purple', linewidth=3):
    """Draw y = m x + b across the whole image extent."""
    # endpoints along full image width
    x0, x1 = 0, width
    y0 = m * x0 + b
    y1 = m * x1 + b
    ax.plot([x0, x1], [y0, y1], color=color, linewidth=linewidth)

def draw_full_line(ax, p1, p2, width, height, color='purple', linewidth=3):
    """Draw an infinite line through p1 & p2, clipped to image borders."""
    x1, y1 = p1
    x2, y2 = p2

    if x2 == x1:  # vertical
        ax.plot([x1, x1], [0, height], color=color, linewidth=linewidth)
        return

    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1
    draw_line_from_mb(ax, m, b, width, height, color=color, linewidth=linewidth)

def draw_intersect_line_from_res(ax, res, color='blue', linewidth=3):
    """
    Third line: passes through the intersection of the top/bottom edges
    and also through the 'top_green' point.
    """
    (xi, yi) = res["intersection"]
    (xg, yg) = res["top_green"]
    draw_full_line(ax, (xi, yi), (xg, yg), res["width"], res["height"], color=color, linewidth=linewidth)

def print_graph_from_metrics(res, out_path="processing/test/images/output.png"):
    image = res["image"]
    graph_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width = res["height"], res["width"]

    fig, ax = plt.subplots()
    ax.imshow(graph_rgb)
    ax.axis('on')

    # IMPORTANT: y-down to match image coordinates

    ax.set_xlabel("x axis")
    ax.set_ylabel("y axis")

    # circles for the detected points
    for key in ["blp", "brp", "trp", "tlp"]:
        x, y = res[key]
        ax.add_patch(plt.Circle((x, y), 50, color='purple', fill=True))
    # top_green marker
    xg, yg = res["top_green"]
    ax.add_patch(plt.Circle((xg, yg), 50, color='blue', fill=True))

    # draw the top and bottom edges using m,b from the result
    draw_line_from_mb(ax, res["m_top"], res["b_top"], width, height, color='purple', linewidth=4)
    draw_line_from_mb(ax, res["m_bot"], res["b_bot"], width, height, color='purple', linewidth=4)

    # third line through the intersection and your chosen point
    draw_intersect_line_from_res(ax, res, color='blue', linewidth=3)

    plt.savefig(out_path, bbox_inches="tight")
    plt.close(fig)

height_metrics = get_height_metrics("processing/test/images/Image1.jpg") 
print(height_metrics["height_est"])
print_graph_from_metrics(height_metrics)


