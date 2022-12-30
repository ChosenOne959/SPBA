import subprocess

# 管理员身份运行Set-ExecutionPolicy RemoteSigned
if __name__ == '__main__':
    args = ["powershell", "../start.ps1", "$True"]
    shell = subprocess.Popen(args, stdout=subprocess.PIPE)
    output_bytes = shell.stdout.read()
    output = output_bytes.decode('utf-8')
    print(output)