#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # data must be splitted line by line before passed in
        return data[0]

    def parse_code(self, data):
        try:
            return int(data.split()[1])
        except:
            return 500

    def get_headers(self, data):
        # data must be splitted line by line before passed in
        for i in range(1, len(data)):
            # found the empty line, take all lines before(except for status code line)
            if not data[i]: return "\r\n".join(data[1:i+1])
    
    def parse_headers(self, data):
        header_dict = {}
        for each in data.splitlines():
            # use one-element list to prevent unpack error
            for key, value in [each.split(": ", 1)]:
                header_dict[key] = value
        return header_dict

    def get_body(self, data):
        # data must be splitted line by line before passed in
        for i in range(1, len(data)):
            # found the empty line, take all line after
            if not data[i]: return "\r\n".join(data[i+1:]) + "\r\n"
        
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    def recvall(self, sock):
        # read everything from the socket
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        # https://docs.python.org/3/library/urllib.parse.html Author: python officials, Last Updated : Unknown
        parsedurl = urllib.parse.urlparse(url)
        port = parsedurl.port if parsedurl.port else 80
        path = parsedurl.path if parsedurl.path else "/"

        self.connect(parsedurl.hostname, port)
        self.sendall(f"GET {path} HTTP/1.1\r\nHost: {parsedurl.netloc}\r\nConnection: close\r\n\r\n")
        self.data = self.recvall(self.socket)
        self.close()
        self.splitteded_data = self.data.splitlines()
        code = self.parse_code(self.get_code(self.splitteded_data))
        body = self.get_body(self.splitteded_data)
        return HTTPResponse(code, body)
    
    def generate_post_body(self, args):
        if not args: return ""
        if not len(args.items()): return ""
        # https://www.geeksforgeeks.org/comprehensions-in-python/ Author: rituraj_jain, Last Updated : 14 Nov, 2018
        body = "&".join([f"{key}={value}" for key, value in args.items()])
        return body

    def POST(self, url, args=None):
        code = 500
        body = self.generate_post_body(args)

        parsedurl = urllib.parse.urlparse(url)
        port = parsedurl.port if parsedurl.port else 80
        path = parsedurl.path if parsedurl.path else "/"

        self.connect(parsedurl.hostname, port)

        self.sendall(f"POST {path} HTTP/1.1\r\n" +
                     f"Host: {parsedurl.netloc}\r\n" +
                      "Content-Type: application/x-www-form-urlencoded\r\n" +
                      "Connection: close\r\n" +
                     f"Content-Length: {len(body)}\r\n" +
                      "\r\n" +
                     f"{body}\r\n")

        self.data = self.recvall(self.socket)
        self.close()
        self.splitteded_data = self.data.splitlines()
        code = self.parse_code(self.get_code(self.splitteded_data))
        body = self.get_body(self.splitteded_data)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        res = client.command( sys.argv[2], sys.argv[1] )
        print(res.code)
        print(res.body)
    else:
        res = client.command( sys.argv[1] )
        print(res.code)
        print(res.body)