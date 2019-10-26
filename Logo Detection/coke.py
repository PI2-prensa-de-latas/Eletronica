import numpy as np
import cv2
import time

coke_cascade = cv2.CascadeClassifier('haarcascade_coke2.xml')
font = cv2.FONT_HERSHEY_COMPLEX

cv2.namedWindow("drawing")
rejectLevels = []
levelWeights = []

vc = cv2.VideoCapture(0)

def nothing(x):
    pass
startA = 100
startB = 200
cv2.createTrackbar('MIN','img',startA,1000,nothing)
cv2.createTrackbar('MAX','img',startB,1000,nothing)

while (1):
    a = cv2.getTrackbarPos('MIN','img')
    b = cv2.getTrackbarPos('MAX','img')
    
    _,frame = vc.read()
#     frame_horizontal = cv2.flip(frame, 0)
#     frame_vertical = cv2.flip(frame, 1)
#     frame_ambos = cv2.flip(frame, -1)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     gray2 = cv2.cvtColor(frame_horizontal, cv2.COLOR_BGR2GRAY)
#     gray3 = cv2.cvtColor(frame_vertical, cv2.COLOR_BGR2GRAY)
#     gray4 = cv2.cvtColor(frame_ambos, cv2.COLOR_BGR2GRAY)
    cokes = coke_cascade.detectMultiScale(gray,scaleFactor=1.5, minNeighbors=6,minSize=(30, 30))
   # cokes = coke_cascade.detectMultiScale(frame,1.3,6)
#     cokes2 = coke_cascade.detectMultiScale(gray2, 1.3, 5)
#     cokes3 = coke_cascade.detectMultiScale(gray3, 1.3, 5)
#     cokes4 = coke_cascade.detectMultiScale(gray4, 1.3, 5)
    
    #for (x,y,w,h) in [cokes,cokes2,cokes3,cokes4]:
    for (x,y,w,h) in cokes:
#        (cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2) or cv2.rectangle(frame_horizontal, (x,y), (x+w, y+h), (0,255,0), 2) or cv2.rectangle(frame_vertical, (x,y), (x+w, y+h), (0,255,0), 2) or cv2.rectangle(frame_ambos, (x,y), (x+w, y+h), (0,255,0), 2))
        (cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)) 
        cv2.putText(frame,"COCA COLA",(x,y),font,0.3,(0,255,0))
        print ("coke")
    
    cv2.imshow("drawing", frame)

    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break

cv2.destroyAllWindows()
