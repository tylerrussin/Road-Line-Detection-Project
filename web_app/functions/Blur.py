import cv2

def blur(image):
    # Adding Gaussian Blur (much more effective when applied after edge detection)
    image = cv2.GaussianBlur(image, (5, 5), 0)
    return image