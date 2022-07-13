import sys
from tcp import TCP
from man import logo, man

if len(sys.argv) > 1:
    if sys.argv[1] == "-h" or sys.argv[1] == "--help":
        logo()
        man()
    else:
        print("Error de sintaxis")
else:
    tcp = TCP("localhost", 9999)

    tcp.conectar()

    tcp.shell()
