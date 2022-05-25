from tcp import TCP
import sys

host = sys.argv[1]
port = int(sys.argv[2])
chunk = int(sys.argv[3])

tcp = TCP(host, port, chunk)

tcp.shell()
