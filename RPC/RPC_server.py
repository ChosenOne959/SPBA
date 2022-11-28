from xmlrpc.server import SimpleXMLRPCServer
import socket
import json
import threading

# private ip of remote server
remote_host = '192.168.31.69'

class tcp_mapping:
    def __init__(self):
        self.PKT_BUFF_SIZE = 2048
        self.local_ip = '127.0.0.1'
        self.local_port = '41451'
        self.remote_ip = '192.168.31.69'
        self.remote_port = '41451'
    def tcp_mapping_worker(self, conn_receiver, conn_sender):
        while True:
            try:
                data = conn_receiver.recv(self.PKT_BUFF_SIZE)
            except Exception:
                print('Event: Connection closed.')
                break
            if not data:
                print('Info: No more data is received.')
                break
            try:
                conn_sender.sendall(data)
            except Exception:
                print('Error: Failed sending data.')
                break
        # send_log('Info: Mapping data > %s ' % repr(data))
        print('Info: Mapping >%s->%s>%dbytes.' % (conn_receiver.getpeername(), conn_sender.getpeername(), len(data)))
        conn_receiver.close()
        conn_sender.close()
        return

    def tcp_mapping_request(self, local_conn, remote_ip, remote_port):
        remote_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            remote_conn.connect((remote_ip, remote_port))
        except Exception:
            local_conn.close()
            print('Error: Unable to connect to the remote server.')
            return
        threading.Thread(target=self.tcp_mapping_worker, args=(local_conn, remote_conn)).start()
        threading.Thread(target=self.tcp_mapping_worker, args=(remote_conn, local_conn)).start()
        return

    def tcp_mapping(self, remote_ip='', remote_port='', local_ip='', local_port=''):
        if not remote_ip:
            remote_ip = self.remote_ip
            remote_port = self.remote_port
            local_ip = self.local_ip
            local_port = self.local_port
        local_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_server.bind((local_ip, local_port))
        local_server.listen(1)
        print('Event: Starting mapping service on ' + local_ip + ':' + str(local_port) + ' ...')
        while True:
            try:
                (local_conn, local_addr) = local_server.accept()
            except KeyboardInterrupt:
                local_server.close()
                print('Event: Stop mapping service.')
                break
        threading.Thread(target=self.tcp_mapping_request, args=(local_conn, remote_ip, remote_port)).start()
        print('Event: Receive mapping request from%s:%d.' % local_addr)
        return

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
        # need to start a tcp_mapping if use remote server
        mapping = tcp_mapping
        threading.Thread(target=mapping.tcp_mapping, args=('127.0.0.1', '41451', remote_host, '41451')).start()
        print("server: Listening on remote port 41451")




if __name__ == "__main__":
    start_server(is_localhost=True)

