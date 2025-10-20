import cv2
import matplotlib.pyplot as plt
import zxingcpp

def plant_image_found(file_path):
    image = cv2.flip(cv2.imread(file_path),0)
    if (image is None):
        print("IMAGE NOT FOUND")
        return image
    else:
        return image

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

def print_graph_from_metrics(res, out_path="Server/processing/test/images/output.png"):
    image = res["image"]
    graph_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width = res["height"], res["width"]

    fig, ax = plt.subplots()
    ax.imshow(graph_rgb)
    ax.axis('on')

    # IMPORTANT: y-down to match image coordinates
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)

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


def find_purple_bl(image):
    height, width, _ = image.shape
    for s in range(height + width - 1):  # s = x + y
        for x in range(s + 1):
            y = s - x
            if x < width and y < height:
                pixel = image[y, x] 
                if (pixel[0]>200 and pixel[2]>200 and pixel[1]<50):
                    return (x,y)
                
def find_purple_tl(image):
    height, width, _ = image.shape
    for s in range(height + width - 1):  # s = x + y
        for x in range(s + 1):
            y = height - s + x
            if x < width and y < height:
                pixel = image[y, x] 
                if (pixel[0]>200 and pixel[2]>200 and pixel[1]<50):
                    return (x,y)
                
def find_purple_br(image):
    height, width, _ = image.shape
    for s in range(height + width - 1):  # s = x + y
        for i in range(s+1):
            x = (width - 1) - i
            y = s - i
            if x < width and y < height:
                pixel = image[y, x] 
                if (pixel[0]>200 and pixel[2]>200 and pixel[1]<50):
                    return (x,y)
                
def find_purple_tr(image):
    height, width, _ = image.shape
    for s in range(height + width - 1):       # s = x + y
        for i in range(s + 1):
            x = (width  - 1) - i              # move left
            y = (height - 1) - (s - i)        # move up
            if 0 <= x < width and 0 <= y < height:
                pixel = image[y, x]
                if pixel[0]>200 and pixel[2]>200 and pixel[1]<50:
                    return (x, y)
                
def find_green_top(image):
    height, width, _ = image.shape
    for y in range(height-1,0,-1):
        for x in range(width):
            pixel = image[y,x]
            if pixel[0]<80 and pixel[1]>100 and pixel[2]<100:
                return (x,y)
            
def compute_height_metrics(image_path, scale_units=5.0):
    image = plant_image_found(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")

    # ---- detections ----
    tlp = find_purple_tl(image)
    trp = find_purple_tr(image)
    blp = find_purple_bl(image)
    brp = find_purple_br(image)
    top_green = find_green_top(image)

    for name, pt in [("tlp", tlp), ("trp", trp), ("blp", blp), ("brp", brp), ("top_green", top_green)]:
        if pt is None:
            raise ValueError(f"Missing detection: {name}")

    (x1, y1) = tlp
    (x2, y2) = trp
    (x3, y3) = blp
    (x4, y4) = brp
    (xg, yg) = top_green

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

    # y-down image coords: 0 at top, increases downward
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
    
def get_barcode_metrics(file_path):
    img = cv2.imread(file_path)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = zxingcpp.read_barcodes(rgb)  # handles QR + many 1D/2D symbologies
    return results

def generate_query(file_path):
    barcode_metrics = get_barcode_metrics(file_path)
    specimen_id = barcode_metrics[0].text
    height_metrics = compute_height_metrics(file_path)
    print_graph_from_metrics(height_metrics,"Server/processing/test/images/output.png")
    height = height_metrics["height_est"]
    query = f"INSERT INTO HEIGHT_LOG (SPECIMEN_ID, HEIGHT_CM) VALUES (\'{specimen_id}\',\'{height}\')"
    print(query)
    return query




    
