import cv2
import numpy as np
def nothing(x):
    pass

cam = cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_COMPLEX
FOUND_RECT = 0
low = 90
up = 255

while(1):
    _,image = cam.read()
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    gaussian1 = cv2.GaussianBlur(gray, (7,7), 0)
    #gaussian2 = cv2.medianBlur(gray,5)
    kernal = cv2.getStructuringElement(cv2.MORPH_RECT,(10,10))
    _,thresh = cv2.threshold(gray,low,up,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU )
    #_,thresh = cv2.threshold(gaussian,low,up,cv2.THRESH_BINARY_INV)
    #kernal = cv2.getStructuringElement(cv2.MORPH_RECT,(10,10))
    #kernal = np.ones((5, 5), np.uint8)
    erosion = cv2.erode(thresh,kernal,iterations=1)
    dilate = cv2.dilate(thresh,kernal,iterations=1)
    contours,_ = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        approx = cv2.approxPolyDP(cnt, 0.03*cv2.arcLength(cnt,True),True)
        x = approx.ravel()[0]
        y = approx.ravel()[1]

        if area>5000:
            cv2.drawContours(image,[approx],-1,(0,255,0),2)
            if (len(approx)==4):
                x,y,width,height = cv2.boundingRect(approx)
                aspectRatio = width/float(height)
                print(aspectRatio)
                #if aspectRatio <= 0.9 and aspectRatio >=1.1:
                shape = "square" if aspectRatio >= 0.95 and aspectRatio <= 1.05 else "rectangle"
                cv2.putText(image,shape,(x,y),font,2,(255,0,0))
                FOUND_RECT = 1
                print("id",FOUND_RECT)
                #else:
                   # print("não é retângulo")
            else:
                print("não é o formato")
        else:
            print ("fora da área",area)
    cv2.imshow("shape cam",image)
    cv2.imshow("threshold",thresh)
    cv2.imshow("dilate",dilate)
    #cv2.imshow("erode",erosion)
 

    if cv2.waitKey(1)==27:
        break
cam.release()
cv2.destroyAllWindows()