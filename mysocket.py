import socket,os
from threading import Thread


def print_all_command_client():
    print("please type in commands: ")
    print("msg -send string message")
    print('ls -look all files in current directory')
    print("get filename -download file in current directory")
    print("upload filename -download file in current directory")
    print("exit -exit the client")


class Client_FTP(object):
    def __init__(self) -> None:
        self.socket = socket.socket()

    def client_connect(self, server_ip: str, server_port: int):
        self.socket.connect((server_ip, server_port))

    def send_message(self, message: str):
        self.socket.send(message.encode())

    def recv_message(self, size: int):
        try:
            message = self.socket.recv(size).decode()
            return message
        except Exception as e:
            return e

    def ls_file(self):
        response = self.socket.recv(1024)
        print(response)

    def get_file(self, filename):
        response = self.socket.recv(1024)  # receive file size or "not file"
        if response.decode().startswith("not"):
            print("please input the correct filename.")
            return False

        # get file size at response
        self.socket.send(b'ready to recv data')
        print(response)
        file_size = int(response.decode())
        recv_size = 0

        f = open(filename, 'wb')

        count_recv = 0
        while recv_size < file_size:

            if file_size - recv_size > 1024:
                size = 1024
            else:
                size = file_size - recv_size
                print("last receive:", size)

            recv_data = self.socket.recv(size)
            count_recv += 1
            recv_size += len(recv_data)

            f.write(recv_data)
        else:
            print("download finished, receive data times:{0}".format(count_recv))
            f.close()
        return True

    def upload_file(self, filename:str):
        if os.path.isfile(filename):
            f = open(filename, "rb")
            size = os.stat(filename).st_size  # get size of the file
            # step3: send size of file
            self.socket.send(str(size).encode())
            self.socket.recv(1024)  # step4: receive "ready"

            # for line in f:
            #     self.socket.send(line)
            count_send = 0
            chunk = f.read(1024*1024)
            while chunk:
                self.socket.send(chunk)
                count_send += 1
                chunk = f.read(1024*1024)
                print("Upload Progress: {}%\r".format(count_send*1024*1024/size), end="")


            f.close()
        else:
            print("please input correct filename!")


    def cmd_loop(self):
        while True:
            cmd = input(">>:").strip()

            # 1 - no cmd
            if len(cmd) == 0:
                continue
            # 2 - client exit
            if cmd.startswith("exit"):
                self.socket.close()
                break

            if cmd.startswith("msg"):
                client.send_message(cmd)
            # print(client.recv_message(1024))

            if cmd.startswith("get"):
                client.send_message(cmd)
                filename_get = cmd.split()[1]
                client.get_file(filename=filename_get)

            if cmd.startswith("upload"):
                client.send_message(cmd)
                filename = cmd.split()[1]
                client.upload_file(filename)

            if cmd.startswith("ls"):
                client.send_message(cmd)
                client.ls_file()


class Server_FTP(object):
    def __init__(self):
        self.socket = socket.socket()
        self.conn_pool = {}
        self.count_client = 0

    def server_bind_listen(self, port:int):
        self.socket.bind(("0.0.0.0",port))
        self.socket.listen(8)
        print("server start, wait for client to connect.")

    def accept_client(self):
        while True:
            socket_conn, address_conn = self.socket.accept()
            thread = Thread(target=handle_client, args=(self, socket_conn, address_conn))
            print("client online: ")
            print(address_conn)
            self.conn_pool[address_conn] = socket_conn
            self.count_client +=1
            thread.daemon = True
            thread.start()

    def remove_client(self, address_conn):
        client = self.conn_pool[address_conn]
        if None != client:
            client.close()
            self.conn_pool.pop(address_conn)
            self.count_client -=1
            print("client offline: ")
            print(address_conn)

    def response_get(self, address_conn, filename):
        client = self.conn_pool[address_conn]
        if os.path.isfile(filename):
            f = open(filename, 'rb')
            print(filename)
            file_size = os.stat(filename).st_size
            print(str(file_size).encode())
            client.send(str(file_size).encode())
            client.recv(1024)  # receive "ready"

            count_send = 0

            # for line in f:
            #     client.send(line)
            #     count_send += 1
            #     print(type(line))
            #     print(count_send, " th send, size:", line.__sizeof__())

            chunk = f.read(1024)
            while chunk:
                client.send(chunk)
                count_send += 1
                chunk = f.read(1024)
                print(count_send, " th send, size:", chunk.__sizeof__())


            f.close()

        else:
            client.send("not file".encode())

    def str_filenames_current_path(self):
        listdir = os.listdir(os.getcwd())
        str = []
        for item in listdir:
            str.append(item)
        str1 = ' '.join(str)
        return str1

    def response_ls(self, address_conn):
        client = self.conn_pool[address_conn]
        client.send(self.str_filenames_current_path().encode())

    def response_upload(self, address_conn, filename):
        client = self.conn_pool[address_conn]
        # step2,3: receive size
        response = client.recv(1024)
        client.send(b"ready to recv data")  # step4 send ready
        print("the size of file to receive: "+response.decode())
        file_size = int(response.decode())  # step3 receive size
        recv_size = 0  # size of already receive

        f = open(filename, "wb")

        # step5: receive file
        count_recv = 0
        while recv_size < file_size:

            # define the size of each receive 1024 or file_size%1024
            if file_size - recv_size > 1024*1024:
                size = 1024*1024
            else:
                size = file_size - recv_size
                print("last receive:", size)
            # step5: each recv
            recv_data = client.recv(size)

            count_recv += 1
            recv_size += len(recv_data)
            # verified: here, length of recv_data == size
            # write each receive to file
            f.write(recv_data)
            print("Upload Progress: {}%\r".format(recv_size-file_size), end="")

        else:
            print("upload finished,receive data times: {0}".format(count_recv))
            f.close()


def handle_client(server:Server_FTP, socket_client, address_conn):
    # socket_client.sendall("done connect".encode())
    while True:
        try:
            cmd = socket_client.recv(1024).decode()
            print(cmd)
            if cmd:
                if cmd.startswith("msg"):
                    print(cmd)
                if cmd.startswith("get"):
                    filename = cmd.split()[1]
                    server.response_get(address_conn, filename)
                if cmd.startswith("ls"):
                    server.response_ls(address_conn)
                if cmd.startswith("upload"):
                    filename = cmd.split()[1]
                    server.response_upload(address_conn,filename)
            else:
                socket_client.close()
                server.remove_client(address_conn)
                break

        except Exception as e:
            print(e)
            socket_client.close()
            server.remove_client(address_conn)
            break


if __name__ == '__main__':

    run = 'server'
    # run = 'server'
    if run == 'server':
        server = Server_FTP()
        server.server_bind_listen(8080)
        server.accept_client()
    else:
        client = Client_FTP()
        # client.client_connect("172.20.10.6", 8080)  # matebook on iphone13pro max
        # client.client_connect("172.20.10.8", 8080)  # macbook on iphone13pro max
        # client.client_connect("192.168.43.11", 8080)  # matebook on motor phone
        client.client_connect("124.223.184.248", 8080)  # macbook on motor phone
        client.send_message("connect")
        client.cmd_loop()
