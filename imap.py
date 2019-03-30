import getpass
import socket as sock
import ssl
import re
import sys
from prettytable import PrettyTable
import math

tag = 0
server = 'imap.gmail.com'
# server = 'imap-mail.outlook.com'
port = 993  # or 143
username = 'truongnguyen5x'
# username = 'truongnguyen5x@outlook.com'
password = ''
crypt = 'SSL'
count_email = 0
page = 0
headers = []
email_per_page = 10


def send_command(command, socket):
    global tag
    code = hex(tag)[2:]
    socket.send((code + ' ' + command + '\r\n').encode())
    tag += 1
    resp = socket.recv(2048).decode('utf-8')
    while code + " OK" not in resp:
        resp += socket.recv(2048).decode('utf-8')
    return resp


def get_ssl_socket():
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        client = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        client.connect((server, port))
        client = context.wrap_socket(client, server_hostname=server)
        print(client.recv(2048).decode().rstrip())
    except Exception as e:
        print(e)
        client.close()
    return client


def get_stl_socket():
    return None


def get_header(socket, index):
    resp = send_command('FETCH ' + str(index) + ' (FLAGS BODY.PEEK[HEADER.FIELDS (SUBJECT DATE FROM)])', socket)

    p = re.compile(r"FLAGS \(\\\w+\)")
    flag = p.findall(resp)
    if not flag:
        flag = 'UnSeen'
    else:
        flag = flag[0]
        id1 = flag.find('\\') + 1
        id2 = flag.find(')', id1)
        flag = flag[id1:id2]
    p = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    email = p.findall(resp)[0]
    p = re.compile(r"Subject:.*\s")
    result = p.findall(resp)
    if not result:
        subject = 'No subject'
    else:
        subject = result[0][9:-2]
        subject = subject if subject != '' else 'No subject'
    p = re.compile(r"\d{1,2} [A-Z][a-z][a-z] \d\d\d\d \d\d:\d\d:\d\d")
    date = p.findall(resp)[0]
    return {"no": index, "flag": flag, "date": date, "from": email, "subject": subject}


def get_headers(socket):
    global headers
    headers = []
    if count_email == 0:
        return
    start = page * email_per_page + 1
    end = start + email_per_page - 1
    if end > count_email:
        end = count_email
    for i in range(start, end + 1):
        item = get_header(socket, i)
        headers.append(item)


def show_list_header():
    total_page = math.ceil(count_email / email_per_page)
    print("Showing page " + str(page + 1) + ' per ' + str(total_page) + ' of ' + str(count_email) + ' emails:')
    t = PrettyTable(['No', 'Flag', 'Date', 'From', 'Subject'])
    for item in headers:
        t.add_row([item["no"], item["flag"], item["date"], item["from"], item["subject"]])
    print(t)


def previous():
    global page
    if math.ceil(count_email / email_per_page) == 1:
        return
    if page == 0:
        page = int(count_email / email_per_page) 
    else:
        page -= 1


def next():
    global page
    if math.ceil(count_email / email_per_page) == 1:
        return
    if page == int(count_email / email_per_page):
        page = 0
    else:
        page += 1


def read_email(socket, index):
    response = send_command('fetch ' + str(index) + ' (BODY[TEXT])', socket)
    p = re.compile(r"--.*Content-Type: text/plain", re.DOTALL)
    m = p.search(response)
    if m is None:
        text_plain = response
    else:
        title = m.group()[:-26]
        id1 = response.find('\r\n\r\n', m.end())
        id2 = response.find(title, id1)
        text_plain = response[id1:id2].strip('\r\n')
    temp = get_header(socket, index)
    t = PrettyTable(header=False)
    t.add_row(['From', temp["from"]])
    t.add_row(['Date', temp["date"]])
    t.add_row(['Subject', temp["subject"]])
    t.hrules = 1
    print(t)
    print('Email content:')
    count = 0
    while count <= len(text_plain) / 1000:
        end = (count + 1) * 1000
        if end > len(text_plain):
            print(text_plain[count * 1000:len(text_plain)])
            input('\r\nPress enter to menu')
        else:
            print(text_plain[count * 1000:end])
            opt = input("\r\nN to next, Q to mail menu:")
            if opt.lower() == 'q':
                break
        count += 1


def login_menu():
    print(".___   _____      _____ __________  _____  ")
    print("|   | /     \    /  _  \\\\______   \/  |  | ")
    print("|   |/  \ /  \  /  /_\  \|     ___/   |  |_")
    print('|   /    Y    \/    |    \    |  /    ^   /')
    print('|___\____|__  /\____|__  /____|  \____   |')
    print('            \/         \/             |__|')

    print("\r\n1) IMAP Server:    " + server)
    print("2) Port:           " + str(port))
    print("3) Crypto:         " + crypt)
    print("4) Username:       " + username)
    if password == '':
        print("5) Password:")
    else:
        print("5) Password:       <not displayed>")
    print("6) Login")
    print("Q) Quit program")
    print("Choose one option to edit:")


def mail_menu():
    print("\r\nA) Previous page")
    print("B) Next page:")
    print("C) Choose a page: ")
    print("Q) Quit menu:")
    print("Enter A, B, C, Q or a number of email to read:")


while True:
    login_menu()
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
        pass
        while True:
            c = input('Choose an encryption protocol (TLS, SSL): ')
            if (c.lower() == 'tls') or (c.lower() == 'ssl'):
                cryptMethod = c
                break
            else:
                print("Invalid choice!")
    elif option == '4':
        username = input('Enter your username: ')
    elif option == '5':
        password = getpass.getpass('Enter your password: ')
    elif option == '6':
        if crypt.lower() == 'ssl':
            socket = get_ssl_socket()
        else:
            socket = get_stl_socket()
        socket.send((hex(tag)[2:] + ' login ' + username + ' ' + password + '\r\n').encode())
        socket.recv(2048)
        tag += 1

        response = send_command('select INBOX', socket)
        p = re.compile(r"\d+ EXISTS")
        count_email = int(p.findall(response)[0][:-7])
        # print(response)

        page = 0
        get_headers(socket)
        while True:
            show_list_header()
            mail_menu()
            opt = input().lower()
            if opt == 'a':
                previous()
                get_headers(socket)
            elif opt == 'b':
                next()
                get_headers(socket)
            elif opt == 'c':
                page = int(input('Enter a page number:')) - 1
                get_headers(socket)
            elif opt == 'q':
                resp = send_command('logout', socket)
                print(resp)
                socket.close()
                socket = None
                break
            else:
                index = int(opt)
                read_email(socket, index)
    elif option.lower() == 'q':
        exit()
    else:
        print('Invalid choice. Please enter again.')
