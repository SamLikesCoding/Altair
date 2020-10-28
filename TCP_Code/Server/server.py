"""
    Altair - Server Script (TCP)
"""

# Required Libraries
from os import path, makedirs
import _thread as thread
from glob import glob
import socket as skt
import traceback
import hashlib
import pickle
import sys

# Archive path : where seeds are stored
_archive_path_ = "./chamber"

# Poetry


class ServerSocket:

    def __init__(self, host="localhost", port=10092):
        if not path.exists(_archive_path_):
            makedirs(_archive_path_)
        print("-> Setting up server...")
        self.server_addr = host
        self.serve_port = port
        print("= {}:{}".format(self.server_addr, self.serve_port))
        self.OFFSET = 8
        self.socket_agent = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        # self.socket_agent.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
        self.socket_agent.bind((self.server_addr, self.serve_port))
        self.CMD_ENGINE = {
            "TEST": self.test,
            "PLANT": self.plant
        }

    def online(self):
        self.socket_agent.listen()
        print("-> Server : Online")
        while True:
            client, addr = self.socket_agent.accept()
            print("-> {}:{} is connected".format(addr[0], addr[1]))
            thread.start_new_thread(self.service, (client,))

    def service(self, client):
        C_SIZE = 0
        BUF_RSET = True
        BUFFER = b''
        FRAME_LEN = self.OFFSET
        while True:
            FRAME = client.recv(FRAME_LEN)
            if FRAME != b'':
                if BUF_RSET:
                    FRAME_LEN = int(FRAME[:self.OFFSET])
                    print("PacketSize={}".format(FRAME_LEN))
                    BUF_RSET = False
                else:
                    # print(FRAME)
                    BUFFER = BUFFER + FRAME
                    C_SIZE = C_SIZE + len(FRAME)
                    print("PacketGrowth : {}".format(C_SIZE))
                    if C_SIZE == FRAME_LEN:
                        print("--- Writing buffer out ---")
                        PACKET = self.unpack(BUFFER)
                        self.CMD_ENGINE[PACKET['type']](PACKET['data'], client)
                        FRAME_LEN = self.OFFSET
                        BUF_RSET = True

    def unpack(self, packet):
        return pickle.loads(packet)

    def pack(self, data):
        packet = pickle.dumps(data)
        return bytes(f"{len(packet):<{self.OFFSET}}", "utf-8")+packet

    def filePack(self, data, hash):
        try:
            if not path.exists(_archive_path_):
                makedirs(_archive_path_)
            fhead = open(path.join(_archive_path_,
                                   "{}.store".format(hash)), 'wb')
            pickle.dump(data, fhead)
            fhead.close()
            print("--- project packed ---")
            return True
        except Exception as e:
            print("=== Something's wrong ===\n{}".format(e))
            return False

    def hasher(self, stringInput):
        return hashlib.sha256(stringInput.encode('utf-8')).hexdigest()

    def plant(self, data, client):
        print("Planting new artifact...")
        if data:
            print("Seed verified")
            _data = self.unpack(data[self.OFFSET:])
            _id = _data['Project_ID']
            _pwd = _data['passwd']
            prj_hash = self.hasher(_id+_pwd)
            if self.filePack(_data, prj_hash):
                resp = {"type": "PLANT", "data": True}
            else:
                resp = {'type': "PLANT", "data": False}
        else:
            print("Seed courrpted")
            resp = {"type": "PLANT", "data": False}
        client.send(self.pack(resp))
        print("==== Response Sent ====")

    def test(self, data, client):
        if data:
            print("Packet Verified")
            resp = {"type": "TEST", "data": True}
        else:
            print("Packet Verification failed")
            resp = {"type": "TEST", "data": False}
        client.send(self.pack(resp))

    def close(self):
        print("\nGoodbye!")
        self.socket_agent.close()


# Main function
if __name__ == "__main__":
    print("_/_/_/_/ Running Script _/_/_/_/")
    server = ServerSocket()
    try:
        server.online()
    except KeyboardInterrupt:
        server.close()
    except Exception as e:
        print("Somenthing's wrong \n {}".format(e))
        traceback.print_exception(*sys.exc_info())
