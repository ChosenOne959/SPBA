from xmlrpc.server import SimpleXMLRPCServer
import json

remote_host = '202.120.37.157'

class server_API:
    def __init__(self, is_localhost=True):
        self.is_localhost = is_localhost
        if(is_localhost):
            with open('./Setting_Path/configuration_file.json', 'r') as cfile_path:
                self.path_data = json.load(cfile_path)['path']
        else:
            with open('./Setting_Path/remote_configuration_file.json', 'r') as cfile_path:
                self.path_data = json.load(cfile_path)['path']
        print(self.path_data)

    def json_dump(self, filename: str, data):
        print("json_dump!")
        with open(self.path_data[filename], 'w', encoding='utf8')as file:
            json.dump(data, file, ensure_ascii=False, allow_nan=True)

    def json_load(self, filename: str):
        print("json_load!")
        with open(self.path_data[filename], 'r', encoding='utf8')as file:
            data = json.load(file)
        return data



def start_server(is_localhost=True):
    obj = server_API(is_localhost=is_localhost)
    if(is_localhost):
        server = SimpleXMLRPCServer(('localhost', 13333), allow_none=True)

        # 将实例注册给 rpc server  并指定 别名(在客户端中调用)
        server.register_instance(obj)

        print("server: Listening on local port 13333")
        server.serve_forever()
    else:
        server = SimpleXMLRPCServer((remote_host, 13333), allow_none=True)

        # 将实例注册给 rpc server  并指定 别名(在客户端中调用)
        server.register_instance(obj)

        print("server: Listening on remote port 13333")
        server.serve_forever()

if __name__ == "__main__":
    start_server(True)
