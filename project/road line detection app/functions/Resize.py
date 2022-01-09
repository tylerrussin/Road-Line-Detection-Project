import cv2

def resize(image, x, y):
    # Resizing image
    dim = (x, y)
    image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
    return image