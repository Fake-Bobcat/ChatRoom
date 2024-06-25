import socket
import json

from _thread import *

def RunServer(s, onlineusers):
    while True:
        try:
            data, addr = s.recvfrom(1024)
        except:
            continue
        if data and addr:
            data = json.loads(data.decode("utf-8"))
            user, command, usermsg = data["user"], data["command"], data["message"]
            if command == "join":
                alreadyfound = onlineusers.get(user,None)
                if alreadyfound:
                    s.sendto(json.dumps("Taken").encode("utf-8"), addr)
                    print(f"{addr} Failed to Connect | Username taken")
                else:
                    onlineusers[data["user"]] = addr
                    message = data["user"]+" has Joined the Chat."
                    for ip in onlineusers.values():
                        s.sendto(json.dumps(message).encode("utf-8"), ip)
                    print(f"{addr} ({user}) Joined the Chat")
            elif command == "disc":
                finduser = onlineusers.get(user,None)
                if finduser:
                    onlineusers.pop(user)
                message = f"{user} has Left the Chat."
                for ip in onlineusers.values():
                    s.sendto(json.dumps(message).encode("utf-8"), ip)
                print(f"{addr} ({user}) Left the Chat")
            elif command == "getonline":
                message = "\n-- List Of Online Users --\n"
                for username,ip in onlineusers.items():
                    message += username+" | "+ip[0]+"\n"
                s.sendto(json.dumps(message).encode("utf-8"), addr)
                print(f"{addr} ({user}) Ran Command /online")
            elif command == "message":
                print(f"{addr} ({user}) Sent a Message: {usermsg}")
                finalmessage = data["user"]+": "+usermsg
                for ip in onlineusers.values():
                    s.sendto(json.dumps(finalmessage).encode("utf-8"), ip)

def Main():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    host= ip_address #Server ip
    port = 0 # Chooses any available port

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    serveraddress = s.getsockname()[0]+"%"+str(s.getsockname()[1])
    print(f"Server IP Address & Port: {serveraddress}")

    onlineusers = {}

    print("-- Server Started --\n")

    #start_new_thread(RunServer,(s,onlineusers))
    RunServer(s,onlineusers)

    s.close()

if __name__=='__main__':
    Main()