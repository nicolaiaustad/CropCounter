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
    #Best params 
    params= [9, 7, 0.7686860830758948, 1, 0.16154762031630662, 1, 0.9421867499939008, 1, 52.758635929553286, 572.5683701121316]
    #Dummy function for
    value = calculations.blob(image_path, 9, 7, 0.7686860830758948, 1, 0.16154762031630662, 1, 0.9421867499939008, 1, 52.758635929553286, 572.5683701121316)
    return value
