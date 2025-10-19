import cv2
import matplotlib.pyplot as plt

def find_best_bias(image, axy, axx, plant_height):
    bestbias = (0,0,0)
    height, width, _ = image.shape
    best_difference=100
    for rbias in range(90,255,15):
        for gbias in range(90, 255, 15):
            for bbias in range (90,255, 15):
                print (f"testing bias ({rbias},{gbias},{bbias})")
                found = False
                guessed_height = 0
                for y in range (height-1, axy, -1):
                    for x in range (axx, width):
                            b, g, r = image[y, x]
                            if r < rbias and g > gbias and b < bbias:
                                guessed_height = 17+((y - axy)  / pixels_per_cm)
                                found = True
                                break
                            if 'found' in locals():
                                break
                if abs(plant_height-guessed_height)<best_difference:
                    best_difference = abs(plant_height-guessed_height)
                    best_bias = (rbias,gbias,bbias)
                    print (f"new accuracy: {(guessed_height-plant_height)/plant_height}")
    return (rbias,gbias,bbias)



# Load image
image = cv2.imread("greenhouse/plant.jpg")
if image is None:
    print("Image not found") 
else:
    
    # Parameters
    #these are all in pixels
    # Where the plant image first appears in the image.
    axy = 171
    #can be anything, but the farthest leaf of the plant should be okay
    axx = 0
    #pixels per cm
    pixels_per_cm = 106
    # bias for how the program finds the color of the plant 
    rbias = 150
    gbias = 175
    bbias = 150
    
    
    image = cv2.flip(image, 0)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    
    height, width, _ = image.shape
    plt.imshow(image_rgb) 
    plt.axis('on')
    
    plt.xlim(axx, width)
    plt.ylim(axy, height)
    
    M = pixels_per_cm
    for y in range(axy, height, M):
        plt.axhline(y=y, color='blue', linestyle='--', linewidth=1)
    
    for y in range (height-1, axy, -1):
        print (f"Scanning row {y}")
        for x in range (axx, width):
            b, g, r = image[y, x]
            if r < rbias and g > gbias and b < bbias:
                print(f"Found green pixel at ({x}, {y})")
                print(f"Color values: R={r}, G={g}, B={b}")
                print(f"Height in cm: {17+((y - axy)  / pixels_per_cm):.2f}")
                plt.scatter([x], [y], c="red", s=40, marker="o")
                found = True
                break
        if 'found' in locals():
            break       
        
    plt.savefig("greenhouse/output.png", bbox_inches="tight")

