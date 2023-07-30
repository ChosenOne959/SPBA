from xmlrpc.client import ServerProxy
import threading
from new_ui.RPC import RPC_server
import new_ui.SPBA_API as SPBA_API
import time
import subprocess

# public ip of remote server
remote_host = '202.120.37.157'

class RPC_client:
    def __init__(self, SharedData):
        self.SharedData = SharedData
        self.is_localhost = SharedData.is_localhost
        self.SharedData.add_resources('RPC_client', self)
        if(self.is_localhost):
            # print('client: starting local server')
            # self.server_thread = threading.Thread(target=RPC.RPC_server.start_server(), args=(self.is_localhost)).start()
            # print('client: initializing local server')
            # self.server = ServerProxy("http://localhost:13333", allow_none=True) # 初始化服务器
            self.server = RPC_server.server_API(is_localhost=True)
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
        if param_data == {}:
            return False
        return self.server.set_params(param_data)

    def set_param(self, param: str, value):
        self.server.set_param(param, value)

    def get_params(self):
        return self.server.get_params()

    def start_simulator(self):
        return self.server.start_simulator()

    def kill_task(self, local: bool, task_name: str):
        if local:
            args = ["powershell", "./KillTask.ps1", task_name]
            shell = subprocess.Popen(args, stdout=subprocess.PIPE)
            return True
        else:
            return self.server.kill_task(task_name)
