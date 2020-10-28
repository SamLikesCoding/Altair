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


def hasher(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def progressOut(state, end):
    if state == end:
        return 100.0
    else:
        return (state/end)*100.0


class ServerSocket:

    def __init__(self, host="localhost", port=10092):
        if not path.exists(_archive_path_):
            makedirs(_archive_path_)
        print("-> Setting up server...")
        self.server_addr = host
        self.serve_port = port
        print("=> {}:{}".format(self.server_addr, self.serve_port))
        self.OFFSET = 32
        self.agent = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
        # self.agent.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
        self.agent.bind((self.server_addr, self.serve_port))
        self.CMD_EXEC = {
            "TEST": self.test,
            "PLANT": self.plant,
            "REAP": self.reap
        }

    def online(self):
        self.agent.listen()
        print("-> Server : Online")
        while True:
            client, addr = self.agent.accept()
            print("-> {}:{} is connected".format(addr[0], addr[1]))
            # client.setblocking(False)
            thread.start_new_thread(self.service, (client,))

    def service(self, client):
        print("ServiceModule: Active")
        _BFRSET = True
        _FW_LEN = self.OFFSET
        _PBUF = b''
        while True:
            try:
                _BUFFER = client.recv(_FW_LEN)
                if _BUFFER != b'':
                    if _BFRSET:
                        _FW_LEN = int(_BUFFER[:self.OFFSET])
                        print("PacketSize={}".format(_FW_LEN))
                        _BFRSET = False
                    else:
                        _PBUF += _BUFFER
                        if len(_PBUF) < _FW_LEN:
                            _prgs = progressOut(len(_PBUF), _FW_LEN)
                            print("Progress : {0:0.02f}".format(
                                _prgs), end="\r")
                        #self.sendprogress(_prgs, client)
                        elif len(_PBUF) == _FW_LEN:
                            _PACKET = self.unpack(_PBUF)
                            print("\nREQType:{}".format(_PACKET["type"]))
                            self.CMD_EXEC[_PACKET['type']](
                                _PACKET['data'], client)
                            _BFRSET = True
                            _FW_LEN = self.OFFSET
                            _PBUF = b''
                            _BUFFER = b''
            except Exception as E:
                # pass
                print("It's the buffer error")
                traceback.print_exception(*sys.exc_info())

    def plant(self, data, client):
        if data:
            _pid = data['Project-ID']
            _usr = data['Author']
            _pswd = data['Password']
            print("--- Project ---\n {} by {}".format(_pid, _usr))
            _pr_path = path.join(
                _archive_path_,
                hasher(str(_pid+_pswd))+".seed"
            )
            if path.exists(_pr_path):
                self.sendmsg(
                    "The Project is found on server,\nThe existing project will be overwritten", client)
            try:
                print("Writing seed..")
                seeder = open(_pr_path, "wb")
                pickle.dump(data, seeder)
                print("SeedWrite: SUCESS")
                res = True
            except Exception:
                print("SeedWrite: FAIL")
                traceback.print_exception(*sys.exc_info())
                res = False
        else:
            res = False
        client.send(self.pack({
            "type": "PLANT",
            "data": res
        }))

    def reap(self, data, client):
        print("Searching the plant...")
        seedbytes = None
        _pid = data['prj_id']
        _pswd = data['paswd']
        __target_seed__ = path.join(_archive_path_, hasher(_pid+_pswd)+".seed")
        if path.exists(__target_seed__):
            exrtc = open(__target_seed__, 'rb')
            seedbytes = pickle.load(exrtc)
            print("Sending Extract...")
            client.send(self.pack({
                "type": "REAP",
                "data": seedbytes
            }))
            print("Packet Sent...")
        else:
            print("=== Project not found ===")
            client.send(self.pack({
                "type": "REAP",
                "data": None
            }))

    def test(self, data, client):
        if data:
            print("Packet Verified")
            resp = {"type": "TEST", "data": True}
        else:
            print("Packet Verification failed")
            resp = {"type": "TEST", "data": False}
        client.send(self.pack(resp))

    def sendmsg(self, msg, client):
        client.send(self.pack({
            "type": "MESG",
            "data": msg
        }))

    def sendprogress(self, data, client):
        print("Progress : {0:0.02f}".format(data), end='\r')
        client.send(self.pack({
            "type": "PRGS",
            "data": data
        }))

    def unpack(self, packet):
        return pickle.loads(packet)

    def pack(self, data):
        packet = pickle.dumps(data)
        return bytes(f"{len(packet):<{self.OFFSET}}", "utf-8")+packet

    def close(self):
        print("\nGoodbye!")
        self.agent.close()


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
