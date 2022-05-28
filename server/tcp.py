import socket
import os
import re
import pickle
import struct
import cv2
import numpy
from time import sleep
from colorama import init
from colorama.ansi import Fore

init(autoreset=True)

class TCP:
    def __init__(self, host, port, chunk):
        self.__host = host
        self.__port = port

        if chunk <= 0 or chunk > 10:
            self.__chunk = 1024
        else:
            self.__chunk = chunk * 1024

        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.__sock.bind((self.__host, self.__port))
        self.__sock.listen(1)
        print(Fore.CYAN + f"[*] Esperando conexion en el puerto {self.__port}")

        self.__conexion, self.__addr = self.__sock.accept()
        print(Fore.GREEN + f"[+] Conexion establecida con {self.__addr[0]}")

        sleep(0.05)
        self.__conexion.send(str(self.__chunk).encode())
        info = self.__conexion.recv(1024).decode()
        info = info.split('\n')
        self.__userName = info[0]
        self.__hostName = info[1]
        self.__currentDir = info[2]

    def terminal(self):
        print(Fore.GREEN + "\u250c\u2500\u2500(" + Fore.BLUE + f"{self.__userName}~{self.__hostName}" + Fore.GREEN + ")-[" + Fore.WHITE + self.__currentDir + Fore.GREEN + ']')
        print(Fore.GREEN + "\u2514\u2500" + Fore.BLUE + "> ", end='')

    def getNombre(self, ubicacion):
        nombre = os.path.abspath(ubicacion)
        nombre = os.path.basename(nombre)
        return nombre

    def escalar(self, height, width):
        if height > width:
            escala = 500/height
        elif width > height:
            escala = 400/width
        else:
            escala = (height+width)/2
            escala = 500/escala

        return escala

    def recibirDatos(self):
        data = b''
        size = struct.calcsize('Q')
        while len(data) < size:
            info = self.__conexion.recv(self.__chunk)
            data += info

        dataSize = data[:size]
        data = data[size:]
        byteSize = struct.unpack('Q', dataSize)[0]

        while len(data) < byteSize:
            data += self.__conexion.recv(self.__chunk)

        info = data[:byteSize]
        data = data[byteSize:]
        info = pickle.loads(info)

        return info

    def enviarArchivo(self, ubicacion):
        tam = os.path.getsize(ubicacion)
        paquetes = int(tam/self.__chunk)
        print(Fore.CYAN + f"[*] Paquetes estimados: {paquetes}")

        sleep(0.1)
        i = 1
        with open(ubicacion, 'rb') as archivo:
            info = archivo.read(self.__chunk)
            while info:
                self.__conexion.send(info)
                info = archivo.read(self.__chunk)
                print(f"Paquete {i} enviado", end='\r')
                i += 1
                sleep(0.05)
        archivo.close()

        print(Fore.GREEN + f"[+] Archivo \"{ubicacion}\" enviado")

    def recibirArchivo(self, ubicacion):
        paquetes = self.__conexion.recv(1024).decode()
        print(Fore.CYAN + f"[*] Paquetes estimados: {paquetes}")

        i = 1
        with open(ubicacion, 'wb') as archivo:
            while True:
                info = self.__conexion.recv(self.__chunk)
                archivo.write(info)

                if len(info) < self.__chunk:
                    break
                print(f"Paquete {i} recibido", end='\r')
                i += 1
        archivo.close()
        print(Fore.GREEN + f"[+] Archivo \"{ubicacion}\" creado")

    def enviarDirectorio(self, origen, index):
        archivos = []
        for i in os.listdir(origen):
            archivo = f"{origen}/{i}"
            if os.path.isfile(archivo):
                archivos.append(archivo)
        tam = len(archivos)
        print(Fore.CYAN + f"[*] Numero de archivos: {tam}")

        sleep(0.1)
        self.__conexion.send(str(tam).encode())

        if index > tam:
            index = 1
        subidos = 0
        while index <= tam:
            nombre = self.getNombre(archivos[index-1])
            peso = os.path.getsize(archivos[index-1])
            paquetes = int(peso/self.__chunk)

            if paquetes != 0:
                print(Fore.MAGENTA + f"\n[?] {index}. Subir \"{nombre}\" ({paquetes})?...\n[S/n] ", end='')
                res = input()
            else:
                print(Fore.YELLOW + f"\n[!] {index}. Archivo \"{nombre}\" omitido ({nombre}, {paquetes})")
                res = 'N'

            sleep(0.05)
            if len(res) == 0 or res.upper() == 'S':
                self.__conexion.send('S'.encode())
                sleep(0.05)
                self.__conexion.send(nombre.encode())
                self.enviarArchivo(archivos[index-1])
                subidos += 1

            elif res.lower() == 'q' or res.lower() == "quit":
                self.__conexion.send("quit".encode())
                break

            else:
                self.__conexion.send('N'.encode())

            index += 1
            sleep(0.05)

        print(Fore.GREEN + f"[+] {subidos} archivos subidos de {tam}")

    def recibirDirectorio(self, destino, index):
        if not os.path.isdir(destino):
            os.mkdir(destino)
        tam = int(self.__conexion.recv(1024).decode())
        print(Fore.CYAN + f"[*] Numero de archivos: {tam}")

        if index > tam:
            index = 1
        bajados = 0
        while index <= tam:
            info = self.__conexion.recv(1024).decode()
            info = info.split('\n')
            nombre, paquetes = info[:2]

            if paquetes != '0':
                print(Fore.MAGENTA + f"\n[?] {index}. Bajar \"{nombre}\" ({paquetes})?...\n[S/n] ", end='')
                res = input()
            else:
                print(Fore.YELLOW + f"\n[!] {index}. Archivo \"{nombre}\" omitido ({nombre}, {paquetes})")
                res = 'N'

            if len(res) == 0 or res.upper() == 'S':
                self.__conexion.send('S'.encode())
                self.recibirArchivo(f"{destino}/{nombre}")
                bajados += 1
            elif res.lower() == 'q' or res.lower() == "quit":
                self.__conexion.send("quit".encode())
                break
            else:
                self.__conexion.send('N'.encode())

            index += 1

        print(Fore.GREEN + f"[+] {bajados} archivos descargados de {tam}")

    def local(self, cmd):
        if cmd.lower()[:2] == "cd":
            directorio = cmd[3:]
            if os.path.isdir(directorio):
                os.chdir(directorio)
                print(os.getcwd())

            else:
                print(Fore.YELLOW + f"[!] Directorio \"{directorio}\" no encontrado")

        else:
            os.system(cmd)

    def exit(self, cmd):
        print(Fore.MAGENTA + f"[?] Segur@ que quieres terminar la conexion con {self.__addr}?...\n[S/n] ", end='')
        res = input()

        if len(res) == 0 or res.upper() == 'S':
            self.__conexion.send(cmd.encode())
            self.__conexion.close()
            self.__sock.close()
            print(Fore.YELLOW + f"[!] Conexion terminada con {self.__addr[0]}")
            return True
        else:
            print(Fore.YELLOW + f"[!] Operacion cancelada")
            return False

    def cd(self, cmd):
        self.__conexion.send(cmd.encode())

        msg = self.__conexion.recv(1042).decode()
        if msg[:6] != "error:":
            self.__currentDir = msg
        else:
            print(Fore.RED + f"[-] {self.__addr[0]}: {msg}")

    def sendFileFrom(self, cmd):
        if re.search("-d", cmd):
            destino = re.findall("-d[= ]([a-zA-Z0-9./ ].*)", cmd)[0]
            self.__conexion.send(cmd.encode())

            msg = self.__conexion.recv(1024).decode()
            if msg[:6] != "error:":
                self.recibirArchivo(destino)

            else:
                print(Fore.RED + f"[-] {self.__addr[0]}: {msg}")

        else:
            self.__conexion.send(cmd.encode())

            msg = self.__conexion.recv(1024).decode()
            if msg[:6] != "error:":
                destino = self.__conexion.recv(1024).decode()
                self.recibirArchivo(destino)

            else:
                print(Fore.RED + f"[-] {self.__addr[0]}: {msg}")

    def sendFileTo(self, cmd):
        if re.search("-d", cmd):
            origen = re.findall("-o[= ]([a-zA-Z0-9./ ].*) -d", cmd)[0]

            if os.path.isfile(origen):
                self.__conexion.send(cmd.encode())
                self.enviarArchivo(origen)

            else:
                print(Fore.YELLOW + f"[!] Archivo \"{origen}\" no encontrado")

        else:
            origen = re.findall("-o[= ]([a-zA-Z0-9./ ].*)", cmd)[0]

            if os.path.isfile(origen):
                self.__conexion.send(cmd.encode())
                nombre = self.getNombre(origen)

                sleep(0.05)
                self.__conexion.send(nombre.encode())
                self.enviarArchivo(origen)

            else:
                print(Fore.YELLOW + f"[!] Archivo \"{origen}\" no encontrado")

    def image(self, cmd):
        self.__conexion.send(cmd.encode())

        msg = self.__conexion.recv(1024).decode()

        if msg[:6] != "error:":
            nombre = self.__conexion.recv(1024).decode()
            info = self.recibirDatos()

            matriz = numpy.frombuffer(info, dtype=numpy.uint8)
            imagen = cv2.imdecode(matriz, -1)

            if re.search("-t", cmd):
                escala = float(re.findall("-t[= ]([0-9.].*)", cmd)[0])
            else:
                height, width = imagen.shape[:2]
                escala = self.escalar(height, width)
            imagen = cv2.resize(imagen, None, fx=escala, fy=escala)
            print(f"Escala: {escala}")

            cv2.imshow(f"{self.__addr[0]}: {nombre}", imagen)
            cv2.waitKey()
            cv2.destroyAllWindows()

        else:
            print(Fore.RED + f"[-] {self.__addr[0]}: {msg}")

    def sendDirFrom(self, cmd):
        if re.search("-d", cmd):
            if re.search("-i", cmd):
                destino = re.findall("-d[= ]([a-zA-Z0-9./ ].*) -i", cmd)[0]
                index = int(re.findall("-i[= ]([0-9. ].*)", cmd)[0])
                if index <= 0:
                    index = 1
            else:
                destino = re.findall("-d[= ]([a-zA-Z0-9./ ].*)", cmd)[0]
                index = 1

            self.__conexion.send(cmd.encode())
            msg = self.__conexion.recv(1024).decode()
            if msg[:6] != "error:":
                self.recibirDirectorio(destino, index)
            else:
                print(Fore.RED + f"[-] {self.__addr[0]}: {msg}")

        else:
            if re.search("-i", cmd):
                index = int(re.findall("-i[= ]([0-9. ].*)", cmd)[0])
                if index <= 0:
                    index = 1
            else:
                index = 1

            self.__conexion.send(cmd.encode())
            msg = self.__conexion.recv(1024).decode()
            if msg[:6] != "error:":
                destino = self.__conexion.recv(1024).decode()
                self.recibirDirectorio(destino, index)
            else:
                print(Fore.RED + f"[-] {self.__addr[0]}: {msg}")

    def sendDirTo(self, cmd):
        if re.search("-d", cmd):
            origen = re.findall("-o[= ]([a-zA-Z0-9./ ].*) -d", cmd)[0]
            if re.search("-i", cmd):
                index = int(re.findall("-i[= ]([0-9. ].*)", cmd)[0])
                if index <= 0:
                    index = 1
            else:
                index = 1

            self.__conexion.send(cmd.encode())
            self.enviarDirectorio(origen, index)

        else:
            if re.search("-i", cmd):
                origen = re.findall("-o[= ]([a-zA-Z0-9./ ].*) -i", cmd)[0]
                index = int(re.findall("-i[= ]([0-9. ].*)", cmd)[0])
                if index <= 0:
                    index = 1
            else:
                origen = re.findall("-o[= ]([a-zA-Z0-9./ ].*)", cmd)[0]
                index = 1

            self.__conexion.send(cmd.encode())
            sleep(0.05)
            destino = self.getNombre(origen)
            self.__conexion.send(destino.encode())
            self.enviarDirectorio(origen, index)

    def comprimir(self, cmd):
        self.__conexion.send(cmd.encode())
        msg = self.__conexion.recv(1024).decode()

        if msg[:6] != "error:":
            print(Fore.GREEN + f"[+] {self.__addr[0]}: {msg}")
        else:
            print(Fore.RED + f"[-] {self.__addr[0]}: {msg}")

    def descomprimir(self, cmd):
        self.__conexion.send(cmd.encode())
        msg = self.__conexion.recv(1024).decode()

        if msg[:6] != "error:":
            print(Fore.GREEN + f"[+] {self.__addr[0]}: {msg}")
        else:
            print(Fore.RED + f"[-] {self.__addr[0]}: {msg}")

    def shell(self):
        try:
            while True:
                self.terminal()
                cmd = input()

                if cmd == '' or cmd.replace(' ', '') == '':
                    print(Fore.YELLOW + f"[!] Comando invalido")

                elif cmd[0] == '!':
                    try:
                        self.local(cmd[1:])

                    except:
                        print(Fore.RED + "[-] Error de sintaxis local")

                elif cmd.lower() == "clear" or cmd.lower() == "cls" or cmd.lower() == "clc":
                    os.system("clear")

                elif cmd.lower() == "exit":
                    try:
                        salir = self.exit(cmd)
                        if salir:
                            break

                    except:
                        print(Fore.RED + "[-] Error al terminar la conexion")

                elif cmd.lower() == 'q' or cmd.lower() == "quit":
                    try:
                        self.__conexion.send(cmd.encode())
                        self.__conexion.close()
                        self.__sock.close()
                        break

                    except:
                        print(Fore.RED + "[-] Error al cerrar el programa")

                elif cmd.lower()[:2] == "cd":
                    try:
                        self.cd(cmd)

                    except:
                        print(Fore.RED + "[-] Error de proceso (cd)")

                elif cmd.lower()[:3] == "sff":
                    try:
                        if re.search("-o", cmd):
                            self.sendFileFrom(cmd)

                        else:
                            print(Fore.YELLOW + f"[!] Falta del parametro de origen (-o)")

                    except:
                        print(Fore.RED + "[-] Error de proceso (sff)")

                elif cmd.lower()[:3] == "sft":
                    try:
                        if re.search("-o", cmd):
                            self.sendFileTo(cmd)
                        else:
                            print(Fore.RED + "[!] Falta del parametro de origen (-o)")

                    except:
                        print(Fore.RED + "[-] Error de proceso (sft)")

                elif cmd.lower()[:3] == "img":
                    try:
                        if re.search("-i", cmd):
                            self.image(cmd)
                        else:
                            print(Fore.YELLOW + f"[!] Falta del parametro imagen (-i)")

                    except:
                        print(Fore.RED + "[-] Error de proceso (img)")

                elif cmd.lower()[:3] == "sdf":
                    try:
                        if re.search("-o", cmd):
                            self.sendDirFrom(cmd)

                        else:
                            print(Fore.YELLOW + f"[!] Falta del parametro origen (-o)")

                    except:
                        print(Fore.RED + "[-] Error de proceso (sdf)")

                elif cmd.lower()[:3] == "sdt":
                    try:
                        if re.search("-o", cmd):
                            self.sendDirTo(cmd)
                        else:
                            print(Fore.YELLOW + f"[!] Falta del parametro origen (-o)")

                    except:
                        print(Fore.RED + "[-] Error de proceso (sdt)")

                elif cmd.lower()[:3] == "zip":
                    try:
                        if re.search("-o", cmd):
                            self.comprimir(cmd)
                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro de origen (-o)")

                    except:
                        print(Fore.RED + "[-] Error de proceso (zip)")

                elif cmd.lower()[:5] == "unzip":
                    try:
                        if re.search("-o", cmd):
                            self.descomprimir(cmd)

                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro de origen (-o)")

                    except:
                        print(Fore.RED + "[-] Error de proceso (unzip)")

                else:
                    try:
                        self.__conexion.send(cmd.encode())

                        while True:
                            info = self.__conexion.recv(self.__chunk)
                            info = ''.join([chr(i) for i in info])
                            print(info)

                            if len(info) < self.__chunk:
                                break

                    except:
                        print(Fore.RED + "[-] Error al ejecutar el comando")

        except:
            print(Fore.RED + "Excepcion en el programa principal")
