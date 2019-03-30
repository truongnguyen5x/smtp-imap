import base64
import getpass
import socket
import ssl
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from os.path import basename
from tkinter import Tk
from tkinter.filedialog import askopenfilenames

# with smtp.gmail.com: we have 2 method encrypt is TLS and SSL (port 587 and 465)
# smtp-mail.outlook.com: we only use TLS
server = 'smtp.gmail.com'
# server = 'smtp-mail.outlook.com'
port = 587
# port = 465
mailFrom = 'kaironsw@gmail.com'
# mailFrom = 'truongnguyen5x@outlook.com'
to = ['truongnguyen5x@gmail.com']
content = ''
username = 'kaironsw'
# username = 'truongnguyen5x@outlook.com'
password = ''
subject = ''
crypt = 'TLS'
# crypt = 'SSL'
files = []


def show_main_menu():
    print("\r\n1) SMTP Server:    " + server)
    print("2) Port:           " + str(port))
    print("3) Crypto:         " + crypt)
    print("4) From:           " + mailFrom)
    print("5) Add receivers:  " + ", ".join(to))
    print("6) Username:       " + username)
    if password == '':
        print("7) Password:")
    else:
        print("7) Password:       <not displayed>")
    print("8) Add file attachments:")
    for path in files:
        print('\t- ' + path)
    print("9) Write email:    " + subject)
    print("10) Send email")
    print("11) Clear receivers")
    print("12) Clear file attachments")
    print("Q) Quit program")
    print("Choose one option to edit:")


def get_ssl_socket():
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server, port))
        client = context.wrap_socket(client, server_hostname=server)
        client.send('HELO gmail\r\n'.encode())
        print(client.recv(2048).decode().rstrip())
    except Exception as e:
        print(e)
        client.close()
    return client


def get_tls_socket():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server, port))
        print(client.recv(2048).decode().rstrip())

        client.send('HELO gmail\r\n'.encode())
        print(client.recv(2048).decode().rstrip())

        client.send('STARTTLS\r\n'.encode())
        print(client.recv(2048).decode().rstrip())

        client = ssl.wrap_socket(client, ssl_version=ssl.PROTOCOL_TLS)
    except Exception as e:
        print(e)
        client.close()
    return client


def get_socket():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server, port))
    print(client.recv(2048).decode())

    client.send('EHLO gmail\r\n'.encode())
    print(client.recv(2048).decode().rstrip())
    return client


def send_session():
    if crypt.lower() == 'ssl':
        client = get_ssl_socket()
    elif crypt.lower() == 'tls':
        client = get_tls_socket()
    else:
        client = get_socket()

    client.send('HELO gmail\r\n'.encode())
    print(client.recv(2048).decode().rstrip())

    client.send('AUTH LOGIN\r\n'.encode())
    print(client.recv(2048).decode().rstrip())

    user64 = base64.b64encode(username.encode()) + '\r\n'.encode()
    client.send(user64)
    print(client.recv(2048).decode().rstrip())

    pass64 = base64.b64encode((password + '\r\n').encode()) + '\r\n'.encode()
    client.send(pass64)
    print(client.recv(2048).decode().rstrip())

    client.send(('MAIL FROM: <' + mailFrom + '>\r\n').encode())
    print(client.recv(2048).decode().rstrip())

    for people in to:
        client.send(('RCPT TO: <' + people + '>\r\n').encode())
        print(client.recv(2048).decode().rstrip())

    client.send('DATA\r\n'.encode())
    print(client.recv(2048).decode().rstrip())

    msg = MIMEMultipart()
    msg['From'] = mailFrom
    msg['To'] = ", ".join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(content))

    for path in files:
        part = MIMEApplication(open(path, "rb").read(), Name=basename(path))
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(path)
        msg.attach(part)
    client.send(msg.as_string().encode())

    client.send('\r\n.\r\n'.encode())
    print(client.recv(2048).decode().rstrip())

    client.send('QUIT\r\n'.encode())
    print(client.recv(2048).decode().rstrip())

    client.close()


while True:
    print('  ______   __       __  ________ _______                                 __  __ ')
    print(' /      \ /  \     /  |/        /       \                               /  |/  |')
    print('/$$$$$$  |$$  \   /$$ |$$$$$$$$/$$$$$$$  |       _____  ____    ______  $$/ $$ |')
    print('$$ \__$$/ $$$  \ /$$$ |   $$ |  $$ |__$$ |      /     \/    \  /      \ /  |$$ |')
    print('$$      \ $$$$  /$$$$ |   $$ |  $$    $$/       $$$$$$ $$$$  | $$$$$$  |$$ |$$ |')
    print(' $$$$$$  |$$ $$ $$/$$ |   $$ |  $$$$$$$/        $$ | $$ | $$ | /    $$ |$$ |$$ |')
    print('/  \__$$ |$$ |$$$/ $$ |   $$ |  $$ |            $$ | $$ | $$ |/$$$$$$$ |$$ |$$ |')
    print('$$    $$/ $$ | $/  $$ |   $$ |  $$ |            $$ | $$ | $$ |$$    $$ |$$ |$$ |')
    print(' $$$$$$/  $$/      $$/    $$/   $$/             $$/  $$/  $$/  $$$$$$$/ $$/ $$/ ')
    show_main_menu()
    option = input().lower()
    if option == '1':
        server = input('Enter the address of the mail server: ')
    elif option == '2':
        while True:
            p = int(input('Enter the port number to connect to: '))
            if not (p < 0 or p > 65535):
                port = p
                break
            else:
                print('Invalid entry. Port number must be between 0 and 65,535.')
    elif option == '3':
        while True:
            c = input('Choose an encryption protocol (TLS, SSL, or none): ')
            if (c.lower() == 'tls') or (c.lower() == 'ssl') or (c.lower() == 'none'):
                crypt = c
                break
            else:
                print("Invalid choice!")
    elif option == '4':
        mailFrom = input('Enter the email address you\'re sending from: ')
    elif option == '5':
        to.append(input('Add the email address you\'re sending to: '))
    elif option == '6':
        username = input('Enter your username: ')
    elif option == '7':
        password = getpass.getpass('Enter your password: ')
    elif option == '8':
        root = Tk()
        files.extend(root.tk.splitlist(askopenfilenames()))
        root.mainloop()
    elif option == '9':
        subject = input('Enter subject of email: ')
        print('Enter your message below. To finish: enter \'quit\' in new line')
        lines = []
        while True:
            line = input()
            if line.lower() != 'quit':
                lines.append(line)
            else:
                break
        content = '\n'.join(lines)
    elif option == '10':
        send_session()
    elif option == '11':
        to.clear()
    elif option == '12':
        files.clear()
    elif option.lower() == 'q':
        exit()
    else:
        print('Invalid choice. Please enter again.')
