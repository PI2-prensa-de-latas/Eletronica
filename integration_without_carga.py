import cv2
import numpy as np
import time
import RPi.GPIO as GPIO

#iniciar condições de reconhecimento de forma para coca
font = cv2.FONT_HERSHEY_COMPLEX
l_h = 110
l_s = 0
l_v = 0
u_h = 180
u_s = 255
u_v = 255
lower_red = np.array([l_h, l_s, l_v])
upper_red = np.array([u_h, u_s, u_v])

# #iniciar reconhecimento de marca
def ORB_detector(new_image, image_template):
    # Function that compares input image to template
    # It then returns the number of ORB matches between them
    image1 = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)
    # Create ORB detector with 1000 keypoints with a scaling pyramid factor of 1.2
    orb = cv2.ORB_create(500, 1.5)
    # Detect keypoints of original image
    (kp1, des1) = orb.detectAndCompute(image1, None)
    # Detect keypoints of rotated image
    (kp2, des2) = orb.detectAndCompute(image_template, None)
    # Create matcher 
    # Note we're no longer using Flannbased matching
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    # Do matching
    matches = bf.match(des1,des2)
    # Sort the matches based on distance.  Least distance
    # is better
    matches = sorted(matches, key=lambda val: val.distance)
    return len(matches)

def SHAPE (IS_CAN,EMPTY, IS_RECT = None):
    if (IS_CAN == 1) and (EMPTY == 0):
        
        _, frame = cap.read()
        height, width = frame.shape[:2]
        teste = cv2.imwrite('teste.png', frame)
            
        #cv2.imshow('Object Detector using ORB', teste)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_red, upper_red)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print ("entrou no while")
        
        #height, width = frame.shape[:2]

        for cnt in contours:
            print ("entrou no for")
            #area = cv2.contourArea(cnt)
            approx = cv2.approxPolyDP(cnt, 0.05*cv2.arcLength(cnt, True), True)
            x = approx.ravel()[0]
            y = approx.ravel()[1]
            #cv2.drawContours(teste, [approx], -1, (0, 255, 0), 3)
            #if area > 1200:
                #cv2.drawContours(frame, [approx], -1, (0, 255, 0), 3)
            if len(approx) == 4:
                print("é retângulo")
                IS_RECT = 1
            else:
                IS_RECT = 0
                IS_CAN = 0
        return(IS_RECT)

def LOGO(IS_RECT,IS_CAN,IS_COKE = None,OPEN = None):
    if (IS_RECT == 1) and (IS_CAN == 1):
                # Define ROI Box Dimensions (Note some of these things should be outside the loop)
        _, frame = cap.read()
        height, width = frame.shape[:2] 
        top_left_x = int(width / 3)
        top_left_y = int((height / 2) + (height / 4))
        bottom_right_x = int((width / 3) * 2)
        bottom_right_y = int((height / 2) - (height / 4))
            # Draw rectangular window for our region of interest
        cv2.rectangle(frame, (top_left_x,top_left_y), (bottom_right_x,bottom_right_y), 255, 3)
        cropped = frame[bottom_right_y:top_left_y , top_left_x:bottom_right_x]
            # Flip frame orientation horizontally
            #frame = cv2.flip(frame,1)
        matches = ORB_detector(cropped, image_template)
            # Display status string showing the current no. of matches 
        output_string = "Matches = " + str(matches)
        cv2.putText(frame, output_string, (50,450), cv2.FONT_HERSHEY_COMPLEX, 2, (250,0,150), 2)
        threshold = 30
            # If matches exceed our threshold then object has been detected
        if matches > threshold:
            #cv2.rectangle(teste, (top_left_x,top_left_y), (bottom_right_x,bottom_right_y), (0,255,0), 3)
            print("match")
            #cv2.putText(teste,'Object Found',(50,50), cv2.FONT_HERSHEY_COMPLEX, 2 ,(0,255,0), 2)
            cv2.imshow('Object Detector using ORB', frame)
            IS_COKE = 1
            OPEN = 1
            print("abriu alçapão")
            p.ChangeDutyCycle(5)
            print("abriu alçapão1")
            time.sleep(5)
            print("abriu alçapão2")
            p.ChangeDutyCycle(15.5)
            print("abriu alçapão3")
            time.sleep(5)
            #GPIO.cleanup()
        else:
            IS_COKE = 0
            OPEN = 0
    #cv2.imshow('Object Detector using ORB', frame)
    return(IS_COKE,OPEN)

def DOOR (OPEN):
    if OPEN == 1:
        print("abriu alçapão")
        p.ChangeDutyCycle(5)
        time.sleep(5)
        p.ChangeDutyCycle(15.5)
        time.sleep(5)
        gpio.cleanup()
        OPEN = 0
        IS_CAN = 0
        IS_COKE = 0
        EMPTY = 0
    return(IS_CAN,IS_COKE,EMPTY)

#sensor indutivo
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)

#servo motor
servoPIN = 17
GPIO.setwarnings(False)
GPIO.setup(servoPIN, GPIO.OUT)
p = GPIO.PWM(servoPIN, 50) # GPIO 17 para PWM com 50Hz
p.start(2.5) # Initializaçao


cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

#imagem modelo para identificar logo
image_template = cv2.imread('cocalogo.png', 0) 

#iniciar auxiliares
#IS_RECT = 0
#IS_CAN = 0
#EMPTY = 0
#IS_COKE = 0
#OPEN = 0

while True:
    if GPIO.input(23) == GPIO.LOW:
         IS_CAN = 1
         EMPTY = 0
         IS_RECT = SHAPE(IS_CAN,EMPTY)
         IS_COKE = LOGO(IS_RECT,IS_CAN)
         #OPEN = DOOR(OPEN)
         print("metal")
    else:
         IS_CAN = 1
         EMPTY = 0
         IS_RECT = SHAPE(IS_CAN,EMPTY)
         IS_COKE = LOGO(IS_RECT,IS_CAN)
         #OPEN = DOOR(OPEN)
         print("nao metal")

    key = cv2.waitKey(1)
    if key == 27:
        break
 
    time.sleep(1)
 
GPIO.cleanup()

# if (IS_CAN == 1) and (EMPTY == 0):
#     
#     _, frame = cap.read()
#     height, width = frame.shape[:2]
#     teste = cv2.imwrite('teste.png', frame)
#         
#     #cv2.imshow('Object Detector using ORB', teste)
#     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#     mask = cv2.inRange(hsv, lower_red, upper_red)
#     kernel = np.ones((5, 5), np.uint8)
#     mask = cv2.erode(mask, kernel)
#     contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     print ("entrou no while")
#     
#     #height, width = frame.shape[:2]
# 
#     for cnt in contours:
#         print ("entrou no for")
#         #area = cv2.contourArea(cnt)
#         approx = cv2.approxPolyDP(cnt, 0.05*cv2.arcLength(cnt, True), True)
#         x = approx.ravel()[0]
#         y = approx.ravel()[1]
#         #cv2.drawContours(teste, [approx], -1, (0, 255, 0), 3)
#         #if area > 1200:
#             #cv2.drawContours(frame, [approx], -1, (0, 255, 0), 3)
#         if len(approx) == 4:
#             print("é retângulo")
#             IS_RECT = 1
#         else:
#             IS_RECT = 0
#             IS_CAN = 0
            
#     if (IS_RECT == 1) and (IS_CAN == 1):
#                 # Define ROI Box Dimensions (Note some of these things should be outside the loop)
#         top_left_x = int(width / 3)
#         top_left_y = int((height / 2) + (height / 4))
#         bottom_right_x = int((width / 3) * 2)
#         bottom_right_y = int((height / 2) - (height / 4))
#             # Draw rectangular window for our region of interest
#         cv2.rectangle(frame, (top_left_x,top_left_y), (bottom_right_x,bottom_right_y), 255, 3)
#         cropped = frame[bottom_right_y:top_left_y , top_left_x:bottom_right_x]
#             # Flip frame orientation horizontally
#             #frame = cv2.flip(frame,1)
#         matches = ORB_detector(cropped, image_template)
#             # Display status string showing the current no. of matches 
#         output_string = "Matches = " + str(matches)
#         cv2.putText(frame, output_string, (50,450), cv2.FONT_HERSHEY_COMPLEX, 2, (250,0,150), 2)
#         threshold = 30
#             # If matches exceed our threshold then object has been detected
#         if matches > threshold:
#             cv2.rectangle(teste, (top_left_x,top_left_y), (bottom_right_x,bottom_right_y), (0,255,0), 3)
#             print("match")
#             cv2.putText(teste,'Object Found',(50,50), cv2.FONT_HERSHEY_COMPLEX, 2 ,(0,255,0), 2)
#             cv2.imshow('Object Detector using ORB', frame)
#             IS_COKE = 1
#         else:
#             IS_COKE = 0
#     cv2.imshow('Object Detector using ORB', frame)
#     key = cv2.waitKey(1)
#     if key == 27:
#         break

cap.release()
cv2.destroyAllWindows()
