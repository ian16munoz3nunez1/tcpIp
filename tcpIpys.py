#!python3

## Server
from server.tcp import TCP
from server.man import logo, man
import sys
from colorama import init
from colorama.ansi import Fore

init(autoreset=True)

if len(sys.argv) == 1:
    host = "0.0.0.0"
    port = 9999

    tcp = TCP(host, port)
    tcp.shell()

elif len(sys.argv) == 2:
    if sys.argv[1] == "--help" or sys.argv[1] == "-h":
        logo()
        man()
    else:
        print(Fore.RED + "[-] Error de sintaxis")

elif len(sys.argv) == 3:
    try:
        host = sys.argv[1]
        port = int(sys.argv[2])

        tcp = TCP(host, port)
        tcp.shell()
    except:
        print(Fore.RED + "[-] Error de sintaxis")

else:
    print(Fore.YELLOW + f"[!] Demasiados argumentos ({len(sys.argv)})")

