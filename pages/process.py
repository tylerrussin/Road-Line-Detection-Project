# Imports from 3rd party libraries
import dash_bootstrap_components as dbc
from dash import dcc

# Imports from this application
from run import app

# Infor to be displayed on the process page of the website
column1 = dbc.Col(
    [
        dcc.Markdown(
            """
            # Road Lane Detection with Computer Vision

            The following is a walk-through of our process of masking predicted lines onto our video data. With OpenCV, we process videos frame by frame.

            **Overview**
            - OpenCV
            - Frame Masking
            - Hough Line Tranformations
            - Real World Driving Data Collection

            **Resize frame**

            Resizing the video frames to be in a standardized format for working with the video feed
            ```
            def resize(image):

            # Resizing image
            dim = (800, 600)
            image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
            return image
            ```

            **Edge detection**

            Preforming an edge detection mask over the frame to simplify the data in a format that lines can begin to be discovered

            ```
            def canny(image):
            # Applying Canny edge detection (threshold values will have to be tweaked)
            image = cv2.Canny(image, threshold1=100, threshold2=130)
            return image
            ```

            **Greyscale conversion**

            Converting image to greyscale for data simplicity
            ```
            def grey(image):
            # Processing to Grayscale (simpiler data)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return image
            ```

            **Gaussian Blur**

            This is a blurring technic that we are utilizing to blur pixels together so that the Hough Line implementation is more performant
            ```
            def blur(image):
            # Adding Gaussian Blur (much more effective when applied after edge detection)
            image = cv2.GaussianBlur(image, (5, 5), 0)
            return image
            ```

            **Region masking**

            Cutting out most of the frame leaving only the pixels that exist where road lanes could be

            ```
            def region(image):
            vertices = np.array([[1,500], [350,350], [450,350], [800,500]])

            mask = np.zeros_like(image)
            mask = cv2.fillPoly(mask, [vertices], 255)
            mask = cv2.bitwise_and(image, mask)
            
            return mask
            ```

            **Hough Lines Algorithm**

            Apply the line algorithm. It searches for lines within the frame given certain conditions

            ```
            def hough_lines(image):
            # Find all lines
            lines = cv2.HoughLinesP(image, 1, np.pi/180, 180, np.array([]), 100, 5)
            return lines
            ```

            **Average Lines**

            Averaging all the lines found and finding the two lines found to determine the two lines that are likely our lane lines

            ```
            def make_points(image, average):
            slope, y_int = average
            y1 = image.shape[0]
            y2 = int(y1 * (3/5))
            x1 = int((y1 - y_int) // slope)
            x2 = int((y2 - y_int) // slope)
            return np.array([x1, y1, x2, y2])

            def average(image, lines):
            # Find average left and right lines
            left = []
            right = []
            for line in lines:
                x1, y1, x2, y2 = line.reshape(4)
                parameters = np.polyfit((x1, x2), (y1, y2), 1)
                slope = parameters[0]
                y_int = parameters[1]
                # (all images in OpenCV have inversed y-axes)
                if slope < 0:
                    left.append((slope, y_int))
                else:
                    right.append((slope, y_int))

            # Calculate average points
            right_avg = np.average(right, axis=0)
            left_avg = np.average(left, axis=0)
            left_line = make_points(image, left_avg)
            right_line = make_points(image, right_avg)

            return np.array([left_line, right_line])
            ```

            **Display Lines**

            Displaying the discovered lines onto our source frame

            ```
            def draw_lines(image, lines):
            lines_image = np.zeros_like(image)
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line
                    cv2.line(lines_image, (x1, y1), (x2, y2), [255,0,0], 10)
            return lines_image
            ```
            """
        ),
    ],
)

layout = dbc.Row([column1])