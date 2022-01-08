import cv2

def resize(image):
    # Resizing image
    dim = (800, 600)
    image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
    return image