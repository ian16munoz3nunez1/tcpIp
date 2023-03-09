## Client
import sys
from tcp import TCP
from man import logo, man

if len(sys.argv) == 2:
    if sys.argv[1] == "-h" or sys.argv[1] == "--help":
        logo()
        man()
    else:
        print("Error de sintaxis")

elif len(sys.argv) == 3:
    try:
        host = sys.argv[1]
        port = int(sys.argv[2])
        tcp = TCP(host, port)
        tcp.conectar()
        tcp.shell()
    except:
        print("Error de sintaxis")

else:
    tcp = TCP("localhost", 9999)

    tcp.conectar()

    tcp.shell()
