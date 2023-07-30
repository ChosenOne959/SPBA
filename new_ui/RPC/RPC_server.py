# -*- coding: utf-8 -*-
from xmlrpc.server import SimpleXMLRPCServer
import socket
import json
import threading
import re
import subprocess
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
        print('server: initializing server_API')
        self.is_localhost = is_localhost
        self.param_data = self.init_param_data()
        if(is_localhost):
            print('server: reading path data in configuration.json')
            with open('./configuration_file.json', 'r') as cfile_path:
                self.path_data = json.load(cfile_path)['path']
        else:
            print('server: reading path data in remote_configuration.json')
            with open('./remote_configuration_file.json', 'r') as cfile_path:
                self.path_data = json.load(cfile_path)['path']
        print('server: path data is '+str(self.path_data))

    @staticmethod
    def init_param_data():
        param_data = {'Rotor_params': {'Thrust': {'Name': 'C_T'}, 'Torque': {'Name': 'C_P'}, 'Air': {'Name': 'air_density'}, 'Revolutions': {'Name': 'max_rpm'}}}
        for parameter, value in param_data['Rotor_params'].items():
            value['DataType'] = 'real_T'
        return param_data

    def json_dump(self, filename: str, data):
        print("json_dump!")
        with open(self.path_data[filename], 'w', encoding='utf8')as file:
            json.dump(data, file, ensure_ascii=False, allow_nan=True)

    def json_load(self, filename: str):
        print("json_load!")
        with open(self.path_data[filename], 'r', encoding='utf8')as file:
            data = json.load(file)
        return data

    def set_param(self, param: str, value):
        pass

    def set_params(self, param_data={}):
        print('set params!')
        if param_data == {}:
            print('failure: received empty params')
            return False
        self.param_data = param_data
        for param_kind, params in self.param_data.items():
            param_list = []
            for param, attr in self.param_data[param_kind].items():
                new_str = attr['DataType'] + ' ' + attr['Name'] + ' = ' + attr['Value'] + 'f'
                old_str = attr['OldStr']
                param_list.append((old_str, new_str))
                attr['OldStr'] = new_str
            with open(self.path_data[param_kind], "r+", encoding="utf-8") as f1:
                lines = []
                for line in f1:
                    for str_tuple in param_list:
                        if str_tuple[0] in line:
                            line = line.replace(*str_tuple)
                            lines.append(line)
                            break

            with open(self.path_data[param_kind], "w+", encoding="utf-8") as f1:
                for line in lines:
                    f1.write(line)
        return True

    def get_params(self):
        print('get params!')
        with open(self.path_data['Rotor_params'], "r+") as file:
            for line in file:
                for param, attr in self.param_data['Rotor_params'].items():
                    pattern = attr['DataType']+' '+attr['Name']+' = (.*?)f'
                    value_str =  "".join(re.findall(pattern, line))
                    old_str = attr['DataType']+' '+attr['Name']+' = '+value_str+'f'
                    if value_str != '':
                        attr['Value'] = eval(value_str)
                        attr['OldStr'] = old_str
        return self.param_data
                # Thrust_str = "".join(re.findall(r'real_T C_T = (.*?)f', line))
                # Torque_str = "".join(re.findall(r'real_T C_P = (.*?)f', line))
                # Air_str = "".join(re.findall(r'real_T air_density = (.*?)f', line))
                # Revolutions_str = "".join(re.findall(r'real_T max_rpm = (.*?)f', line))
                # if Thrust_str != "":
                #     self.Thrust_old_str = "real_T C_T = " + Thrust_str
                #     self.Thrust_SpinBox.setProperty("value", eval(Thrust_str))
                # if Torque_str != "":
                #     self.Torque_old_str = "real_T C_P = " + Torque_str
                #     self.Torque_SpinBox.setProperty("value", eval(Torque_str))
                # if Air_str != "":
                #     self.Air_old_str = "real_T air_density = " + Air_str
                #     self.Air_SpinBox.setProperty("value", eval(Air_str))
                # if Revolutions_str != "":
                #     self.Revolutions_old_str = "real_T max_rpm = " + Revolutions_str
                #     self.Revolutions_SpinBox.setProperty("value", eval(Revolutions_str))

    def start_simulator(self):
        # 管理员身份运行Set-ExecutionPolicy RemoteSigned
        if self.is_localhost:
            args = ["powershell", "./start.ps1", "$True"]
        else:
            args = ["powershell", "./start.ps1", "$False"]
        shell = subprocess.Popen(args, stdout=subprocess.PIPE)
        # output_bytes = shell.stdout.read()
        # output = output_bytes.decode('utf-8')
        # print(output)
        return True

    def kill_task(self, task_name: str):
        args = ["powershell", "./KillTask.ps1", task_name]
        shell = subprocess.Popen(args, stdout=subprocess.PIPE)
        return True




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
    start_server(is_localhost=False)

