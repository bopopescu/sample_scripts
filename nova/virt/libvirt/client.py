import socket

s = socket.socket()
host = "10.29.1.90"
port = 1053
try:
   s.connect((host, port))
   s.send("root H&perS0nic vmaaaaaman 10.29.21.199 delete")

   data = s.recv(1024)
   print data
   s.close()
except socket.error, msg:
   print "Couldnt connect to DNS server 10.29.1.90"
