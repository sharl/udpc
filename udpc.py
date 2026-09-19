# -*- coding: utf-8 -*-
import queue
import socket
import threading

ADDR = '127.0.0.1'
BADD = '127.255.255.255'
PORT = 18765
BUFSIZE = 4096


class Client:
    def __init__(self, addr=BADD, port=PORT):
        self.bind = (addr, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def send(self, cmd):
        self.sock.sendto(cmd.encode(), self.bind)


class Server:
    def __init__(self, addr=ADDR, port=PORT):
        self.stop_event = threading.Event()
        self.queue = queue.Queue()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((addr, port))

    def task(self, cmd):
        # do nothing
        pass

    def recv(self):
        while not self.stop_event.is_set():
            try:
                cmd = self.queue.get(timeout=0.1)
                self.task(cmd)
            except Exception:
                pass

    def wait(self):
        while not self.stop_event.is_set():
            data, address = self.sock.recvfrom(BUFSIZE)
            cmd = data.decode()
            self.queue.put(cmd)

    def stop(self):
        self.stop_event.set()

    def run(self):
        self.stop_event.clear()

        threading.Thread(target=self.recv, daemon=True).start()
        threading.Thread(target=self.wait, daemon=True).start()

        while not self.stop_event.is_set():
            try:
                if self.stop_event.wait(1):
                    break
            except KeyboardInterrupt:
                break


if __name__ == '__main__':
    class cmd_server(Server):
        def task(self, cmd):
            print(cmd)
            if cmd.upper() == 'QUIT':
                self.stop()

    cmd_server().run()
    print('done')
