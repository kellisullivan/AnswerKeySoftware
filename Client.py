
import sys
from tkinter import *
from socket import socket, SOCK_STREAM
from threading import Thread

#variables used for getting users choice
answers = []
choice = ''
#read in the list and return the quiz choice the user chose
def readList(sock):
    #get the list of possible quiz choices
    buf = sock.recv(50)
    list = buf.decode('ascii')
    list = list.split("\n")
    list.pop(len(list) - 1)
    #display the list of quiz choices for the user
    root = Tk()
    #create frame
    frame = Frame(root, height = 10, width = 10, bg = "dark gray")
    frame.pack()

    #make label to display quetion for user
    label = Label(frame, text="Which quiz would you like to take?\n", height = 3, font = "Helvetica 16 bold", bg = "dark gray")
    label.pack(side = TOP)

    #place the list of quizzes in the list box
    quizzes = Listbox(frame, height = len(list), font = "Helvetica 20", fg = "white", bg = "dark gray")
    #insert each quiz choice into the text box
    for x in range(len(list)):
        quizzes.insert(x + 1, list[x])
    quizzes.pack(side = LEFT)

    #command to get the selection from the user and then destroy the tk window
    def getDestroy():
        global choice
        choice = quizzes.curselection()
        root.destroy()

    #place a button on the window to get the choice of quiz from the user
    B = Button(frame, text = "Enter", command = getDestroy, font = "Helvetica 20 bold",  activebackground = "green", bg = "grey", fg = "white")
    B.pack(side = RIGHT)

    #make sure to return the global choice that we stored
    global choice
    root.mainloop()
    #return the list choice
    return list[choice[0]]

#read intro message from user
def readMessage(sock):
    try:
        #create a buffer that recieves the first 4 bytes of a incoming message
        buf = sock.recv(5)
        #decode the messaging into ascii format
        type = buf.decode('ascii')
        #helpful print statement
        return type
    #if we can't read anything than return nothing
    except:
        return None

#method that gets quiz from answer key software and
#lets the user take the exam
def takeQuiz(sock):
    #check length of quiz for for loop
    len = sock.recv(1)
    length = int(len.decode('ascii'))
    #get the questions from the answer key software
    quest = sock.recv(1000)
    questions = quest.decode('ascii')
    #split questions by end of line characters
    list = questions.split("\n")
    #method to display GUIs to answer questions
    def answerQuestions(question):
        #string of answers to be sent back to server
        answer = ''
        global answers
        #create window
        root = Tk()
        #create frame on the window
        frame = Frame(root, height = 10, width = 10, bg = "dark gray")
        frame.pack()

        #display the question
        T = Label(frame, height = 4, text = question, font = "Helvetica 20 bold", bg = "dark gray" )
        T.pack(side = TOP)

        #display text box so that the user can answer the question
        E = Entry(frame, textvariable = answer, font = "Helvetica 20 bold" )
        E.pack(side = LEFT)

        #method to get the input from the user
        def pushButton():
            #add answer to the list
            global answers
            answers = answers + [E.get()]
            root.destroy()

        #add a button for user to indicate they are done and you can get their response
        B = Button(frame, text = "Enter", command = pushButton, font = "Helvetica 20 bold",  activebackground = "green", bg = "grey", fg = "white")
        B.pack(side = RIGHT)

        #return the answers so it can be sent via the socket
        global answers
        root.mainloop()
        return answers
    #loop through questions and store the users answer in the answer list
    for num in range(length):
        decoy = answerQuestions(list[num])
    #return the list of the users answers
    return answers

#send the users quiz choice
def sendQuiz(sock):
    #do this by calling readlist
    quizchoice = readList(sock)
    #send the quizchoice that was returned from readList
    sock.send(quizchoice.encode('ascii'))
    return None

#this method is actually going to take care of sending the answers
def sendAnswers(answers, sock):
    buf = bytearray()
    #loop through answer list and but the into byte array
    for x in range(len(answers)):
        add = answers[x] + "\n"
        buf.extend(add.encode('ascii'))
    #send the byte array through the socket
    sock.send(buf)
    return None

#method that is going to run through the answer key software
class Reader :
    #constructor
    def __init__(self, sock , x):
        self.sock = sock
        self.x = x
        msg = ('BEGIN'.encode('ascii'))


    #run method does the serialization experience for the client
    def run(self):
        self.sock.settimeout(30)
        try :
            #get that the server is ready to start
            buf = self.sock.recv(5)
            type = buf.decode('ascii')
            if type == 'START':
                #server is ready to start now see if the user wants to continue
                #create a GUI to ask if the user is ready to go
                #create window
                root = Tk()
                frame = Frame(root, height = 10, width = 10)
                frame.pack()
                #method to send message of BEGIN to the server
                #also learns to close window
                def sendSock():
                    self.sock.send(msg)
                    root.destroy()
                #method to send quit to server so it will turn off
                #also learns to close window
                def closeSock():
                    #change x so the program knows to end
                    self.x = 1
                    root.destroy()
                    exit(0)
                #create label to ask if user wants to take quiz
                label = Label(frame, text="Would you like to take a quiz?\n", height = 3, font = "Helvetica 20 bold")
                label.pack(side = TOP)
                #define BEGIN message in case user wants to take a quiz
                msg = ('BEGIN'.encode('ascii'))
                #create YES button if user wants to take a quiz
                yes = Button(frame, text = "Yes", command = sendSock, font = "Helvetica 20 bold", activebackground = "green", bg = "grey", fg = "white")
                yes.pack(side = LEFT)
                #create NO button if user wants to take a quiz
                no = Button(frame, text = "No", command = closeSock, font = "Helvetica 20 bold", activebackground = "red", bg = "grey", fg = "white")
                no.pack(side = RIGHT)
                root.mainloop()

                #loop to make sure we are getting the correct quiz choice
                while True :
                    #go to message that will figure oout quiz choice and send it to server
                    sendQuiz(self.sock)
                    #the next message will tell us if this thing is good or bad
                    buf1 = self.sock.recv(4)
                    buf1 = buf1.decode('ascii')
                    #if bad inform user nad send back through the loop
                    if buf1 == "BADD":
                        print("This quiz was invalid. Please try again.")
                    #if the quiz is valid than break the loop
                    else :
                        break
                #read to take the quiz, call method to get responses
                responses = takeQuiz(self.sock)
                #call the global answers
                global answers
                #reset the global answers
                answers = []
                #call method to send answers back to server
                sendAnswers(responses, self.sock)
                #check to make sure there are answers to dispaly to user
                check = self.sock.recv(5)
                check = check.decode('ascii')
                #if check says YIKES there are no answers to display
                if check == 'YIKES':
                    #create window
                    root = Tk()
                    frame = Frame(root, height = 10, width = 10, bg = "dark grey")
                    frame.pack()
                    #method to close window when button is pushed
                    def close():
                        root.destroy()

                    #label to display information to user
                    L = Label(root, text = "Sorry we don't have any other answers for this quiz.", font = "Helvetica 20 bold")
                    L.pack(side = TOP)

                    #button to let user close window after reading info
                    B = Button(root, text = "Okay", command = close, font = "Helvetica 20 bold", activebackground = "green", fg = "white", bg = "dark gray")
                    B.pack(side = BOTTOM)
                    root.mainloop()
                #didnt recieve YIKES message so there is info to be displayed
                else :
                    #get number of answer keys stored for this quiz
                    value1 = self.sock.recv(1)
                    value1.decode('ascii')
                    #get number of questions in quiz
                    value2 = self.sock.recv(1)
                    value2.decode('ascii')
                    #get integer representations of those values
                    value1 = int(value1)
                    value2 = int(value2)

                    #get answer key info
                    answerkey = self.sock.recv(100)
                    answerkey = answerkey.decode('ascii')
                    answerkey = answerkey.split("\n")

                    #create window to display answers
                    root = Tk()
                    frame = Frame(root, height = 15, width = 15, bg = "dark grey")
                    frame.pack()

                    #add label that dispalys the responses the user gave
                    my = Label(root, text = "Your responses:", font = "Helvetica 12 bold", )
                    my.pack()
                    my1 = Label(root, text = responses , font = "Helvetica 12")
                    my1.pack()

                    #label that displays the past responses for this quiz
                    my2 = Label(root, text = "Other responses:", font = "Helvetica 12 bold")
                    my2.pack()

                    #method to destroy window when done reading info
                    def close():
                        root.destroy()

                    #helps sort through message
                    m = 0

                    #method sorts through answer string with many answers and displays them properly
                    for x in range(value1):
                        thing = ''
                        for y in range(value2):
                            thing = thing + str(answerkey[m]) + ", "
                            m = m + 1
                        L = Label(root, text = str(thing), font = "Helvetica 12")
                        L.pack()

                    #button to allow user to close out of window when done
                    B = Button(root, text = "Okay", command = close, font = "Helvetica 12 bold", activebackground = "green", fg = "white", bg = "dark gray")
                    B.pack(side = BOTTOM)
                    root.mainloop()
        except:
            pass

        return None

    #crucial for closing loop at end of the main method
    def getX(self):
        return self.x

    #method to break socket loop and closes socket
    def close():
        x = 1
        self.sock.close()

#main method
def main() :
    #create the socket
    clientsocket = socket(type=SOCK_STREAM)
    #create address info
    addr = ("127.0.0.1", 8080)
    clientsocket.connect(addr)
    #instantize x
    x = 0
    #create reader
    read = Reader(clientsocket, x)
    #create loop to take infinite number of quizzes, x will be updated via
    #the read method
    while x == 0:
        read.run()
        x = read.getX()
    print("GOODBYE!")

#starts this whole thing
if __name__=='__main__':
    main()
