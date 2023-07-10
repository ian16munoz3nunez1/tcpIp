## Client
from colorama import init
from colorama.ansi import Fore

init(autoreset=True)

def logo():
    print(Fore.CYAN   + "(client)")
    print(Fore.BLUE   + "▄▄▄█████▓ ▄████▄   ██▓███   ██▓ ██▓███ ▓██   ██▓")
    print(Fore.BLUE   + "▓  ██▒ ▓▒▒██▀ ▀█  ▓██░  ██▒▓██▒▓██░  ██▒▒██  ██▒")
    print(Fore.YELLOW + "▒ ▓██░ ▒░▒▓█    ▄ ▓██░ ██▓▒▒██▒▓██░ ██▓▒ ▒██ ██░")
    print(Fore.YELLOW + "░ ▓██▓ ░ ▒▓▓▄ ▄██▒▒██▄█▓▒ ▒░██░▒██▄█▓▒ ▒ ░ ▐██▓░")
    print(Fore.RED    + "  ▒██▒ ░ ▒ ▓███▀ ░▒██▒ ░  ░░██░▒██▒ ░  ░ ░ ██▒▓░")
    print(Fore.RED    + "  ▒ ░░   ░ ░▒ ▒  ░▒▓▒░ ░  ░░▓  ▒▓▒░ ░  ░  ██▒▒▒ ")
    print(Fore.RED    + "    ░      ░  ▒   ░▒ ░      ▒ ░░▒ ░     ▓██ ░▒░ ")
    print(Fore.RED    + "  ░      ░        ░░        ▒ ░░░       ▒ ▒ ░░  ")
    print(Fore.RED    + "         ░ ░                ░           ░ ░     ")
    print(Fore.RED    + "         ░                              ░ ░     ")

def man():
    print(Fore.BLUE + "\ncomand" + Fore.RED + " --> " + Fore.WHITE + "Comando")
    print(Fore.MAGENTA + "comand" + Fore.RED + " --> " + Fore.WHITE + "Ejemplo de comando")
    print(Fore.YELLOW + "*" + Fore.RED + " --> " + Fore.WHITE + "Parametro obligatorio")
    print(Fore.GREEN + "+" + Fore.RED + " --> " + Fore.WHITE + "Parametro opcional\n\n")

    print(Fore.BLUE + "--help/-h/help" + Fore.RED + " --> " + Fore.WHITE + "Despliega este mensaje de ayuda")
    print(Fore.MAGENTA + "\ttcpIpys --help ~~ tcpIpys -h ~~ (dentro del programa)> help")

    print(Fore.BLUE + "\ntcpIpys" + Fore.RED + " --> " + Fore.WHITE + "Se ejecuta el programa con los parametros por default")
    print(Fore.BLUE + "tcpIpys <ipv4> <port>" + Fore.RED + " --> " + Fore.WHITE + "Se ejecuta el programa con los parametros especificados")
    print(Fore.MAGENTA + "\t<ipv4> --> 127.0.0.1 ~~ <port> --> 2048")
    print()

    print(Fore.BLUE + "\n!" + Fore.RED + " --> " + Fore.WHITE + "Ejecuta un comando local despues del simbolo")
    print(Fore.MAGENTA + "\t!cd ..")

    print(Fore.BLUE + "\ncap" + Fore.RED + " --> " + Fore.WHITE + "Muestra un video de alguna camara web de la maquina del cliente")
    print(Fore.YELLOW + "\t* -c" + Fore.RED + " --> " + Fore.WHITE + "Especifica la camara que se quiere utilizar")
    print(Fore.MAGENTA + "\tcap -c 0 ~~ cap -c=1")

    print(Fore.BLUE + "\ncd" + Fore.RED + " --> " + Fore.WHITE + "Cambia el directorio del cliente al especificado")
    print(Fore.MAGENTA + "\tcd Escritorio")

    print(Fore.BLUE + "\nclear/cls/clc" + Fore.RED + " --> " + Fore.WHITE + "Limpia la pantalla")
    print(Fore.MAGENTA + "\tclear/cls/clc")

    print(Fore.BLUE + "\ndecrypt" + Fore.RED + " --> " + Fore.WHITE + "Desencripta los archivos de un directorio del cliente")
    print(Fore.YELLOW + "\t* -i" + Fore.RED + " --> " + Fore.WHITE + "Especifica el directorio a desencriptar")
    print(Fore.YELLOW + "\t* -k" + Fore.RED + " --> " + Fore.WHITE + "Especifica el nombre de la llave de desencriptacion")
    print(Fore.MAGENTA + "\tdencrypt -k llave.key -i .")

    print(Fore.BLUE + "\nencrypt" + Fore.RED + " --> " + Fore.WHITE + "Encripta los archivos de un directorio del cliente")
    print(Fore.YELLOW + "\t* -i" + Fore.RED + " --> " + Fore.WHITE + "Especifica el directorio a encriptar")
    print(Fore.YELLOW + "\t* -k" + Fore.RED + " --> " + Fore.WHITE + "Especifica el nombre de la llave de encriptacion")
    print(Fore.MAGENTA + "\tencrypt -k llave.key -i .")

    print(Fore.BLUE + "\nexit" + Fore.RED + " --> " + Fore.WHITE + "Termina el programa en ambos extremos")
    print(Fore.MAGENTA + "\texit")

    print(Fore.BLUE + "\nimg" + Fore.RED + " --> " + Fore.WHITE + "Se muestra una imagen especificada de la maquina del cliente")
    print(Fore.YELLOW + "\t* -i" + Fore.RED + " --> " + Fore.WHITE + "Especifica la ruta de la imagen del cliente")
    print(Fore.GREEN + "\t+ -t" + Fore.RED + " --> " + Fore.WHITE + "Sirve para asignar la escala de la imagen")
    print(Fore.GREEN + "\t+ -r" + Fore.RED + " --> " + Fore.WHITE + "Elige una imagen del directorio actual de manera aleatoria")
    print(Fore.GREEN + "\t+ -90" + Fore.RED + " --> " + Fore.WHITE + "Gira la imagen 90 grados")
    print(Fore.GREEN + "\t+ -180" + Fore.RED + " --> " + Fore.WHITE + "Gira la imagen 180 grados")
    print(Fore.GREEN + "\t+ -270" + Fore.RED + " --> " + Fore.WHITE + "Gira la imagen 270 grados")
    print(Fore.GREEN + "\t+ -x" + Fore.RED + " --> " + Fore.WHITE + "Gira la imagen en el eje x")
    print(Fore.GREEN + "\t+ -y" + Fore.RED + " --> " + Fore.WHITE + "Gira la imagen en el eje y")
    print(Fore.GREEN + "\t+ -g" + Fore.RED + " --> " + Fore.WHITE + "Cambia el color de la imagen a escala de grises")
    print(Fore.GREEN + "\t+ -n" + Fore.RED + " --> " + Fore.WHITE + "Cambia el color de la imagen al negativo")
    print(Fore.GREEN + "\t+ -m" + Fore.RED + " --> " + Fore.WHITE + "Efecto espejo")
    print(Fore.GREEN + "\t+ -c" + Fore.RED + " --> " + Fore.WHITE + "Deteccion de bordes con algoritmo Canny")
    print("\tAl tener la imagen abierta, esta se guarda presionando la tecla 's'")
    print(Fore.MAGENTA + "\timg -i imagen.jpg ~~ img -r ~~ img -g -i imagen.jpg -t=0.5 ~~ img -ynm -i imagen.jpg")

    print(Fore.BLUE + "\nlendir" + Fore.RED + " --> " + Fore.WHITE + "Muestra al numero de elementos de un directorio")
    print(Fore.MAGENTA + "\tlendir dirPath")

    print(Fore.BLUE + "\nmialias" + Fore.RED + " --> " + Fore.WHITE + "Muestra los alias que se encuentran en el archivo \'alias.json\'")

    print(Fore.BLUE + "\nmienv" + Fore.RED + " --> " + Fore.WHITE + "Muestra las variables de entorno que se encuentran en el archivo \'var.json\'")

    print(Fore.BLUE + "\nmiwget" + Fore.RED + " --> " + Fore.WHITE + "Descarga un archivo de internet en la maquina del cliente")
    print(Fore.YELLOW + "\t* -u" + Fore.RED + " --> " + Fore.WHITE + "Especifica la url del archivo")
    print(Fore.GREEN + "\t+ -n" + Fore.RED + " --> " + Fore.WHITE + "Especifica el nombre del archivo")
    print(Fore.MAGENTA + "\tmiwget -u=<url> ~~ miwget -u <url> -n wget.pdf")

    print(Fore.BLUE + "\npic" + Fore.RED + " --> " + Fore.WHITE + "Toma una foto con alguna camara web de la maquina del cliente")
    print(Fore.YELLOW + "\t* -c" + Fore.RED + " --> " + Fore.WHITE + "Especifica la camara que se quiere usar")
    print("\tAl tener la imagen abierta, esta se guarda presionando la tecla 's'")
    print(Fore.MAGENTA + "\tpic -c 0 ~~ pic -c=1")

    print(Fore.BLUE + "\nq/quit" + Fore.RED + " --> " + Fore.WHITE + "Termina la conexion con el cliente, pero no el programa")
    print(Fore.MAGENTA + "\tq/quit")

    print(Fore.BLUE + "\nsave" + Fore.RED + " --> " + Fore.WHITE + "Guarda en un archivo de texto la informacion regresada por un comando")
    print(Fore.MAGENTA + "\tsave whoami")

    print(Fore.BLUE + "\nsdf" + Fore.RED + " --> " + Fore.WHITE + "Envia los archivos de un directorio del cliente al servidor")
    print(Fore.YELLOW + "\t* -i" + Fore.RED + " --> " + Fore.WHITE + "Especifica el directorio origen de la maquina del cliente")
    print(Fore.GREEN + "\t+ -a" + Fore.RED + " --> " + Fore.WHITE + "Indica si se quieren enviar los archivos de forma automatica")
    print(Fore.GREEN + "\t+ -o" + Fore.RED + " --> " + Fore.WHITE + "Especifica el directorio destino del servidor")
    print(Fore.GREEN + "\t+ -x" + Fore.RED + " --> " + Fore.WHITE + "Filtra los archivos que coinciden con la extension de la bandera")
    print(Fore.MAGENTA + "\t sdf -i directorioOrigen ~~ sdf -a -i dirOrigen -o dirDestino -p=4")

    print(Fore.BLUE + "\nsdt" + Fore.RED + " --> " + Fore.WHITE + "Envia los archivos de un directorio del servidor al cliente")
    print(Fore.YELLOW + "\t* -i" + Fore.RED + " --> " + Fore.WHITE + "Especifica el directorio origen del servidor")
    print(Fore.GREEN + "\t+ -a" + Fore.RED + " --> " + Fore.WHITE + "Indica si se quieren enviar los archivos de forma automatica")
    print(Fore.GREEN + "\t+ -o" + Fore.RED + " --> " + Fore.WHITE + "Especifica el directorio destino de la maquina del cliente")
    print(Fore.GREEN + "\t+ -x" + Fore.RED + " --> " + Fore.WHITE + "Filtra los archivos que coinciden con la extension de la bandera")
    print(Fore.MAGENTA + "\t sdf -i directorioOrigen ~~ sdf -a -i dirOrigen -o dirDestino -p=4")

    print(Fore.BLUE + "\nsff" + Fore.RED + " --> " + Fore.WHITE + "Envia un archivo del cliente al servidor")
    print(Fore.YELLOW + "\t* -i" + Fore.RED + " --> " + Fore.WHITE + "Especifica la ruta del archivo del cliente")
    print(Fore.GREEN + "\t+ -o" + Fore.RED + " --> " + Fore.WHITE + "Especifica la ruta destino en el servidor (si no se agrega este parametro, el nombre del archivo se mantiene igual)")
    print(Fore.MAGENTA + "\tsff -i origen.txt ~~ sff -i origen.txt -o destino.txt")

    print(Fore.BLUE + "\nsft" + Fore.RED + " --> " + Fore.WHITE + "Envia un archivo del servidor al cliente")
    print(Fore.YELLOW + "\t* -i" + Fore.RED + " --> " + Fore.WHITE + "Especifica la ruta del archivo del servidor")
    print(Fore.GREEN + "\t+ -o" + Fore.RED + " --> " + Fore.WHITE + "Especifica la ruta de destino en la maquina del cliente (si no se agrega este parametro, el nombre del archivo no cambia)")
    print(Fore.MAGENTA + "\tsft -i origen.txt ~~ sft -i origen.txt -o destino.txt")

    print(Fore.BLUE + "\nss" + Fore.RED + " --> " + Fore.WHITE + "Toma capturas de la pantalla del cliente")
    print(Fore.GREEN + "\t+ -d" + Fore.RED + " --> " + Fore.WHITE + "Directorio del cliente para guardar los archivos temporales")
    print(Fore.GREEN + "\t+ -n" + Fore.RED + " --> " + Fore.WHITE + "Numero de capturas a tomar")
    print(Fore.GREEN + "\t+ -o" + Fore.RED + " --> " + Fore.WHITE + "Directorio de destino en el servidor")
    print(Fore.GREEN + "\t+ -t" + Fore.RED + " --> " + Fore.WHITE + "Tiempo de espera entre cada captura")
    print(Fore.MAGENTA + "\tss ~~ ss -n 10 -t 1 ~~ ss -n 4 -t 5 -d inDir -o outDir")

    print(Fore.BLUE + "\nunzip" + Fore.RED + " --> " + Fore.WHITE + "Decomprime un archivo .zip")
    print(Fore.YELLOW + "\t* -i" + Fore.RED + " --> " + Fore.WHITE + "Especifica el archivo .zip de origen")
    print(Fore.GREEN + "\t+ -o" + Fore.RED + " --> " + Fore.WHITE + "Especifica el directorio destino")
    print(Fore.MAGENTA + "\tunzip -i archivo.zip ~~ unzip -i=archivo.zip -o=dirDestino")

    print(Fore.BLUE + "\nzip" + Fore.RED + " --> " + Fore.WHITE + "Comprime los archivos de un directorio del cliente")
    print(Fore.YELLOW + "\t* -i" + Fore.RED + " --> " + Fore.WHITE + "Especifica el archivo o directorio a comprimir")
    print(Fore.GREEN + "\t+ -o" + Fore.RED + " --> " + Fore.WHITE + "Especifica el archivo .zip de destino")
    print(Fore.MAGENTA + "\tzip -i archivo.pdf ~~ zip -i=dirOrigen -o=archivo.zip")

