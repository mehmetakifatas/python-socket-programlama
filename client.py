import tkinter as tk
import threading
from tkinter import messagebox
from socket import *

from tkinter import filedialog
ip='10.93.11.15'
s = socket(AF_INET, SOCK_STREAM)
s.connect((ip, 12345))


def parse(x):
    if (x.count(';') >= 4):
        tmp = x.split(';')
        if (tmp[0] == 'msg'):
            return (('msg', tmp[1], tmp[2], tmp[3]), ';'.join(tmp[4:], ))
        elif tmp[0] == 'usr':
            return (('usr', tmp[3].split(',')), ';'.join(tmp[4:], ))
        elif tmp[0] == 'logok':
            return ('logok', ';'.join(tmp[4:], ))
        elif tmp[0] == 'logfail':
            return ('logfail', ';'.join(tmp[4:], ))
    else:
        return (None, x)



class Client(tk.Frame):
    def __init__(self, nickname, buff, master=None):
        tk.Frame.__init__(self, master)
        self.config(background='gray')




        self.master.minsize(600, 400)
        self.grid(sticky=tk.N + tk.S + tk.E + tk.W)
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.createWidgets()
        self.selectedUser = None
        self.nickname = nickname
        self.master.title('Chat: ' + str(nickname))
        self.ucho = Hear(self, buff);
        self.ucho.start()

    def showMessage(self, frm, to, message, sep=' => '):
        self.chatBox.insert(tk.END, frm + sep + to + ':\n' + message + '\n')
        self.chatBox.see(tk.END)

    def updateUsers(self, k):
        self.userList.delete(0, tk.END)
        k.insert(0, 'Tüm_Kullanıcılar')
        for x in range(len(k)):
            self.userList.insert(x, k[x])
        self.userList.activate(0)

    def createWidgets(self):

        self.chatFrame = tk.Frame(self)
        self.chatFrame.grid(row=0, column=0, rowspan=10, sticky=tk.S + tk.N + tk.E + tk.W)

        self.chatBox = tk.Text(self.chatFrame, height=10,fg="cyan",bg="#000000",width=10,font=(None,20,"bold"))
        self.chatBox.grid(row=0, column=0, sticky=tk.S + tk.N + tk.E + tk.W)
        self.chatBox.bind("<Key>", lambda e: "break")
        self.sscr = tk.Scrollbar(self.chatFrame)
        self.sscr.grid(column=1, row=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.chatBox.config(yscrollcommand=self.sscr.set)
        self.sscr.config(command=self.chatBox.yview)
        self.chatFrame.columnconfigure(0, weight=1)
        self.chatFrame.rowconfigure(0, weight=1)

        self.usersFrame = tk.Frame(self)
        self.usersFrame.grid(column=1, row=0, rowspan=15, padx=5, sticky=tk.N + tk.S + tk.W + tk.E)
        scr = tk.Scrollbar(self.usersFrame)
        scr.grid(column=1, row=1, sticky=tk.N + tk.S + tk.W + tk.E)

        userLabel = tk.Label(self.usersFrame, text='Kullanıcılar:',fg="black",bg="gray",width=10,font=(None,20,"bold")).grid(column=0, row=0, sticky=tk.N + tk.S + tk.E + tk.W)

        self.userList = tk.Listbox(self.usersFrame,fg="red",bg="#000000",width=10,font=(None,20,"bold underline"))
        self.userList.insert(0, 'Tüm_Kullanıcılar')
        self.userList.activate(0)

        self.userList.grid(column=0, row=1, sticky=tk.N + tk.S + tk.E + tk.W)
        self.userList.config(yscrollcommand=scr.set)
        scr.config(command=self.userList.yview)

        self.usersFrame.columnconfigure(0, weight=1)
        self.usersFrame.rowconfigure(0, weight=1)
        self.usersFrame.rowconfigure(1, weight=15)

        self.messageBox = tk.Text(self, height=3,fg="#191970",bg="#e0ffff",width=10,font=(None,20,"bold"))
        self.messageBox.grid(row=10, column=0, rowspan=5, sticky=tk.S + tk.N + tk.E + tk.W)

        self.sendButton = tk.Button(self, text='Mesajı Gönder',fg="black",bg="#00ced1",width=10,font=(None,20,"bold"))
        self.sendButton.myName = "Send Button"
        self.sendButton.grid(row=15, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
        self.sendButton.bind("<Button-1>", self.send)

        self.exitButton = tk.Button(self, text='Çıkış',fg="black",bg="#00ced1",width=10,font=(None,20,"bold"))
        self.exitButton.myName = "Exit Button"
        self.exitButton.grid(row=15, column=1, sticky=tk.N + tk.S + tk.E + tk.W)
        self.exitButton.bind("<Button-1>", self.exit)

        self.master.bind_all("<Return>", self.send)

        for i in range(16):
            self.rowconfigure(i, weight=1)
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)

    def handler(self, event):
        pass

    def send(self, event):
        to = self.userList.get(tk.ACTIVE)
        msg = self.messageBox.get('1.0', tk.END).strip()
        if len(msg) == 0:
            self.messageBox.delete('0.0', tk.END)
            self.messageBox.insert(tk.INSERT, "Mesaj boş gönderilemez.")
        else:
            if self.ucho.status == True:
                msg = 'msg;' + self.nickname + ";" + to + ";" + msg + ';'
                s.send(bytes(msg, 'UTF-8'))
            self.messageBox.delete('1.0', tk.END)

    def exit(self, event):
        if self.ucho.status == True:
            msg = 'logout;;;' + self.nickname + ';'
            s.send(bytes(msg, 'UTF-8'))
            s.close()
        self.ucho.status = False
        self.master.destroy()

    def on_closing(self):
        if tk.messagebox.askokcancel("ÇIKIŞ", "Çıkmak İstiyormusunuz?"):
            self.exit(None)


class Hear(threading.Thread):
    def __init__(self, root, buff):
        self.buff = buff
        self.root = root
        self.status = True
        super().__init__(daemon=True)

    def run(self):
        try:
            while self.status:
                while self.buff.count(';') >= 4:
                    tmp = parse(self.buff)
                    self.buff = tmp[1]
                    if (tmp[0] is not None):
                        tmp = tmp[0]
                        if (tmp[0] == 'msg'):
                            self.root.showMessage(tmp[1], tmp[2], tmp[3])
                        else:
                            self.root.updateUsers(tmp[1])
                try:
                    echodane = ''
                    echodane = s.recv(1024)
                    if not echodane:
                        self.root.showMessage('', '', 'baglantı kurulamadı.', '')
                        self.status = False
                        s.close()
                        break
                except:
                    self.root.showMessage('', '', 'baglantı kurulamadı', '')
                    self.status = False
                    s.close()
                    return
                echodane = echodane.decode('UTF-8')
                self.buff += echodane

        finally:
            s.close()







from tkinter import *

# Arayüz için gerekli Tkinter komutlarımız
pencere = Tk()
pencere.title("Chat: Leşh")
pencere.geometry("1000x600+425+200")
pencere.state("normal")
# pencerenin görünürlgü yüzde doksan oranına düşürülmüştür
pencere.wm_attributes("-alpha", 0.9)


def giriş():
    buff = ''
    nickname = None
    nickname="░▒▓█" + metinl.get()
    if (nickname != 'Tüm_Kullanıcılar' and nickname != ''):
        msg = 'login;;;' + nickname + ';'
        s.send(bytes(msg, 'UTF-8'))
        while True:
            data = s.recv(1024).decode('UTF-8')
            tmp = parse(buff + data)
            buff = tmp[1]
            if (tmp[0] == 'logok'):
                break;
            elif tmp[0] == 'logfail':
                print("Bu kullanıcı adı mevcut.")
                nickname = None
                break;

    else:
        print("Bu kullanıcı adı mevcut.")

    label.destroy()
    clientApp = Client(nickname=nickname, buff=buff)
    clientApp.mainloop()


def dosyag():
    pencere.filename = filedialog.askopenfilename(initialdir="/", title="Dosya Seç",filetypes=(("jpeg files", "*.jpg"),("mp3 file", "*.mp3"), ("Tüm Dosyalar", "*.*")))
    print(pencere.filename)
    import socket
    import sys
    HOST = "ip"
    PORT = 9999
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    f_send = pencere.filename
    with open(f_send, "rb") as f:
        data = f.read()
        s.sendall(data)
        s.close()


def dosyal():
    import socket
    TCP_IP = ip
    TCP_PORT = 9001
    BUFFER_SIZE = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    with open('D:\\alınan.mp3', 'wb') as f:
        while True:
            # print('receiving data...')
            data = s.recv(BUFFER_SIZE)
            print('data=%s', (data))
            if not data:
                f.close()
                break
            f.write(data)
    f.close()
    s.close()

photo = PhotoImage(file = "gif.gif")
label =Label(image=photo)
label.pack()


kullanici = tk.PhotoImage(file="kul1.png")
kullanıcıgirisi = Label(text="Kullanıcı Adı=",image=kullanici)
kullanıcıgirisi.config(font=('times', 24, 'italic bold underline'))
kullanıcıgirisi.pack()


kullanıcıgirisi.place(relx=0.15, rely=0.40, relheight=0.10, relwidth=0.24)
metinl = Entry(bg= "cyan", font=('times', 24, 'italic bold underline') , fg="Forest Green")


metinl.place(relx=0.40, rely=0.40, relheight=0.10, relwidth=0.24 )

tus = tk.PhotoImage(file="oda.png")
gir = Button(text="Odaya Giriş", command=giriş, image=tus)
gir.place(relx=0.4, rely=0.51, relheight=0.15, relwidth=0.24)

gonder = tk.PhotoImage(file="gonder.png")
dosya = Button(text="Dosya Gönder", command=dosyag, image=gonder)
dosya.place(relx=0.4, rely=0.67, relheight=0.15, relwidth=0.24)

al = tk.PhotoImage(file="al.png")
dosyaal = Button(text="Dosya Al", command=dosyal, image=al)
dosyaal.place(relx=0.4, rely=0.83, relheight=0.15, relwidth=0.24)


pencere.mainloop()