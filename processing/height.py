import cv2
import matplotlib.pyplot as plt

def plant_image_found(file_path):
    image = cv2.flip(cv2.imread(file_path),0)
    if (image is None):
        print("IMAGE NOT FOUND")
        return image
    else:
        return image




def print_graph(v):
    graph = v.image
    graph_rgb = cv2.cvtColor(graph, cv2.COLOR_BGR2RGB)

    height, width, _ = graph.shape

    fig, ax = plt.subplots()
    ax.imshow(graph_rgb)
    ax.axis('on')

    ax.set_xlim(0, width)
    ax.set_ylim(0, height)  # flip y-axis so coordinates match image

    ax.set_xlabel("x axis")
    ax.set_ylabel("y axis")
    # Create and add circle to the axes
    
    
    for point in [v.blp, v.brp, v.trp, v.tlp]:
        circle = plt.Circle(point, 50, color='purple', fill=True)
        ax.add_patch(circle)
        
    circle = plt.Circle(v.top_green, 50, color='blue', fill=True)
    ax.add_patch(circle)
    
    draw_full_line(ax,v.blp,v.brp,width,height)
    draw_full_line(ax,v.tlp,v.trp,width,height)
    
    draw_intersect_line(ax,v.tlp,v.trp,v.blp,v.brp,width,height,v.top_green, color='blue')

    plt.savefig("Server/processing/output.png", bbox_inches="tight")
    plt.close(fig)  # close to free memory
    
def draw_intersect_line(ax,tpl,tpr,btl,btr,width,height,green_point, color='purple',linewidth=3):
    (x1,y1) = tpl
    (x2,y2) = tpr
    (x3,y3) = btl
    (x4,y4) = btr
    
    m1 = (y2-y1)/(x2-x1)
    b1 = y1 - m1*x1
    
    m2 = (y4 - y3)/(x4 - x3)
    b2 = y3 - m2 * x3
    
    x = (b2-b1)/m1-m2
    y = m1*x+b1
    
    draw_full_line(ax,(x,y),green_point,width,height,color)
    

def draw_full_line(ax, p1, p2, width, height, color='purple', linewidth=3):
    # unpack
    x1, y1 = p1
    x2, y2 = p2

    # handle vertical line separately to avoid divide-by-zero
    if x2 == x1:
        ax.plot([x1, x1], [0, height], color=color, linewidth=linewidth)
        return

    # line equation: y = m*x + b
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1

    # find intersections with image borders
    x_start = 0
    y_start = m * x_start + b
    x_end = width
    y_end = m * x_end + b

    # clip to image boundaries
    ax.plot([x_start, x_end], [y_start, y_end], color=color, linewidth=linewidth)
    

def find_purple_bl(image):
    height, width, _ = image.shape
    for s in range(height + width - 1):  # s = x + y
        for x in range(s + 1):
            y = s - x
            if x < width and y < height:
                pixel = image[y, x] 
                if (pixel[0]>200 and pixel[2]>200 and pixel[1]<50):
                    print(x,y)
                    print("PURPLE FOUND")
                    return (x,y)
                
def find_purple_tl(image):
    height, width, _ = image.shape
    for s in range(height + width - 1):  # s = x + y
        for x in range(s + 1):
            y = height - s + x
            if x < width and y < height:
                pixel = image[y, x] 
                if (pixel[0]>200 and pixel[2]>200 and pixel[1]<50):
                    print(x,y)
                    print("PURPLE FOUND")
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
                    print(x,y)
                    print("PURPLE FOUND")
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
                    print(f"PURPLE FOUND at ({x},{y})")
                    return (x, y)
                

def find_green_top(image):
    height, width, _ = image.shape
    for y in range(height-1,0,-1):
        for x in range(width):
            pixel = image[y,x]
            if pixel[0]<80 and pixel[1]>100 and pixel[2]<100:
                print(f"GREEN FOUND AT {x},{y})")
                print(pixel)
                return (x,y)
                
def compute_height(image_path, scale_units=5.0):
    # Load image
    image = plant_image_found(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")

    # Detect points
    tlp = find_purple_tl(image)
    trp = find_purple_tr(image)
    blp = find_purple_bl(image)
    brp = find_purple_br(image)
    top_green = find_green_top(image)

    # Validate detections
    for name, pt in [("tlp", tlp), ("trp", trp), ("blp", blp), ("brp", brp), ("top_green", top_green)]:
        if pt is None:
            raise ValueError(f"Missing detection: {name}")

    (x1, y1) = tlp
    (x2, y2) = trp
    (x3, y3) = blp
    (x4, y4) = brp
    (xg, yg) = top_green

    # Slopes of top and bottom lines (guard vertical)
    if x2 == x1:
        raise ZeroDivisionError("Top edge is vertical; cannot compute slope.")
    if x4 == x3:
        raise ZeroDivisionError("Bottom edge is vertical; cannot compute slope.")

    m_top = (y2 - y1) / (x2 - x1)
    b_top = y1 - m_top * x1

    m_bot = (y4 - y3) / (x4 - x3)
    b_bot = y3 - m_bot * x3

    # Intersections of vertical x = xg with top/bottom edges
    y_top = m_top * xg + b_top
    y_low = m_bot * xg + b_bot

    # Height fraction along the vertical between those edges at x = xg
    denom = (y_top - y_low)
    if abs(denom) < 1e-9:
        raise ZeroDivisionError("Top and bottom lines coincide at xg; cannot compute height.")

    # If y increases downward (OpenCV coords), this yields 0 at bottom, 1 at top:
    percent = 1.0 - (yg - y_low) / denom

    # Optionally clamp to [0,1]
    percent = max(0.0, min(1.0, percent))

    height_est = scale_units * percent

    print(f"top_green = ({xg}, {yg})")
    print(f"delta_numer = {(y_top - y_low) - (yg - y_low):.3f}")
    print(f"estimated height of plant is {height_est:.3f} (units)")

    return {
        "percent": percent,
        "height_est": height_est,
        "y_top": y_top,
        "y_low": y_low,
        "m_top": m_top, "b_top": b_top,
        "m_bot": m_bot, "b_bot": b_bot,
    }

# Example:
# res = compute_height("Server/processing/Image1.jpg", scale_units=5.0)


class view:
    image_path = "Server/processing/Image1.jpg"
    image = plant_image_found(image_path)
    tlp = find_purple_tl(image)
    (x1,y1) = tlp
    trp = find_purple_tr(image)
    (x2,y2) = trp
    blp = find_purple_bl(image)
    (x3,y3) = blp
    brp = find_purple_br(image)
    (x4,y4) = brp
    
    top_green = find_green_top(image)
    (x_green,y_green) = top_green
    
    m_top = (y2 - y1) / (x2 - x1)
    b_top = y1 - m_top*x1
    
    m_bot = (y4 - y3) / (x4 - x3)
    b_bot = y3 - m_bot*x3
    
    y_top = m_top*x_green+b_top
    y_low = m_bot*x_green+b_bot
    
    percent = 1-(((y_top - y_low) - (y_green - y_low)) / (y_top - y_low))
    height = 5 * percent

    print(f"estimated height of plant is {height}")

    
print_graph(view)