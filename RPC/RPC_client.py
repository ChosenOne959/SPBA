from xmlrpc.client import ServerProxy
import threading, RPC.RPC_server
import time

# public ip of remote server
remote_host = '202.120.37.157'

class RPC_client:
    def __init__(self, is_localhost=True):
        self.is_localhost = is_localhost
        if(is_localhost):
            # print('client: starting local server')
            # self.server_thread = threading.Thread(target=RPC.RPC_server.start_server(), args=(self.is_localhost)).start()
            # print('client: initializing local server')
            # self.server = ServerProxy("http://localhost:13333", allow_none=True) # 初始化服务器
            self.server = RPC.RPC_server.server_API(is_localhost=True)
        else:
            self.server = ServerProxy("http://"+remote_host+":13333", allow_none=True) # 初始化服务器
        print('RPC_client started')
        # time.sleep(0.2)

    def json_dump(self, filename: str, data):
        self.server.json_dump(filename, data)

    def json_load(self, filename: str):
        return self.server.json_load(filename)

    def set_params(self, param_data={}):
        """

        :param param_data:
        :return: True (successful)
        """
        return self.server.set_params(param_data)

    def set_param(self, param: str, value):
        self.server.set_param(param, value)

    def get_params(self):
        return self.server.get_params()