import os, sys

port = 8000

# os.system("ps -ef | grep makeServer.py | grep -v grep | cut -c 9-15 | xargs kill -s 9")
print("killing server which is using port: {0}".format(port))
os.system("netstat -ntlp | grep %s | awk '{print $7}' | awk -F/ '{print $1}' | xargs kill" % port)

if len(sys.argv) == 2 and sys.argv[1] == "shut":
    sys.exit(0)

print("restarting makeServer.py")
os.system("nohup python makeServer.py&")

