import socket
import cv2
import numpy
import base64

class UDP:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.__chunk = 64*1024

        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1)
        self.__sock.bind((self.__host, self.__port))
        self.__sock.settimeout(3)

    def conectar(self):
        self.__addr = self.__sock.recvfrom(self.__chunk)[1]
        print("UDP conectado")

    def captura(self, userName):
        while True:
            info = self.__sock.recvfrom(self.__chunk)[0]
            info = base64.b64decode(info, ' /')
            matriz = numpy.frombuffer(info, dtype=numpy.uint8)
            video = cv2.imdecode(matriz, -1)

            cv2.imshow(f"{userName}@{self.__addr[0]}: Captura", video)

            if cv2.waitKey(1) == 27:
                break
        cv2.destroyAllWindows()

    def close(self):
        self.__sock.close()
        print("UDP desconectado")
