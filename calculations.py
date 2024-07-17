import cv2
import numpy as np
import statistics

import os

### Blob detection method
def blob(image, k, b, circ1, circ2, iner1, iner2, conv1, conv2, area_min, area_max):
    # Convert the image to grayscale
    gray = cv2.imread(image, cv2.IMREAD_GRAYSCALE)

    blurred_image = cv2.GaussianBlur(gray, (k, k), 0)  #Apply gaussian blur to the image
    
    thresh = cv2.adaptiveThreshold(blurred_image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,b,2) #Apply adaptive gaussian thresholding to the image
    
    # Set up the SimpleBlobDetector parameters
    params = cv2.SimpleBlobDetector_Params()

    # Filter by circularity
    params.filterByCircularity = True
    params.minCircularity = circ1 # Adjust as needed
    params.maxCircularity = circ2

    # Filter by inertia
    params.filterByInertia = True
    params.minInertiaRatio = iner1  # Adjust as needed
    params.maxInertiaRatio = iner2
    
    # Filter by Convexity
    params.filterByConvexity = True
    params.minConvexity = conv1
    params.maxConvexity = conv2

    # Filter by area
    params.filterByArea = True
    params.minArea = area_min # Adjust as needed
    params.maxArea = area_max  # Adjust as needed
    
    # Create a detector with the parameters
    detector = cv2.SimpleBlobDetector_create(params)

    # Detect blobs
    keypoints = detector.detect(thresh)
   

    return len(keypoints)



    
def AI_calculation(image_path):
    #Best parameters are stored privately and not shared on GitHub.
    params= [7, 7, 0.7389686996692504, 1, 0.37438265817010036, 1, 0.526007653770587, 1, 42.77016806408365, 483.1027394129678]
    #Dummy function for
    value = blob(image_path, 7, 7, 0.7389686996692504, 1, 0.37438265817010036, 1, 0.526007653770587, 1, 42.77016806408365, 483.1027394129678)
    return value
