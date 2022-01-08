import numpy as np
import cv2

def region(image):
    vertices = np.array([[1,500], [350,350], [450,350], [800,500]])

    mask = np.zeros_like(image)
    mask = cv2.fillPoly(mask, [vertices], 255)
    mask = cv2.bitwise_and(image, mask)
    
    return mask