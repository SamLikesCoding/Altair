"""
    Altair - Server Script (UDP)
"""

# Required Libraries
from os import path, makedirs
import socket as SKT
from glob import glob
import traceback
import hashlib
import pickle
import sys

# Archive path : where seeds are
_arch_path_ = "./chamber"

# Poetry


class ServerSocket:

    def __init__(self, host='localhost', port=10092):
        if not path.exists(_arch_path_):
            makedirs(_arch_path_)
        print("=== Altair : Project Server ===\n\n")
        print(" Server is warming up....")
        self.CMD_EXEC = {
            "plant": self.plant,
            "test": self.test
        }
        self._END_STATE_ = False
        self.host = host
        self.port = port
        print(" Setting server to address ({}:{})".format(
            self.host, self.port))
        self.agent = SKT.socket(SKT.AF_INET, SKT.SOCK_DGRAM)
        self.agent.bind((self.host, self.port))
        print("==== Server is online====\n")
        while not self._END_STATE_:
            _BUFFER = self.agent.recvfrom(4096)
            if _BUFFER:
                _CADR = _BUFFER[1]
                _PACKET = self.unpack(_BUFFER[0])
                _PTYPE = _PACKET['type']
                if _PTYPE == 'req':
                    _CMD = _PACKET['rtype']
                    _DATA = _PACKET['data']
                    print("ClientRequest from {}:{} => {}".format(
                        _CADR[0], _CADR[1], _CMD))
                    self.CMD_EXEC[_CMD](_CADR, _DATA)

    def plant(self, cadr, data):
        print("planting seed from {}:{}".format(cadr[0], cadr[1]))
        if data:
            print("Seed Verified")
            print(data)
            _rsp = self.pack({
                "type": "rsp",
                "rtype": "plant",
                "data": True
            })
        else:
            print("Seed Courupted")
            _rsp = self.pack({
                "type": "rsp",
                "rtype": "plant",
                "data": False
            })
        self.agent.sendto(_rsp, cadr)

    def test(self, cadr, data):
        if data:
            print("TestValue : {}".format(data))
            self.agent.sendto(self.pack({
                "type": "rsp",
                "rtype": "test",
                "data": data
            }), cadr)
        else:
            print("TestValue : {}".format(data))
            self.agent.sendto(self.pack({
                "type": "rsp",
                "rtype": "test",
                "data": data
            }), cadr)

    def unpack(self, packet):
        return pickle.loads(packet)

    def pack(self, data):
        return pickle.dumps(data)


if __name__ == "__main__":
    try:
        server = ServerSocket()
    except Exception as e:
        print("Somethin went wrong!!\n\n")
        traceback.print_exception(*sys.exc_info())
        sys.exit()
