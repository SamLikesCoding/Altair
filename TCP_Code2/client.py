"""

    Altair - Client (TCP)

"""

# Required Libraries
from getpass import getpass
import _thread as thread
import socket as socket
import traceback
import argparse
import hashlib
import pickle
import glob
import time
import sys
import os

# Poetry


def argvalid(prompt_mesg, error_prompt, default_value='', ispasswd=False):
    while True:
        if ispasswd:
            var = getpass(prompt_mesg)
        else:
            var = input(prompt_mesg)
        if var == '':
            if default_value != '':
                return default_value
            print(error_prompt)
        else:
            return var


class projectGraph:
    """
    docstring
    """

    def __init__(self):
        self.sg = sg()


class Seed:

    def __init__(self, pr_id, author, pswd, path):
        self.pr_id = pr_id
        self.author = author
        self.pswd = pswd
        self.path = path
        self.dirs = []
        self.files = {}
        self.ctree(path)

    def ctree(self, path):
        items = glob.glob(os.path.join(path, "*"))
        for item in items:
            if os.path.isdir(item):
                print("DIR: {}".format(item))
                self.dirs.append(item)
                self.ctree(item)
            if os.path.isfile(item):
                print("FILE: {}".format(item))
                self.files[item] = self.filePacker(item)

    def wither(self):
        return {
            "Project-ID": self.pr_id,
            "Author": self.author,
            "Password": self.pswd,
            "dirs": self.dirs,
            "files": self.files
        }

    def filePacker(self, filePath):
        buffer = b''
        with open(filePath, "rb") as reader:
            buffer += reader.read()
        return pickle.dumps(buffer)


class ClientSocket:

    def __init__(self, host="localhost", port=10092):
        print("Setting up Socket...")
        self.agent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = host
        self.port = port
        self._END_ = False
        self.OFFSET = 32
        self.CMD_EXEC = {
            "TEST": self.test_rsp,
            "PLANT": self.plant_rsp,
            "REAP": self.reap_rsp,
            "MESG": self.serverMSG,
            "PRGS": self.progress
        }
        print("Connecting to Server...")
        self.agent.connect((self.addr, self.port))

    def online(self):
        print("ServerListner : ACTIVE")
        _BFRSET = True
        _FW_LEN = self.OFFSET
        while not self._END_:
            _BUFFER = self.agent.recv(_FW_LEN)
            if _BUFFER != b'':

                if _BFRSET:
                    _FW_LEN = int(_BUFFER[:self.OFFSET])
                    _BFRSET = False
                else:
                    print("PacketSize={}".format(_FW_LEN))
                    if len(_BUFFER) == _FW_LEN:
                        _PACKET = self.unpack(_BUFFER)
                        print("REQType:{}".format(_PACKET["type"]))
                        self.CMD_EXEC[_PACKET['type']](_PACKET['data'])
                        _BFRSET = True
                        _FW_LEN = self.OFFSET
                        _BUFFER = b''

    # Plant Functions
    def plant(self):
        proj_id = argvalid("Enter Project ID : ",
                           "=(!)=== Project ID should not be null ===(!)=")
        author = argvalid("Enter Author Name : ",
                          "=(!)=== Author field should not be null ===(!)=")
        passwd = argvalid("Enter Project Password : ",
                          "=(!)=== You really need a password for this ===(!)=",
                          ispasswd=True)
        path = argvalid("Enter Project Path (Default : ./): ", "", './')
        prj = Seed(pr_id=proj_id, author=author,
                   pswd=passwd, path=path)
        packet = self.pack({
            "type": "PLANT",
            "data": prj.wither()
        })
        self.agent.send(packet)

    def reap(self):
        proj_id = argvalid("Enter Project ID : ",
                           "=(!)=== Project ID should not be null ===(!)=")
        passwd = argvalid("Enter Project Password : ",
                          "=(!)=== You really need a password for this ===(!)=",
                          ispasswd=True)
        packet = self.pack({
            "type": "REAP",
            "data": {"prj_id": proj_id, "paswd": passwd}
        })
        self.agent.sendall(packet)

    def reap_rsp(self, rsp):
        print("Reaping....")
        if rsp != None:
            print(rsp)
        else:
            print("SERVICE_FAIL: Project Not Found")
        sys.exit()

    def plant_rsp(self, rsp):
        if rsp:
            print("Request: OK")
        else:
            print("Request: FAIL")
        self.close()

    def serverMSG(self, msg):
        print("\n=== ServerMessage ===\n")
        print(msg)
        print("\n=== ServerMessage ===\n")

    def progress(self, data):
        print("Progress: {}".format(data), end='\r')

    # Test Functions

    def test(self):
        print("Sending test requests...")
        self.agent.send(
            self.pack({
                "type": "TEST",
                "data": True
            })
        )

    def test_rsp(self, rsp):
        if rsp:
            print("Server Test : OK")
        else:
            print("Server Test : FAIL")
        self.close()

    # Packet Functions

    def pack(self, data):
        print("Packing...")
        packet = pickle.dumps(data)
        print("\nSize={}\n".format(len(packet)))
        return bytes(f"{len(packet):<{self.OFFSET}}", "utf-8")+packet

    def unpack(self, packet):
        return pickle.loads(packet)

    # Just stop everything!

    def close(self):
        self._END_ = True
        print("\nGoodbye!")
        self.agent.close()


# Main function
if __name__ == "__main__":
    print(" Altair : Client Prototype 2")
    parser = argparse.ArgumentParser(description="Test level")
    parser.add_argument("CMD", help="Command here", action="store")
    args = parser.parse_args()
    client = ClientSocket()
    ARG_EXEC = {
        "test": client.test,
        'plant': client.plant,
        "reap": client.reap
    }
    try:
        thread.start_new_thread(client.online, ())
        time.sleep(0.75)
        ARG_EXEC[args.CMD]()
    except KeyboardInterrupt:
        client.close()
    except Exception as e:
        print("--< Exception Occured (!) >--")
        traceback.print_exception(*sys.exc_info())
