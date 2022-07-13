from tcp import TCP
from man import logo, man
import sys

if sys.argv[1] == "--help" or sys.argv[1] == "-h":
    logo()
    man()

else:
    host = sys.argv[1]
    port = int(sys.argv[2])

    tcp = TCP(host, port)

    tcp.shell()
