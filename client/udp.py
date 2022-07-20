## Client
import socket
import cv2
import base64
import time

class UDP:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.__chunk = 64*1024
        self.__addr = (self.__host, self.__port)

        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1)
        self.__sock.settimeout(3)

    def conectar(self):
        self.__sock.sendto(''.encode(), self.__addr)

    def captura(self, camara):
        captura = cv2.VideoCapture(camara, cv2.CAP_DSHOW)
        while True:
            leido, video = captura.read()
            if not leido:
                break

            height, width = video.shape[:2]
            x = 6
            y = height-10
            widthS = x-5
            widthF = widthS+298
            heightS = y-22
            heightF = y+8

            cv2.rectangle(video, (widthS, heightS), (widthF, heightF), (50, 50, 50), -1)
            cv2.putText(video, time.strftime("%Y/%m/%d %H:%M:%S"), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1, cv2.LINE_AA)

            msg = cv2.imencode(".jpg", video, [cv2.IMWRITE_JPEG_QUALITY, 80])[1]
            msg = base64.b64encode(msg)
            self.__sock.sendto(msg, self.__addr)

            msg = self.__sock.recvfrom(self.__chunk)
            if msg == "end":
                break
        captura.release()

    def close(self):
        self.__sock.close()
