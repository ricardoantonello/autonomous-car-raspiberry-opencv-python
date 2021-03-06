# coding: utf-8
# Autor: Ricardo Antonello 
# Site: cv.antonello.com.br
# E-mail: ricardo@antonello.com.br

# import the necessary packages
import time
import cv2
import serial
import time

#Imports para a funcao preprocessamento1()
import numpy as np
from skimage import morphology
from skimage.morphology import skeletonize
from skimage.morphology import medial_axis

#Imports para a funcao calcula_angulo
from math import atan, pi

# Definições globais
ser = serial.Serial('/dev/ttyUSB0', 9600)
global_threshold=20

def re():
    ser.write(str('-1').encode())
    ser.flush()
def parar():
    ser.write(str('0').encode())
    ser.flush()
def frente():
    ser.write(str('1').encode())
    ser.flush()
def direita():
    ser.write(str('2').encode())
    ser.flush()
def esquerda():
    ser.write(str('3').encode())
    ser.flush()

def texto(img, texto, coord, fonte = cv2.FONT_HERSHEY_SIMPLEX, cor=(0,0,255), tamanho=0.5, thickness=2):
    textSize, baseline = cv2.getTextSize(texto, fonte, tamanho, thickness);
    cor_background = 0
    if type(cor)==int: # se não for colorida a imagem
        cor_background=255-cor
    else:
        cor_background=(0,255,255)
    #print(cor_background)
    cv2.rectangle(img, (coord[0], coord[1]-textSize[1]-3), (coord[0]+textSize[0], coord[1]+textSize[1]-baseline), cor_background, -1)
    #cv2.putText(img, texto, coord, fonte, tamanho, cor_background, thickness+1, cv2.LINE_AA)
    cv2.putText(img, texto, coord, fonte, tamanho, cor, thickness, cv2.LINE_AA)
    return img

def preprocessamento1(im):
    #Aplicação do Skeleton na imagem
    s = cv2.GaussianBlur(im, (15, 15), 0)
    im = cv2.Canny(s, 50, 150)

    #print(canny)
    
    #Retira 30 pixels das bordas para evitar distorção 
    im=im[30:-30,30:-30] #Retira da imagem uma borda de 30 pixels
    #im=im.astype(np.int32) #Converte imagem para 'int32'
    return im

def calculo_angular_artigo_2016(im):
    #Varre a imagem em sentido vertical em 10 pontos equidistantes
    h, w = im.shape; 
    print("Imagem reduzida para processamento: Largura:", w, " Altura:", h, "Tipo:", im.dtype, type(im))
    pontos = []; #Vetor que armazena os pontos encontrados na imagem

    #Percorre a imagem na horizontal em 10 pontos distintos 
    intervalo = h / 9; #divide a altura em 9 partes para percorrer a imagem em 10 pontos diferentes 
    #print('Intervalo=',intervalo)
    for i in range(0,10):
        for j in range(w):
            temp = 0
            temp = i*intervalo if i*intervalo < h else h-1
            if im[int(temp),int(j)]==1:
                pontos.append([i*intervalo,j])      
                #print i*intervalo, j#imprime pontos, útil durante depuração do código
                im[i*intervalo:i*intervalo+4,j:j+4]=120; #marca o ponto encontrado na imagem

    #Percorre a imagem na vertical
    intervalo = w / 9; #divide a largura em 9 partes para percorrer a imagem em 10 pontos diferentes 
    #print('Intervalo=',intervalo)
    for j in range(0,10):
        for i in range(h):
            temp = 0
            temp = j*intervalo if j*intervalo < w else w-1
            if im[i,temp]==1:
                pontos.append([i,j*intervalo])      
                #print i, j*intervalo #imprime pontos, útil durante depuração do código
                im[i:i+4,j*intervalo:j*intervalo+4]=120; #marca o ponto encontrado na imagem

    #Verifica se encontrou ao menos 4 pontos para realizar calculo
    angulo = []; #vetor para armazenar os calculos
    if len(pontos)>=4:
        #Realiza o cálculo do primeiro ponto com o ultimo
        y = pontos[0][0]-pontos[len(pontos)-1][0];
        x = pontos[0][1]-pontos[len(pontos)-1][1];
        if x!=0: #Verifica se divisor é zero e se for considera angula de 90 graus
            anguloRad= atan(y*(-1)/float(x));
        else:
            anguloRad = pi/2;
        angulo.append((anguloRad*180) / pi);
        print('***************\nCalculo 1/2: Radianos', anguloRad, 'Ângulo em graus', angulo[0])
        
        #Realiza o cálculo do segundo ponto com o penultimo
        y = pontos[1][0]-pontos[len(pontos)-2][0];
        x = pontos[1][1]-pontos[len(pontos)-2][1];
        if x!=0: #Verifica se divisor é zero e se for considera angula de 90 graus
            anguloRad= atan(y*(-1)/float(x));
        else:
            anguloRad = pi/2;
        angulo.append((anguloRad*180) / pi);
        print('Calculo 2/2: Radianos', anguloRad, 'Ângulo em graus', angulo[1])
        #Como trabalhos futuros podemos melhorar o calculo dos angulos 
        #em relação aos pontos visando melhorar a precisão.

        #Calcula a média
        angulo = (angulo[0] + angulo[1]) / 2.0;
        print('***************\nÂngulo em graus', angulo,'\n***************')
    else:
        print('\n***************\nImpossível calcular o angulo\n***************')


def angulo(img):
       gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
       edges = cv2.Canny(gray,50,150,apertureSize = 3)
       lines = cv2.HoughLines(edges,1,np.pi/180,100)
       #quanto a linha esta quase reta (90 graus) o resultado é 0,99 ou -0,99
       #entao contamos a maioria para fazer a média dividindo certo
       cont_pos=0 # positivos 
       cont_neg=0 # negativos
       a_acum_pos=0
       a_acum_neg=0
       a_final=0
       if lines!=None:
         for line in lines:
           for rho,theta in line:
             a = np.cos(theta) # só usa essa informação
             b = np.sin(theta)
             x0 = a*rho
             y0 = b*rho
             x1 = int(x0 + 1000*(-b))
             y1 = int(y0 + 1000*(a))
             x2 = int(x0 - 1000*(-b))
             y2 = int(y0 - 1000*(a))
             if a>0:
                 a_acum_pos+=a
                 cont_pos+=1
             else:
                 a_acum_neg+=a
                 cont_neg+=1
             cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)
             print('n:',int(a*1000))
             
         if cont_pos>=cont_neg:
             a_final=int(a_acum_pos/cont_pos*1000)
         else:
             a_final=int(a_acum_neg/cont_neg*1000)
       else:
           a_final = 0
           print('\n***************\nImpossível calcular o angulo2\n***************')

       print('np.cos(theta):',a_final)
       return img
    
def angulo_completo(img):
       gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
       edges = cv2.Canny(gray,50,150,apertureSize = 3)
       lines = cv2.HoughLines(edges,1,np.pi/180,100)
       rho_acum=0
       if lines!=None:
        for line in lines:
         for rho,theta in line:
           a = np.cos(theta) # só usa essa informação
           b = np.sin(theta)
           x0 = a*rho
           y0 = b*rho
           x1 = int(x0 + 1000*(-b))
           y1 = int(y0 + 1000*(a))
           x2 = int(x0 - 1000*(-b))
           y2 = int(y0 - 1000*(a))
           cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)
           print('rho',rho)
           print('theta',theta)
           print('a',a)
           print('b',b)
           print('x0',x0)
           print('y0',y0)
       else:
           print('\n***************\nImpossível calcular o angulo2\n***************')
       return img

def angulo_misto(img):
       gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
       #edges = cv2.Canny(gray, 75, 150)
       edges = cv2.Canny(gray, 50, 150)
       lines = cv2.HoughLinesP(edges, 1, np.pi/180, 30, maxLineGap=250)
         
       if lines!=None:
         for line in lines:
           x1, y1, x2, y2 = line[0]
           cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
           cv2.circle(img, (x1,y1), 5, (0, 255, 0), 1)
           cv2.circle(img, (x2,y2), 5, (0, 255, 0), 1)
       cv2.imshow("Edges", edges)

       #INICIO CALCULO DOS ANGULOS
       #Verifica se encontrou ao menos 4 pontos para realizar calculo
       angulos = []; #vetor para armazenar os calculos
       angulo_medio=0
       if lines!=None:
           for line in lines:
                x1, y1, x2, y2 = line[0]

                #Realiza o cálculo do primeiro ponto com o ultimo
                y = y2-y1
                x = x2-x1
                if x!=0: #Verifica se divisor é zero e se for considera angula de 90 graus
                    anguloRad= atan(y*(-1)/float(x));
                else:
                    anguloRad = pi/2;
                anguloGraus = (anguloRad*180) / pi
                angulos.append(anguloGraus);
                print('***************\nCalculo: Radianos', anguloRad, 'Ângulo em graus', anguloGraus)

           #Calcula a média
           for a in angulos:
               angulo_medio += a
               #print('angulo',a)
           angulo_medio = angulo_medio/len(angulos) # calcula a media
           print('***************\nÂngulo em graus', angulo_medio,'\n***************')
       else:
           print('\n***************\nImpossível calcular o angulo\n***************')

       #FIM DO CALCULOS DOS ANGULOS
       return img

try:
     from picamera.array import PiRGBArray
     from picamera import PiCamera
     
     # initialize the camera and grab a reference to the raw camera capture
     camera = PiCamera()
     camera.resolution = (320, 240) #camera.resolution = (640, 480)
     camera.framerate = 32
     rawCapture = PiRGBArray(camera, size=(320, 240)) #rawCapture = PiRGBArray(camera, size=(640, 480))
      
     # allow the camera to warmup
     time.sleep(0.1)
      
     # capture frames from the camera
     for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
       # grab the raw NumPy array representing the image, then initialize the timestamp
       # and occupied/unoccupied text
       img = frame.array
       img = img[::-1,::-1,::].copy()
       
       #INICIO DO ALGORITMO DE RECONHECIMENTO

       #i = preprocessamento1(i)
       #calculo_angular(i)
       #break


       
       #FIM DO ALGORITMO DE RECONHECIMENTO

       img = angulo(img)

       
       # show the frame
       cv2.imshow("Frame", img)
       key = cv2.waitKey(1) & 0xFF
       # clear the stream in preparation for the next frame
       rawCapture.truncate(0)
       # if the `q` key was pressed, break from the loop
       if key == ord("q"):
         cv2.destroyAllWindows()
         break
except ImportError:
     print('Não esta rodando em um Raspberry')

