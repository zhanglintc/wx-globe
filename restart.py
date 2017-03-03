import os, sys

print("killing makeServer.py")
os.system("ps -ef | grep makeServer.py | grep -v grep | cut -c 9-15 | xargs kill -s 9")

if len(sys.argv) == 2 and sys.argv[1] == "shut":
    sys.exit(0)

print("restarting makeServer.py")
os.system("nohup python makeServer.py&")

