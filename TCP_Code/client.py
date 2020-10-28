"""
    Altair : Client
"""

# Required Libraries
from getpass import getpass
import socket as skt
import traceback
import argparse
import pickle
import base64
import glob
import json
import sys
import os

# Poetry


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


class ClientSocket:

    def __init__(self, host, port):
        print("Waking up....")
        self.socket_agent = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        self.addr = host
        self.port = port
        self.OFFSET = 8
        self.CMD_ENGINE = {
            "TEST": self.test_rsp,
            "PLANT": self.plant_rsp
        }
        print("Connecting to Server...")
        self.socket_agent.connect((self.addr, self.port))

    def online(self):
        print("\n=> Listening...")
        BUF_RSET = True
        FRAME_LEN = self.OFFSET
        while True:
            FRAME = self.socket_agent.recv(FRAME_LEN)
            if FRAME != b'':
                if BUF_RSET:
                    FRAME_LEN = int(FRAME[:self.OFFSET])
                    print("PacketSize={}".format(FRAME_LEN))
                    BUF_RSET = False
                else:
                    PACKET = self.unpack(FRAME)
                    print(
                        "-> PacketType: {}\n-> PacketData: {}".format(PACKET['type'], PACKET['data']))
                    self.CMD_ENGINE[PACKET['type']](PACKET['data'])

    def plant(self):
        proj_id = argvalid("Enter Project ID : ",
                           "=(!)=== Project ID should not be null ===(!)=")
        author = argvalid("Enter Author Name : ",
                          "=(!)=== Author field should not be null ===(!)=")
        passwd = argvalid("Enter Project Password : ",
                          "=(!)=== You really need a password for this ===(!)=",
                          ispasswd=True)
        path = argvalid("Enter Project Path (Default : ./): ", "", './')
        prj = projectSeed(project_id=proj_id, author=author,
                          passwd=passwd, path=path)
        # Most of the problem originate here
        packet = self.pack({
            "type": "PLANT",
            "data": self.pack(prj.artifact())
        })
        print(len(packet))
        self.socket_agent.send(packet)

    def test(self):
        print("Sending test requests...")
        self.socket_agent.send(
            self.pack({
                "type": "TEST",
                "data": True
            })
        )

    # Response Functions

    def plant_rsp(self, rsp):
        print("Reccived response")
        if rsp:
            print("Project has been planted!")
        else:
            print("Server Response : PlantFail")
        self.close()
        sys.exit()

    def test_rsp(self, rsp):
        if rsp:
            print("Server Test : OK")
        else:
            print("Server Test : FAIL")
        self.close()
        sys.exit()

    # Packet Functions

    def pack(self, data):
        print("==== START ====\n{}\n==== END ====".format(data.items()))
        packet = pickle.dumps(data)
        print("\nSize={}\n".format(len(packet)))
        return bytes(f"{len(packet):<{self.OFFSET}}", "utf-8")+packet

    def unpack(self, packet):
        return pickle.loads(packet)

    # Just stop everything!

    def close(self):
        print("\nGoodbye!")
        self.socket_agent.close()


# Main Function
if __name__ == "__main__":
    print("< The script is running />")
    parser = argparse.ArgumentParser(description="Test level")
    parser.add_argument("CMD", help="Command here", action="store")
    args = parser.parse_args()
    client = ClientSocket(host="localhost", port=10092)
    cmdPSR = {
        "test": client.test,
        "plant": client.plant
    }
    #session = multiprocessing.Process(target=client.online, daemon=True)
    try:
        cmdPSR[args.CMD]()
        client.online()
        # session.start()
    except KeyboardInterrupt:
        # session.terminate()
        client.close()
    except Exception as e:
        print("Something's wrong \n {}".format(e))
        traceback.print_exception(*sys.exc_info())
