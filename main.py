from ast import Str
import pytesseract
import cv2
pytesseract.pytesseract.tesseract_cmd = "C:\Program Files (x86)\Tesseract-OCR\\tesseract.exe"


def desenhaContornos(contornos, imagem):
    for c in contornos:
        # perimetro do contorno, verifica se o contorno é fechado
        perimetro = cv2.arcLength(c, True)
        if perimetro > 120:
            # aproxima os contornos da forma correspondente
            approx = cv2.approxPolyDP(c, 0.03 * perimetro, True)
            # verifica se é um quadrado ou retangulo de acordo com a qtd de vertices
            if len(approx) == 4:
                # Contorna a placa atraves dos contornos encontrados
                (x, y, lar, alt) = cv2.boundingRect(c)
                cv2.rectangle(imagem, (x, y), (x + lar, y + alt), (0, 255, 0), 2)
                # segmenta a placa da imagem
                roi = imagem[(y + 14):y + (lar - 7), (x + 6) :x + (alt - 10)]
                #cv2.imwrite("output/roi.png", roi)
                return roi


def buscaRetanguloPlaca(source):
    # Captura ou Video
    video = cv2.VideoCapture(source)
    cont = 0
    while video.isOpened():
        ret, frame = video.read()
        if (cont % 1 == 0):
            print (cont)
            print (ret)

            if (ret == False):
                break

            # area de localização u 720p
            area = frame[500:, 300:800]

            # area de localização 480p
            #area = frame[350:, 220:500]

            # escala de cinza
            img_result = cv2.cvtColor(area, cv2.COLOR_BGR2GRAY)

            # limiarização
            ret, img_result = cv2.threshold(img_result, 90, 255, cv2.THRESH_BINARY)

            # desfoque
            img_result = cv2.GaussianBlur(img_result, (5, 5), 0)

            # lista os contornos
            contornos, hier = cv2.findContours(img_result, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

            # limite horizontal
            cv2.line(frame, (0, 500), (1280, 500), (0, 0, 255), 1)
            # limite vertical 1
            cv2.line(frame, (300, 0), (300, 720), (0, 0, 255), 1)
            # limite vertical 2
            cv2.line(frame, (800, 0), (800, 720), (0, 0, 255), 1)

            cv2.imshow('FRAME', frame)

            roi = desenhaContornos(contornos, area)                       
            roi_ocr = preProcessamentoRoi(roi)

            if roi_ocr is None:
             print("roi_ocr is none")             
            else:
                print("else")
                placa = reconhecimentoOCR(roi_ocr)
                cv2.putText(area, placa, (50,50), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0,255,0), cv2.LINE_4)
                cv2.putText(area, str(cont), (200,200), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0,255,0), cv2.LINE_4)
                cv2.imshow('RES', area)            
                if cv2.waitKey(1) & 0xff == ord('q'):            
                    break
        cont = cont + 1        
    video.release()    
    cv2.destroyAllWindows()
    

def preProcessamentoRoi(roi):
    #img_roi = cv2.imread("output/roi.png")
    img_roi = []
    img_roi = roi
    # cv2.imshow("ENTRADA", img_roi)
    if img_roi is None:
        print("none preProcessamentoRoi")
        return
    if len(img_roi) <= 1:
        print("not img_roi")
        return
        
    # redmensiona a imagem da placa em 4x
    print (len(img_roi))
    print(img_roi)
    img = cv2.resize(img_roi, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)

    # Converte para escala de cinza
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("Escala Cinza", img)

    # Binariza imagem
    _, img = cv2.threshold(img, 70, 255, cv2.THRESH_BINARY)
    #cv2.imshow("Limiar", img)

    # Desfoque na Imagem
    img = cv2.GaussianBlur(img, (5, 5), 0)
    # cv2.imshow("Desfoque", img)

    # Aplica reconhecimento OCR no ROI com o Tesseract
    #cv2.imwrite("output/roi-ocr.png", img)
    #cv2.imshow('pre roi', img)
    return img


def reconhecimentoOCR(roi_ocr):
    img_roi_ocr = roi_ocr
    #img_roi_ocr = cv2.imread("output/roi-ocr.png")
    if img_roi_ocr is None:
        print("none OCR")
        return

    config = r'-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 --psm 6'
    saida = pytesseract.image_to_string(img_roi_ocr, lang='eng', config=config)

    #print(saida)
    return saida


if __name__ == "__main__":
    source = "resources/uefs1-720p.mp4"

    buscaRetanguloPlaca(source)

