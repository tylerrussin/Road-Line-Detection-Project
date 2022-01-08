import cv2

def canny(image):
    # Applying Canny edge detection (threshold values will have to be tweaked)
    image = cv2.Canny(image, threshold1=100, threshold2=130)
    return image