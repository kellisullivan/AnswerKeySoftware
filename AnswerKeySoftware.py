import sys
from socket import socket, SOCK_STREAM
from threading import Thread

#answer key class is going to contain answers and the quiz they go along with
class AnswerKey:
    #constructor
    def __init__(self, quiz, answers):
        self.quiz = quiz
        self.answers = answers

    #return answer keys for the quiz
    def getAnswerKey(self) :
        return self.answers

    #add answer to answer key list
    def add(self, answer):
        self.answers = self.answers + [answer]

#master list of quizes
class QuizList:
    #the master lsit will contain the lsit of quizes and will store the length
    #of the quiz
    def __init__(self, list, length):
        self.list = list
        self.length = length

    #this is the method that will send list to user
    def sendList(self, sock):
        #get byte array to send list in
        sendlist = bytearray()
        for x in range(self.length) :
            id = self.list[x].getID()
            id = id + "\n"
            sendlist.extend(id.encode('ascii'))
        sock.send(sendlist)
        return None

    #add a new quiz
    def add(self, quiz):
        self.list = self.list + [quiz]
        self.length += 1

    #get the length of quiz list
    def getlength(self) :
        return self.length

    #return the list of quize
    def getList(self) :
        return self.list

#class to represent an individual quiz
class Quiz :
    #constructor
    def __init__(self, id, length, questions, answerkeys):
        self.id = id
        self.len = length
        self.questions = questions
        self.answerkeys = answerkeys

    #method that returns name ID to determine identification
    def getID(self):
        name = "Quiz " + str(self.id)
        return name

    #return the number of questions in this quiz
    def getLength(self) :
        return self.len

    #return the list of questions
    def getQuestions(self):
        return self.questions

    #add a question to the quiz  and update length
    def addQuestion(self, question):
        self.questions = self.questions + [question]
        self.len = self.len + 1

    #add an answer key for the quiz
    def setAnswer(self, answer):
        self.answerkeys = answer

    def getAnswers(self):
        return self.answerkeys

#called to send a quiz over to a client
def sendQuiz(quiz, sock):
    length = quiz.getLength()
    sock.send(str(length).encode('ascii'))
    questions = quiz.getQuestions()
    #get byte array to send quiz in
    sendquiz = bytearray()
    for x in range(length) :
        question = questions[x]
        question = question + "\n"
        sendquiz.extend(question.encode('ascii'))
    sock.send(sendquiz)

#method is going to take in a socket and read from that socket
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

#this method will read in the answers from the user
def readAnswers(quiz, sock):
    #get info from socket and deocde
    answer = sock.recv(100)
    answer = answer.decode('ascii')
    #split it by the end of line character
    answers = answer.split("\n")
    #remove excess
    answers.pop(len(answers)-1)
    #send back edited answers
    return answers

#find the quiz choice
def getQuizChoice(sock):
    #get quizchoice from the socket
    quiz = sock.recv(10)
    quiz = quiz.decode('ascii')
    #return quizchoice
    return quiz

#method to send the set of answer keys back to the client
def sendAnswers(sock, answer):
    #if there are no prior answers return specified message to the user
    if len(answer) < 1 :
        sock.send('YIKES'.encode('ascii'))
        return
    #if there are prior quizzes then get them
    else :
        #send that we have messages so the client can handle them
        sock.send('YAYYY'.encode('ascii'))
        #send the number of answerkeys we have
        sock.send(str(len(answer)).encode('ascii'))
        #send the number of answers per answer key
        sock.send(str(len(answer[0])).encode('ascii'))
        #create thing for message to be entered into
        message = ''
        #add all the answers to a message seperated by the new lie character
        for value in answer:
            for x in range(len(value)) :
                message = message + value[x] + "\n"
        #send it via the socket
        sock.send(message.encode('ascii'))
        return

#method that is doing the bulk of the work for this program
def doWork(sock, quizlist, x):
        #create intial message to establish that a conection has method
        welcome = bytearray()
        welcome.extend('START'.encode('ascii'))
        sock.send(welcome)
        #get the users response
        msg = readMessage(sock)
        #if we get BEGIN the client is ready
        if msg == "BEGIN" :
            #loop through running a quiz
            while True :
                #send the lsit of quizzes in the server to the user
                quizlist.sendList(sock)
                #call method to get the quiz choice
                quiz = getQuizChoice(sock)
                #get list to compare users answer to quiz choices
                list = quizlist.getList()
                quizchoice = None
                #try to see if the quiz is in the quiz list
                for x in range(quizlist.getlength()):
                    #if quiz matches then set that as quiz choice
                    if quiz == list[x].getID() :
                        quizchoice = list[x]
                    else :
                        pass
                #check that an adequate quiz was chosen
                if quizchoice == None :
                    sock.send('BADD'.encode('ascii'))
                #then we send the user the quiz
                else :
                    break
            sock.send('GOOD'.encode('ascii'))
            #go through method of sending the quiz
            sendQuiz(quizchoice, sock)
            #get list of quizzes
            quizzes = quizlist.getList()

            #empty answers list
            answers = []
            thequiz = None
            #go throuogh lsit of quizzes to get the quiz instance rather than string
            for quiz in quizzes :
                if quizchoice == quiz:
                    thequiz = quiz
            #set answer key for the quiz we wants answers
            answerkey = thequiz.getAnswers()
            #get the answers through the sock
            answers = readAnswers(quizchoice, sock)

            #send the answers
            sendAnswers(sock, answerkey.getAnswerKey())
            #add the quiz to the answer key now
            answerkey.add(answers)
            #keep the elf.x value at x
            x = 0
            return x
        #if message says quit then change x to 1 so you can exit this sock
        elif msg == "QUITT" :
            x = 1
            sock.close()
            return x
        else :
            pass

#class that creates the many connections
class Connection(Thread):
    #constructor
    def __init__(self, sock, address, quizlist, x):
        super().__init__()
        self.sock = sock
        self.addr = address[0]
        self.port = address[1]
        self.quizlist = quizlist
        self.x = x

    #method that will run for multiple threads
    def run(self):
        while self.x == 0:
            #call method to do most of the work
            self.x = doWork(self.sock, self.quizlist, self.x)
        return None

#method creates the quizzes by grabbing text from files
#generating new quiz classes
def createQuizzes():
    #create quiz1 and the answer key for the quiz
    quiz1 = Quiz(1, 0, [], None)
    AnswerKey1 = AnswerKey(quiz1, [])
    #set answer to the particular quiz
    quiz1.setAnswer(AnswerKey1)

    #create quiz2 and the answer key for the quiz
    quiz2 = Quiz(2, 0, [], None)
    AnswerKey2 = AnswerKey(quiz2, [])
    #set answer to the particular quiz
    quiz2.setAnswer(AnswerKey2)

    #create quiz3 and the answer key for the quiz
    quiz3 = Quiz(3, 0, [], None)
    AnswerKey3 = AnswerKey(quiz3, [])
    #set answer to the particular quiz
    quiz3.setAnswer(AnswerKey3)

    #create the quiz list so we can have the whole list of quizzes
    quizlist = QuizList([],0)

    #open file and add quiz to quizlist and questions to the quiz class
    file1 = open("Quiz1.txt")
    quizlist.add(quiz1)
    for line in file1:
        question = line.split("\n")
        quiz1.addQuestion(question[0])

    #open file and add quiz to quizlist and questions to the quiz class
    quizlist.add(quiz2)
    file2 = open("Quiz2.txt")
    for line in file2:
        question = line.split("\n")
        quiz2.addQuestion(question[0])

    #open file and add quiz to quizlist and questions to the quiz class
    quizlist.add(quiz3)
    file3 = open("Quiz3.txt")
    for line in file3:
        question = line.split("\n")
        quiz3.addQuestion(question[0])
    return quizlist


#main method
def main():
    quizlist = createQuizzes()
    #created a server socket
    srv = socket(type=SOCK_STREAM)
    #set IP address and port
    addr = ("127.0.0.1", 8080)
    #have the server sockt bind to the address, needs list of ip and port
    srv.bind(addr)
    #listen (??) on the socket
    srv.listen(5)
    #while we are listening now we are going  to try to connect
    while True:
        # Accept the next connection
        (conn, caddr) = srv.accept()
        #store this connection as a new connection
        c = Connection(conn, caddr, quizlist, 0)
        c.start()

#start by calling main method
if __name__ == "__main__":
    main()
