## Server
from tcp import TCP
from man import logo, man
import sys

if len(sys.argv) == 2:
    if sys.argv[1] == "--help" or sys.argv[1] == "-h":
        logo()
        man()
    else:
        print("Error de sintaxis")

elif len(sys.argv) == 3:
    try:
        host = sys.argv[1]
        port = int(sys.argv[2])

        tcp = TCP(host, port)
        tcp.shell()
    except:
        print("Error de sintaxis")

else:
    host = sys.argv[1]
    port = int(sys.argv[2])

    tcp = TCP("0.0.0.0", 9999)

    tcp.shell()
