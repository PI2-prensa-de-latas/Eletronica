import cv2
import json
import numpy as np
import sys
import requests
import subprocess
from picamera.array import PiRGBArray
from picamera import PiCamera
from time import sleep
import RPi.GPIO as gpio
import time
from socket import gethostbyname,create_connection
from datetime import datetime

#Configurações
gpio.setmode(gpio.BCM)
font = cv2.FONT_HERSHEY_COMPLEX
camera = PiCamera()
camera.resolution = (640,480)
camera.framerate = 60
rawCapture = PiRGBArray(camera, size=(640, 480))
TOKEN = "bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MywiaWF0IjoxNTc1NDgxODk1fQ.7d0ZFRz-Dxhxxc6fipl2a7fxvdB1gSRUKInM4-OfLK4"
HEADERS = {'Authorization': TOKEN}
URL = 'https://api-producao.herokuapp.com/SmashedCan'

#Sensor de obstáculo Com pull-up interno
gpio.setup(26, gpio.IN, pull_up_down = gpio.PUD_UP) #Pino 33

#Sensor indutivo Com pull-up interno
gpio.setup(19, gpio.IN, pull_up_down = gpio.PUD_UP) #Pino 12

#iniciar reconhecimento de marca
image_template = cv2.imread('coca.jpg', 0)

#iniciar reconhecimento de forma
FOUND_RECT = 0
low = 85
up = 255

#iniciar relé e leds
gpio.setwarnings(False)
gpio.setup(5, gpio.OUT) #led verde gpio 5 pino 29
gpio.setwarnings(False)
gpio.output(5,gpio.LOW)

gpio.setwarnings(False)
gpio.setup(6, gpio.OUT) #led vermelho - objeto inválido gpio 6 pino 31
gpio.setwarnings(False)
gpio.output(6,gpio.LOW)

gpio.setwarnings(False)
gpio.setup(12, gpio.OUT) #relé gpio 12 pino 32
gpio.setwarnings(False)
gpio.output(12,gpio.LOW)

def ORB_detector(new_image, image_template):
    # Function that compares input image to template
    # It then returns the number of ORB matches between them
    image1 = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)
    # Create ORB detector with 1000 keypoints with a scaling pyramid factor of 1.2
    orb = cv2.ORB_create(5000, 1.2)
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


# Verifica se esta conectado a internet
def conectadoInternet():

    tentativas = 0
    servidorRemoto = 'www.google.com.br'

    while tentativas < 2:
        if tentativas == 1:
            servidorRemoto = 'http://159.65.236.163:8080/SmashedCan'
        elif tentativas == 2:
            servidorRemoto = 'www.msn.com'

        try:
            host = gethostbyname(servidorRemoto)
            s = create_connection((host, 80), 2)
            return True
        except: tentativas += 1

    return False

#iniciar auxiliares
TRAVADO = 0
BAIXO = 0
erro = 0


while True:
    
    if gpio.input(26) == gpio.LOW:
        #significa que ñ achou algum objeto
        NOT_METAL = 1
        print("não achou")
        TRAVADO = 0
       # gpio.output(12,gpio.LOW)
        i=0
        BAIXO = 0
    else:
        #significa que achou objeto
        NOT_METAL = 0
        print("achou")

    if gpio.input(19) == gpio.LOW:
         #significa que achou objeto metálico
         IS_CAN = 1
         print("metal")
    else:
         IS_CAN = 0
         print("não metal")
         TRAVADO = 0
         i=0
         BAIXO =0 
     
    if IS_CAN == 1 and NOT_METAL == 0 and TRAVADO == 0:
        gpio.output(12,gpio.HIGH)
        sleep(0.5)
        print("verifica forma")
        camera.capture('formato.png')
        out_shape = cv2.imread('formato.png')
        gray = cv2.cvtColor(out_shape,cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (23,21), 7)
        kernal = cv2.getStructuringElement(cv2.MORPH_RECT,(30,20))
        _,thresh = cv2.threshold(gray,low,up,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU )
        close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernal, iterations=1)
        erosion = cv2.erode(close,kernal,iterations=1)
        dilate = cv2.dilate(close,kernal,iterations=1)
        contours,_ = cv2.findContours(erosion,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for b in range(6) :
            cnt = contours[0]
            M = cv2.moments(cnt)
        #print('m',M)
            area = cv2.contourArea(cnt)
            approx = cv2.approxPolyDP(cnt, 0.05*cv2.arcLength(cnt,True),True)
            k = approx.ravel()[0]
            z = approx.ravel()[1]
            if (len(approx) == 4):
                break
        if area>50000 and area<83000: 
            cv2.drawContours(out_shape,[approx],-1,(0,255,0),3)
            if (len(approx)==4):
                k,z,width,height = cv2.boundingRect(approx)
                aspectRatio = width/float(height)
                print(aspectRatio)
                shape = "square" if aspectRatio >= 0.95 and aspectRatio <= 1.05 else "rectangle"
                cv2.putText(out_shape,shape,(k,z),font,2,(255,0,0))
                FOUND_RECT = 1
                print("id",FOUND_RECT)
                gpio.output(5,gpio.HIGH)
                
        else:
            print("não é o formato", len(approx), area)
            FOUND_RECT = 0
            TRAVADO = 1
            
    elif IS_CAN == 0 and NOT_METAL == 0:
         print('ñ metal e achou')
         TRAVADO = 1      
         
    elif IS_CAN == 1 and NOT_METAL == 1:
         print('metal e ñ achou')
         TRAVADO = 1
                    
    else:
        print("não verifica forma")

    if FOUND_RECT == 1:
        print("testa marca")
        sleep(0.5)
        camera.capture('marca.png')
        out_marca = cv2.imread('marca.png')
        hsv = cv2.cvtColor(out_marca, cv2.COLOR_BGR2HSV)
        kernel =np.ones((5,5),np.uint8)
        maskr1 =cv2.inRange(hsv,(0,50,20),(5,255,255))
        maskr2 = cv2.inRange(hsv,(175,50,20),(180,255,255))
        mask = cv2.bitwise_or(maskr1,maskr2)
        cropped1 = cv2.bitwise_and(out_marca, out_marca, mask=mask)
        opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        x,y,w,h =cv2.boundingRect(opening)
        print('x',x,w)
        if 100 < x < 200 or w > 250:
            height, width = out_marca.shape[:2]
            
            # Define ROI Box Dimensions (Note some of these things should be outside the loop)
            top_left_x = int(width / 3)
            top_left_y = int((height / 2) + (height / 4))
            bottom_right_x = int((width / 3) * 2)
            bottom_right_y = int((height / 2) - (height / 4))
            
            # Draw rectangular window for our region of interest
            cv2.rectangle(out_marca, (top_left_x,top_left_y), (bottom_right_x,bottom_right_y), 255, 3)

            # Crop window of observation we defined above
            cropped = out_marca[bottom_right_y:top_left_y , top_left_x:bottom_right_x]

            # Get number of ORB matches 
            matches = ORB_detector(cropped, image_template)
            
            # Display status string showing the current no. of matches 
            output_string = "Matches = " + str(matches)
            cv2.putText(out_marca, output_string, (50,450), cv2.FONT_HERSHEY_COMPLEX, 2, (250,0,150), 2)

            # Our threshold to indicate object deteciton
            # For new images or lightening conditions you may need to experiment a bit 
            # Note: The ORB detector to get the top 1000 matches, 350 is essentially a min 35% match
            threshold = 200
            
            # If matches exceed our threshold then object has been detected
            if matches >= threshold:
                print('coca')
                cv2.rectangle(out_marca, (top_left_x,top_left_y), (bottom_right_x,bottom_right_y), (0,255,0), 3)
                cv2.putText(out_marca,'Object Found',(50,50), cv2.FONT_HERSHEY_COMPLEX, 2 ,(0,255,0), 2)
                cv2.imshow('Object Detector using ORB', out_marca)
                gpio.output(5,gpio.LOW)
                gpio.output(12,gpio.LOW)
                BAIXO = 1
                print("abriu alçapão")
                sleep(3)
                subprocess.call("echo 5=130 > /dev/servoblaster", shell=True)
                sleep(1)
                subprocess.call("echo 5=200 > /dev/servoblaster", shell=True)
                print("fechou alçapão")
                sleep(0.5)
                subprocess.call("echo 5=0 > /dev/servoblaster", shell=True)
                #Enviar requisição
                if (conectadoInternet() == True):
                    p=0
                    if (erro > 0):
                        while p > erro+1:
                            p += 1
                            url = "https://putsreq.com/nIKlJKlF3cbd3qwfZPqH"
                            body = {"user":1,"machine":"1","canCategory":2}
                            post_user = requests.post(URL,data=json.dumps(body),headers=HEADERS)
                            print('----Resultado da requisição----')
                            print(post_user.json())
                        
                    else:
                        url = "https://putsreq.com/nIKlJKlF3cbd3qwfZPqH"
                        body = {"user":1,"machine":"1","canCategory":2}
                        post_user = requests.post(URL,data=json.dumps(body),headers=HEADERS)
                        print('----Resultado da requisição----')
                        print(post_user)
                        erro=0
                else:
                    now = datetime.now()
                    data = now.strftime('%d/%m/%Y %H:%M')
                    lista = [data]
                    erro += 1
                    if (erro > 1):
                        lista += lista
                    print(erro)
                    print(lista)
                
                
                FOUND_RECT = 0
                IS_CAN = 0
                NOT_METAL = 1
            else:
                print('não é coca')
                gpio.output(5,gpio.LOW)
                gpio.output(12,gpio.LOW)
                BAIXO = 1
                print("abriu alçapão")
                sleep(0.5)
                subprocess.call("echo 5= 130 > /dev/servoblaster", shell=True)
                sleep(1)
                subprocess.call("echo 5=200 > /dev/servoblaster", shell=True)
                print("fechou alçapão")
                sleep(0.5)
                subprocess.call("echo 5=0 > /dev/servoblaster", shell=True)
                #Enviar requisição
                if (conectadoInternet() == True):
                    p=0
                    if (erro > 0):
                        while p > erro+1:
                            p += 1
                            url = "https://putsreq.com/nIKlJKlF3cbd3qwfZPqH"
                            body = {"user":1,"machine":"1","canCategory":1}
                            post_user = requests.post(URL,data=json.dumps(body),headers=HEADERS)
                            print('----Resultado da requisição----')
                            print(post_user.json())
                        
                    else:
                        url = "https://putsreq.com/nIKlJKlF3cbd3qwfZPqH"
                        body = {"user":1,"machine":"1","canCategory":1}
                        post_user = requests.post(URL,data=json.dumps(body),headers=HEADERS)
                        print('----Resultado da requisição----')
                        print(post_user.json())
                        erro=0
                        
                else:
                    now = datetime.now()
                    data = now.strftime('%d/%m/%Y %H:%M')
                    lista = [data]
                    erro += 1
                    if (erro > 1):
                        lista += lista
                    print(erro)
                    print(lista)
    #             
    #             
                FOUND_RECT = 0
                IS_CAN = 0
                NOT_METAL = 1
                             
        else:
            print('não é coca')
            gpio.output(5,gpio.LOW)
            gpio.output(12,gpio.LOW)
            BAIXO = 1
            print("abriu alçapão")
            sleep(0.5)
            subprocess.call("echo 5= 130 > /dev/servoblaster", shell=True)
            sleep(1)
            subprocess.call("echo 5=200 > /dev/servoblaster", shell=True)
            print("fechou alçapão")
            sleep(0.5)
            subprocess.call("echo 5=0 > /dev/servoblaster", shell=True)
            
            #Enviar requisição
            if (conectadoInternet() == True):
                p=0
                if (erro > 0):
                    while p > erro+1:
                        p += 1
                        url = "https://putsreq.com/nIKlJKlF3cbd3qwfZPqH"
                        body = {"user":1,"machine":"1","canCategory":1}
                        post_user = requests.post(URL,data=json.dumps(body), headers=HEADERS)
                        print('----Resultado da requisição----')
                        print(post_user.json())
                    
                else:
                    url = "https://putsreq.com/nIKlJKlF3cbd3qwfZPqH"
                    body = {"user":1,"machine":"1","canCategory":1}
                    post_user = requests.post(URL,data=json.dumps(body), headers=HEADERS)
                    print('----Resultado da requisição----')
                    print(post_user.json())
                    erro=0
                    
            else:
                now = datetime.now()
                data = now.strftime('%d/%m/%Y %H:%M')
                lista = [data]
                erro += 1
                if (erro > 1):
                    lista += lista
                print(erro)
                print(lista)
    #             
    #             
            FOUND_RECT = 0
            IS_CAN = 0
            NOT_METAL = 1
            
            
    else:
        print("não testa")
        gpio.output(12,gpio.LOW)
        
    if TRAVADO == 1:
        gpio.output(6,gpio.HIGH)
        gpio.output(12,gpio.LOW)
    else:
        gpio.output(6,gpio.LOW)
        
    if BAIXO == 1:
        sleep(1)
        subprocess.call("echo 6=80 > /dev/servoblaster", shell=True)
        sleep(0.5)
        subprocess.call("echo 6=80 > /dev/servoblaster", shell=True)
        print('0')
        sleep(3)
        print('7')
        subprocess.call("echo 6=250 > /dev/servoblaster", shell=True)
        sleep(0.5)
        subprocess.call("echo 6=250 > /dev/servoblaster", shell=True)
        sleep(0.5)
        print('0')
        subprocess.call("echo 6=0 > /dev/servoblaster", shell=True)
        BAIXO = 0


    sleep(2) 
    key = cv2.waitKey(1)
    if key == 27:
        break
    
gpio.cleanup()
