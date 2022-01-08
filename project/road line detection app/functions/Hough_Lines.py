import numpy as np
import cv2

def hough_lines(image):
    # Find all lines
    lines = cv2.HoughLinesP(image, 1, np.pi/180, 180, np.array([]), 100, 5)
    return lines