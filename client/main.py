## Client
import sys
from tcp import TCP
from man import logo, man

if len(sys.argv) == 1:
    host = "127.0.0.1"
    port = 9999

    tcp = TCP(host, port)
    tcp.conectar()
    tcp.shell()

if len(sys.argv) == 2:
    if sys.argv[1] == "--help" or sys.argv[1] == "-h":
        logo()
        man()
    else:
        exit()

elif len(sys.argv) == 3:
    try:
        host = sys.argv[1]
        port = int(sys.argv[2])

        tcp = TCP(host, port)
        tcp.conectar()
        tcp.shell()
    except:
        exit()

else:
    exit()

