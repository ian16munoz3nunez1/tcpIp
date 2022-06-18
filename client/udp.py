import socket
import cv2
import base64

class UDP:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port
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

            msg = cv2.imencode(".jpg", video, [cv2.IMWRITE_JPEG_QUALITY, 80])[1]
            msg = base64.b64encode(msg)
            self.__sock.sendto(msg, self.__addr)
        captura.release()

    def close(self):
        self.__sock.close()
