import socket
import os
 
def send_command(control_socket, command):
    control_socket.sendall((command + "\r\n").encode('utf-8'))
 
def read_response(control_socket):
    response = control_socket.recv(4096).decode('utf-8')
    print(response)
    return response
 
def _open_data_connection(control_socket, active):
    if active:
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.bind(("127.0.0.1", 22222))
        data_socket.listen(1)
 
        send_command(control_socket, "PORT 127,0,0,1,86,206")
        read_response(control_socket)
 
        conn = data_socket.accept()[0]
        return conn
    else:
        send_command(control_socket, "PASV")
        response = read_response(control_socket)
 
        ip_port = response[response.find("(") + 1:response.find(")")].split(",")
        ip = ".".join(ip_port[:4])
        port = int(ip_port[4]) * 256 + int(ip_port[5])
 
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.connect((ip, port))                 
        return data_socket
 
def upload_file(control_socket):
    filepath = input("Введите путь к файлу для загрузки: ").strip()
    if not os.path.exists(filepath):
        print("Файл не найден.")
        return
 
    data_socket = _open_data_connection(control_socket, active=False)
    filename = os.path.basename(filepath)
    send_command(control_socket, f"STOR {filename}")
    read_response(control_socket)
 
    with open(filepath, 'rb') as file:
        data_socket.sendall(file.read())
    data_socket.close()
    read_response(control_socket)
 
def download_file(control_socket):
    filename = input("Введите имя файла для загрузки: ").strip()
    dest_path = input("Введите путь для сохранения файла: ").strip()
 
    data_socket = _open_data_connection(control_socket, active=False)
    send_command(control_socket, f"RETR {filename}")
    read_response(control_socket)
 
    with open(dest_path, 'wb') as file:
        while True:
            data = data_socket.recv(4096)
            if not data:
                break
            file.write(data)
    data_socket.close()
    read_response(control_socket)
 
def list_files(control_socket):
    data_socket = _open_data_connection(control_socket, active=False)
    send_command(control_socket, "LIST")
    full_data = ""
    while True:
        data = data_socket.recv(4096).decode('utf-8')
        if not data:
            break
        full_data += data
    print(full_data)  
    data_socket.close()
    read_response(control_socket)

 
def main():
    server = "127.0.0.1"
    port = 21
    control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control_socket.connect((server, port))
    read_response(control_socket)
 
    username = input("Введите имя пользователя: ").strip()
    password = input("Введите пароль: ").strip()
    send_command(control_socket, f"USER {username}")
    read_response(control_socket)
    send_command(control_socket, f"PASS {password}")
    read_response(control_socket)
 
    while True:
        command = input("Введите команду (CWD, MKD, RMD, RNFR, RNTO, LIST, STOR, RETR, QUIT): ").strip().upper()
        if command == "QUIT":
            send_command(control_socket, "QUIT")
            read_response(control_socket)
            control_socket.close()
            break
        elif command == "CWD":
            directory = input("Введите директорию: ").strip()
            send_command(control_socket, f"CWD {directory}")
            read_response(control_socket)
        elif command == "MKD":
            directory = input("Введите название директории: ").strip()
            send_command(control_socket, f"MKD {directory}")
            read_response(control_socket)
        elif command == "RMD":
            directory = input("Введите название директории для удаления: ").strip()
            send_command(control_socket, f"RMD {directory}")
            read_response(control_socket)
        elif command == "RNFR":
            filename = input("Введите имя файла для переименования: ").strip()
            send_command(control_socket, f"RNFR {filename}")
            read_response(control_socket)
        elif command == "RNTO":
            new_filename = input("Введите новое имя файла: ").strip()
            send_command(control_socket, f"RNTO {new_filename}")
            read_response(control_socket)
        elif command == "LIST":
            list_files(control_socket)
        elif command == "STOR":
            upload_file(control_socket)
        elif command == "RETR":
            download_file(control_socket)
        else:
            print("Неизвестная команда. Попробуйте снова.")
 
if __name__ == "__main__":
    main()