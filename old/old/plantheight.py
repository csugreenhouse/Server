import cv2
import matplotlib.pyplot as plt

file_path = "greenhouse/plant.jpg"
#what measurment the ruler is at, in cm
dirt_height = 17
# this should be thhe pixel level for the centimeter level of dirt height on the ruler
axis_y = 171
# can be anything, will move the image over.
axis_x = 0
# number of pixels per centimer. Result should show lines evenly spaced on ruler.
pixels_per_cm = 106

#pixel level to adjust plant indicator sensitivity. lower rbias, lower bbias, and higher gbais means lower sensitivity.
rbias = 150
gbias = 175
bbias = 150
bias = (rbias,gbias,bbias)

def plant_image_found(file_path):
    image = cv2.imread(file_path)
    if (image is None):
        print("IMAGE NOT FOUND")
        return False
    else:
        return True

def get_plant_image(file_path):
    return cv2.flip(cv2.imread(file_path), 0)

def find_green_pixel(plant_image,axis_x,axis_y,bias):
    height, width, _ = plant_image.shape
    for y in range (height-1, axis_y, -1):
        for x in range (axis_x, width):
            b, g, r = plant_image[y, x]
            if r < rbias and g > gbias and b < bbias:
                return (x,y)
            
def show_plant_graph(plant_image,axis_y,axis_x,bias):
    graph = cv2.flip(plant_image, 0)
    graph_rgb = cv2.cvtColor(plant_image, cv2.COLOR_BGR2RGB)
    
    height, width, _ = graph.shape
    plt.imshow(graph_rgb) 
    plt.axis('on')
    
    plt.xlim(axis_x, width)
    plt.ylim(axis_y, height)
    
    M = pixels_per_cm
    for y in range(axis_y, height, M):
        plt.axhline(y=y, color='blue', linestyle='--', linewidth=1)
    
    (x,y) = find_green_pixel(plant_image,axis_x,axis_y,bias)
    plt.scatter([x], [y], c="red", s=40, marker="o")
    
    plt.savefig("greenhouse/output.png", bbox_inches="tight")
    
  
def find_height_plant(file_path,dirt_height, axis_x, axis_y, pixels_per_cm, bias):
    if not plant_image_found(file_path):
        return 
    
    plant_image = get_plant_image(file_path)
    
    (x,y) = find_green_pixel(plant_image,axis_x,axis_y,bias)
    print(f"found green pixel at: {x} {y} )")
    
    plant_height = (y-axis_y)/pixels_per_cm + dirt_height
    print(f"plant height is {plant_height}")
    
    show_plant_graph(plant_image,axis_y,axis_x,bias)
      
find_height_plant(file_path,dirt_height,axis_x,axis_y,pixels_per_cm,bias)
    
    
