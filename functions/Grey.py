import cv2

def grey(image):
    # Processing to Grayscale (simpiler data)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image