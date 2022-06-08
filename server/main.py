from tcp import TCP
import sys

host = sys.argv[1]
port = int(sys.argv[2])

tcp = TCP(host, port)

tcp.shell()
