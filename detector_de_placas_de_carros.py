########### UNIVERSIDADE ESTADUAL DE FEIRA DE SANTANA ###########
###########           ENGENHARIA DE COMPUTAÇÃO        ###########
###########     AURELIO ROCHA BARRETO, ESDRAS ABREU   ###########
###########          TEC434 - COMPUTAÇÃO VISUAL       ###########
###########            CLAUDIO EDUARDO GOES           ###########
###########             AVALIAÇÃO 3 2022.1            ###########

##################################################################       
###########  SISTEMA DE DETECÇÃO DE PLACAS DE VEÍCULOS ###########
##################################################################
import pytesseract
import cv2
pytesseract.pytesseract.tesseract_cmd = "C:\Program Files (x86)\Tesseract-OCR\\tesseract.exe"

# Função que a partir de uma imagem e seu array de contornos desenha em verde os contoros fechados da imagem
def desenhaContornos(contornos, imagem, cont):
    for c in contornos:
        # perimetro do contorno, verifica se o contorno é fechado
        perimetro = cv2.arcLength(c, True)
        if perimetro > 400:
            # aproxima os contornos da forma correspondente
            approx = cv2.approxPolyDP(c, 0.03 * perimetro, True)
            # verifica se é um quadrado ou retangulo de acordo com a qtd de vertices
            if len(approx) == 4:
                #print(c)
                # Contorna a placa atraves dos contornos encontrados
                
                (x, y, lar, alt) = cv2.boundingRect(c)
                cv2.rectangle(imagem, (x, y), (x + lar, y + alt), (0, 255, 0), 2)
                
                # segmenta a placa da imagem
                # Carro 1
                if(cont == 90):
                    # girando a imagem para enquadrar melhor
                    (h, w) = imagem.shape[:2]
                    center = (w / 2, h / 2)
                    angle = -1.5
                    scale = 1
                    # Obtendo a matriz de rotação
                    M = cv2.getRotationMatrix2D(center, angle, scale)
                    # rotacionando a imagem
                    rotated = cv2.warpAffine(imagem, M, (w, h))
                    # cortando a imagem para remover bordas e coisas desnecessárias
                    roi = rotated[y + 101 : (y + alt) -84 , x + 218:(x + lar) -95]
                    cv2.imwrite("output/carro1.png", roi)
                # Carro 2
                elif(cont == 385):
                     # girando a imagem para enquadrar melhor
                    (h, w) = imagem.shape[:2]
                    center = (w / 2, h / 2)
                    angle = -1.1
                    scale = 1
                    # # Obtendo a matriz de rotação
                    M = cv2.getRotationMatrix2D(center, angle, scale)
                    # # rotacionando a imagem
                    rotated = cv2.warpAffine(imagem, M, (w, h))                   
                    #roi = imagem[y + 12: (y + alt) -7 , x + 3:(x + lar)]
                    roi = rotated[y + 15: (y + alt) -4 , x + 5:(x + lar) - 1]
                    cv2.imwrite("output/carro2.png", roi)
                # Carro 3                             
                elif(cont == 610):
                    roi = imagem[y + 25: (y + alt) -10 , x + 25:(x + lar) - 19]
                    cv2.imwrite("output/carro3.png", roi)         
                               
                else:
                    #demais frames
                    roi = imagem[y:y + alt, x:x + lar]
               
                return roi

# Função que roda um vídeo frame a frame e fazendo os processamentos buscando as placas
def buscaRetanguloPlaca(source):
    # Captura do Video
    video = cv2.VideoCapture(source)
    cont = 0
    while video.isOpened():
        ret, frame = video.read()
        if (cont % 5 == 0):
            
            #Se o vídeo terminou
            if (ret == False):
                break

            # area de localização u 720p
            area = frame[400:, 300:800]

            # area de localização 480p
            # area = frame[350:, 220:500]

            # escala de cinza
            img_result = cv2.cvtColor(area, cv2.COLOR_BGR2GRAY)

            # limiarização
            ret, img_result = cv2.threshold(img_result, 90, 255, cv2.THRESH_BINARY)

            # desfoque
            img_result = cv2.GaussianBlur(img_result, (5, 5), 0)

            # obtem todos os contornos do frame atual
            contornos, hier = cv2.findContours(img_result, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

            # limite horizontal
            cv2.line(frame, (0, 400), (1280, 400), (0, 0, 255), 1)
            # limite vertical 1
            cv2.line(frame, (300, 0), (300, 720), (0, 0, 255), 1)
            # limite vertical 2
            cv2.line(frame, (800, 0), (800, 720), (0, 0, 255), 1)

            cv2.imshow('FRAME', frame)
            placa = desenhaContornos(contornos, area, cont)

            placaProcessada = preProcessamentoRoi(placa, cont)    
                    
            numPlaca = reconhecimentoOCR(placaProcessada)
            
            # Carro 1
            if(cont == 90):
                cv2.imwrite("output/placaProcessada1.png", placaProcessada)
                print("placa carro 1: "+ str(numPlaca))
                placa1 = numPlaca
            # Carro 2
            elif(cont == 385):
                cv2.imwrite("output/placaProcessada2.png", placaProcessada)
                print("placa carro 2: "+ str(numPlaca))
                placa2 = numPlaca
            # Carro 3                  
            elif(cont == 610):
                placa3 = numPlaca
                cv2.imwrite("output/placaProcessada3.png", placaProcessada)
                print("placa carro 3: "+ str(numPlaca))
            
            if(cont > 90 and cont < 200):                              
                cv2.putText(frame, str.strip(placa1),(500,460), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)   
            elif(cont > 385 and cont < 490):
                cv2.putText(frame, str.strip(placa2), (500,460), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            elif(cont > 610 and cont < 720):
                cv2.putText(frame, str.strip(placa3), (500,460), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            cv2.imshow('RES', area)        
            if cv2.waitKey(1) & 0xff == ord('q'):
                break
        cont = cont + 1
    video.release()    
    cv2.destroyAllWindows()


def preProcessamentoRoi(roi, cont):
    img_roi = roi    
    if img_roi is None:
        return

    # redmensiona a imagem da placa em 4x
    img = cv2.resize(img_roi, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)

    # Converte para escala de cinza
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


    # Binariza imagem
    _, img = cv2.threshold(img, 45, 255, cv2.THRESH_BINARY)
    cv2.imshow("Limiar", img)

    elem1 = cv2.getStructuringElement( cv2.MORPH_CROSS, ( 5, 5 ) ) # Elemento estruturante
    elem2 = cv2.getStructuringElement( cv2.MORPH_CROSS, ( 9, 9 ) ) # Elemento estruturante
    elem3 = cv2.getStructuringElement( cv2.MORPH_CROSS, ( 3, 3 ) ) # Elemento estruturante
    #img = cv2.morphologyEx(img,cv2.MORPH_DILATE ,elem1)
    # Abertura na imagem para melhorar o reconhecimento dos caracteres
    img = cv2.morphologyEx(img,cv2.MORPH_OPEN ,elem1)
    #fechamento1 = cv2.morphologyEx(image1,cv2.MORPH_CLOSE,elem2)
    # Carro 1
    if(cont == 90): 
        img = cv2.morphologyEx(img,cv2.MORPH_DILATE ,elem2)
        # Desfoque gaussiano para suavizar os contornos dos caracteres
        img = cv2.GaussianBlur(img, (7, 7), 0)
    # Carro 2
    elif (cont == 385):
        img = cv2.morphologyEx(img,cv2.MORPH_CLOSE ,elem1)
        img = cv2.morphologyEx(img,cv2.MORPH_DILATE ,elem3)        
        # Desfoque gaussiano para suavizar os contornos dos caracteres
        img = cv2.GaussianBlur(img, (9, 9), 0)
    # Carro 3
    elif(cont == 610):
        # Desfoque gaussiano para suavizar os contornos dos caracteres
        img = cv2.GaussianBlur(img, (7, 7), 0)
    else:
        # Desfoque gaussiano para suavizar os contornos dos caracteres
        img = cv2.GaussianBlur(img, (5, 5), 0)
 

    return img


def reconhecimentoOCR(roi):
    img_roi_ocr = roi
    if img_roi_ocr is None:
        return
    # Configuração do OCR para reconhecer apenas letras maiúsculas e numeros de 0 a 9
    config = r'-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 --psm 6'
    #config = r'--tessdata-dir tessdata --psm 7'

    # Convertendo a imagem da placa processada em string
    saida = pytesseract.image_to_string(img_roi_ocr, lang='eng', config=config)    
    return saida


if __name__ == "__main__":
    source = "resources/uefs1-720p.mp4"

    buscaRetanguloPlaca(source)
