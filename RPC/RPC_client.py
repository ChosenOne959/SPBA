from xmlrpc.client import ServerProxy

remote_host = '202.120.37.157'

class RPC_client:
    def __init__(self, is_localhost=True):
        if(is_localhost):
            self.server = ServerProxy("http://localhost:13333", allow_none=True) # 初始化服务器
        else:
            self.server = ServerProxy("http://"+remote_host+":13333", allow_none=True) # 初始化服务器

    def json_dump(self, filename: str, data):
        self.server.json_dump(filename, data)

    def json_load(self, filename: str):
        self.server.json_load(filename)

if __name__ == '__main__':
    server = ServerProxy("http://localhost:13333") # 初始化服务器
    print (server.add(3,5)) # 调用函数并传参