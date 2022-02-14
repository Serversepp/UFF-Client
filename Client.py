import socket
import ssl
import threading
import tkinter
import tkinter.scrolledtext
import binascii
from tkinter import simpledialog

from Crypto.PublicKey import RSA
from Crypto import Random

class Client:

    def __init__(self, port, host): # host is ip of server
        if "." in host:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

        ###TLS###
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock = ssl.wrap_socket(self.sock )# keyfile=".\\Key\\MyKeys.key", certfile=".\\Key\\MyCertificates.crt"
        self.sock.connect((host, port))

        if not self.logginprocedure(): exit(-2)

        self.running = True
        self.gui_build = False

        gui_thread = threading.Thread(target=self.Gui_Loop)
        recive_thread = threading.Thread(target=self.recive)

        gui_thread.start()
        recive_thread.start()

    def logginprocedure(self):
        self.random_generator = Random.new().read
        msg = tkinter.Tk()
        msg.withdraw()

        self.configstring = self.sock.recv(1024).decode('utf-8')

        if self.configstring[0] == 1:
            print(" Server refused connection ")
            exit(0)

        if self.configstring[4] == '1':
            pass # ADD PASSWD WITH RSA KEY EXCHANGE HERE

        if self.configstring[1] == '1' and self.configstring[2:3] != "11":
            pass # ADD AES KEY OVER RSA HERE


        self.nick = simpledialog.askstring("Nickname", "PLease Enter your nickname",
                                           parent=msg)  # TODO add loop until Nick not already in use
        return 1

    def Gui_Loop(self):
        self.window = tkinter.Tk()
        self.window.configure(bg="black")

        self.chat_label = tkinter.Label(self.window, text="UFF-Chat", fg="lightgray", bg="black")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.window)
        self.text_area.pack(padx=20,pady=5)
        self.text_area.config(state='disabled', fg="lightgray", bg="black")

        self.chat_label = tkinter.Label(self.window, text="Message")
        self.chat_label.config(font=("Arial", 12), fg="lightgray", bg="black")
        self.chat_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.window, height=5)
        self.input_area.config( fg="lightgray", bg="black")
        self.input_area.pack(padx=20,pady=5)

        self.send_button = tkinter.Button(self.window, text="Send", command=self.write)
        self.send_button.config(font=("Arial", 12), fg="lightgray", bg="black")
        self.send_button.pack(padx=20, pady=5)

        self.gui_build = True
        self.window.mainloop()
        
        self.window.protocol("WM_DELETE_WINDOW", self.stop)

    def write(self):
        message = self.input_area.get('1.0', 'end')
        self.sock.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.window.destroy()
        self.sock.close()
        print("STOPPED")
        exit(0)

    def recive(self):
        while self.running:
            try:
                message = self.sock.recv(1024)
                if self.gui_build:
                    self.text_area.config(state='normal')
                    self.text_area.insert('end', message)
                    self.text_area.yview('end')
                    self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                break
            except:
                self.sock.close()
                break #TODO kill window
