"""
    Altair - Client (UDP)
"""

# Required Libraries
from multiprocessing import Process
from os import path, makedirs
from getpass import getpass
import socket as SKT
import traceback
import argparse
import logging
import pickle
import glob
import sys
import os

# -- Poetry --

# Used for prompt based input


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


class projectSeed:

    def __init__(self, project_id, author, passwd, path):
        self.proj_id = project_id
        self.author = author
        self.passphase = passwd
        self.dirs = []
        self.files = {}
        self.creatree(path)

    def creatree(self, path):
        items = glob.glob(os.path.join(path, "*"))
        for item in items:
            if os.path.isdir(item):
                print("DIR : {}".format(item))
                self.dirs.append(item)
                self.creatree(item)
            if os.path.isfile(item):
                print("FILE : {}".format(item))
                buffer = b''
                with open(item, 'rb') as f:
                    buffer += f.read()
                self.files[item] = buffer
                f.close()

    def artifact(self):
        return {
            "Project_ID": self.proj_id,
            "Author": self.author,
            "passwd": self.passphase,
            "dirs": self.dirs,
            "files": self.files
        }

    def __str__(self):
        return "\n------\nProject : {}\nAuthor : {}\n------\nDirectories : {}\nFiles : {}".format(
            self.proj_id, self.author,
            len(self.dirs), len(self.files)
        )


class ClientSocket:

    def __init__(self, server, port):
        print("=== Altair : Client Module ===")
        self.serverAddr = server
        self.serverPort = port
        self._BUF_SIZE = 4096
        self.PKT_TYPE = {
            "plant": self.plant_rsp,
            "test": self.test_rsp
        }
        print("Connecting to server at {}:{}"
              .format(self.serverAddr, self.serverPort))
        self.agent = SKT.socket(SKT.AF_INET, SKT.SOCK_DGRAM)

    def listen(self):
        print("|=== Server Listner : Active ===|")
        while True:
            _BUFFER = self.agent.recvfrom(self._BUF_SIZE)
            if _BUFFER:
                print("Packet from {}:{}".format(_BUFFER[1][0], _BUFFER[1][1]))
                _PACKET = self.unpack(_BUFFER[0])
                _PTYPE = _PACKET["type"]
                if _PTYPE == 'rsp':
                    _RSP = _PACKET["rtype"]
                    _DATA = _PACKET['data']
                    print("ServerResponse: {}\n ".format(_RSP))
                    self.PKT_TYPE[_RSP](_DATA)
                if _PTYPE == 'req':
                    print("ServerRequest")

    def plant(self):
        _pid = argvalid("Enter Project Name : ",
                        "=(!)=== Project ID should not be null ===(!)=")
        _usr = argvalid("Enter Author Name : ",
                        "=(!)=== We need to know who made this ===(!)=")
        _pwd = argvalid(
            "Enter Password : ", "=(!)=== We really need a password to protect this! ===(!)=", ispasswd=True)
        _prj_path = argvalid(
            "Enter Project Path (default: Current Path) : ", "", "./")
        print("Setting up project seed...")
        _seed = projectSeed(_pid, _usr, _pwd, _prj_path)
        _packet = self.pack({
            "type": "req",
            "rtype": "plant",
            "data": _seed.artifact()
        })
        print("SeedSize={}".format(len(_seed.artifact())))
        self.agent.sendto(_packet, (self.serverAddr, self.serverPort))

    def plant_rsp(self, data):
        if data:
            print("ProjectPlant: SUCESS")
        else:
            print("ProjectPlant: FAIL")
        self.close()

    def test(self):
        print("Sending test request...")
        self.agent.sendto(self.pack({
            "type": "req",
            "rtype": "test",
            "data": True
        }), (self.serverAddr, self.serverPort))

    def test_rsp(self, data):
        if data:
            print("ServerTest : OK")
        else:
            print("ServerTest: FAIL")
        self.close()

    def pack(self, data):
        return pickle.dumps(data)

    def unpack(self, packet):
        return pickle.loads(packet)

    def close(self):
        print("Server Disconnected")
        self.agent.close()
        sys.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PrototypeCMD")
    parser.add_argument("CMD", help="Command here", action="store")
    args = parser.parse_args()
    try:
        Client = ClientSocket("localhost", 10092)
        cmdS = {
            "plant": Client.plant,
            "test": Client.test
        }
        cmdS[args.CMD]()
        ListnrEvent = Process(target=Client.listen)
        ListnrEvent.start()
        print("\n-()-\n")
    except Exception as e:
        logging.error("Something went wrong!\n")
        traceback.print_exception(*sys.exc_info())
