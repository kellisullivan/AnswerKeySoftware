README - instructs how to start this system

AnswerKeySoftware.py - start this first it runs the answer key software and is waiting for connections to begin
Client.py - can start a multitude of these next all at the same time and will execute the quiz taking
Quiz1.txt - file that contains a quiz
Quiz2.txt - file that contains a quiz
Quiz3.txt - file that contains a quiz

For this problem, I really just had the idea of wanting to generate an answer key software that would basically go through
how a class could take quizzes individual and see what others responded to get feedback. The ability for this program to be accessible
for many different people would be to use sockets. I taught myself these in python code and found them realitvely easy to work with.
However, there was ton of incoding and decoding in this process. The next challenge was to understand how the user was going to
experience the software. It was decided that serialization of this process was problem the best way to go about this. I built a sort
of conversation that I wanted the client to have with the server to go about taking a quiz and getting any prior responses someone 
had given for a quiz. The largest challenge was encoding these messages prior to sending via the socket. This way when a message was 
recieved the program was able to decode it and in the case of the client, place in a GUI(wow that was hard). I did this by adding end of line 
characters after each object I wanted to be snipped afterward. This also proved to be extremely beneficial since I was able to print out 
messges when they arrived through the socket. The most difficult thing about this assignment for me was finding where I went wrong. Many times 
there would be no errors and the program wouldn't work correctly and I had no path to lead me to the error. I had to employ a lot of print
statments. This was a hassle but proved to be very beneficial when dealing with sockets. I found the socket documentation not very extensive
which made it hard to teach myseslf those. However, I used examples from the Distributed Systems block and that helped enoromously. 

All in all I have a lot I wish I could have done with the project and maybe with another person or more time this would have been possible. 
I did look into the sql and understood it far better than I had going into it. However, it didn't seem to make the most sense for my answer key. I 
was hoping to incorporate it as a way to create users for the software. I didn't get around to it for this assignment but think it 
would definitely be a doable addition. Finally, I think it would be crucial to create a way for the user to simple exam the answers instead 
of just taking a quiz.
