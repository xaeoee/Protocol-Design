"""

Network server skeleton.

This shows how you can create a server that listens on a given network socket, dealing
with incoming messages as and when they arrive. To start the server simply call its
start() method passing the IP address on which to listen (most likely 127.0.0.1) and 
the TCP port number (greater than 1024). The Server class should be subclassed here, 
implementing some or all of the following five events. 

  onStart(self)
      This is called when the server starts - i.e. shortly after the start() method is
      executed. Any server-wide variables should be created here.
      
  onStop(self)
      This is called just before the server stops, allowing you to clean up any server-
      wide variables you may still have set.
      
  onConnect(self, socket)
      This is called when a client starts a new connection with the server, with that
      connection's socket being provided as a parameter. You may store connection-
      specific variables directly in this socket object. You can do this as follows:
          socket.myNewVariableName = myNewVariableValue      
      e.g. to remember the time a specific connection was made you can store it thus:
          socket.connectionTime = time.time()
      Such connection-specific variables are then available in the following two
      events.

  onMessage(self, socket, message)
      This is called when a client sends a new-line delimited message to the server.
      The message paramater DOES NOT include the new-line character.

  onDisconnect(self, socket)
      This is called when a client's connection is terminated. As with onConnect(),
      the connection's socket is provided as a parameter. This is called regardless of
      who closed the connection.

"""

import sys
from ex2utils import Server

# Create an echo server class
class MyServer(Server):
    def __init__(self):
        super(MyServer, self).__init__()
        # class attribute for counting total connected users.
        self.userCount = 0

        # class attribute for counting total users connected to the chatroom.
        self.userNoInChatRoom = 0

        # contains server connected user's socket object as a key.
        # key = socket object, value = socket.name which is Non initially if connected successfully.
        # when username registration, the value will be set to their username which is socket.name.
        self.connected_user = {}

        # key = username , value = socket object of that user.
        self.userNameKeyObjectValueDict = {}

        # colour attributes.
        self.green = "\033[1;32m"
        self.yellow = "\033[1;33m"
        self.burgundy = "\033[1;31;43m"
        self.violet = "\033[1;35m"
        self.cyan = "\033[1;36m"
        self.margenta = "\033[1;94m"
        self.base = "\033[0m"

    def onStart(self):
        print("Server has started")
        
    def onStop(self):
        print("Server has ended")		
        
    def onConnect(self, socket):
        # initially set the username as None to mark this user has never set the username before.
        socket.name = None
        # put the socket name to socket object key to keep track of connected user's sockets.
        self.connected_user[socket] = socket.name
        # increment user count by 1.
        self.userCount += 1
        # server side message displaying.
        print(f"{self.yellow}New user has been connected to the server, Current users in the server: {self.userCount}{self.base}")
        # client side message displaying.
        # display new user connection notice to all the current online clients.
        for client_socket in self.connected_user.keys():
            message = f"{self.yellow}New user has been connected to the server, Current users in the server: {self.userCount}{self.base}"
            client_socket.send(message.encode())
        notice = f"{self.yellow}/help to refer commands.{self.base}"
        socket.send(notice.encode())

    def onDisconnect(self, socket):
        # decrement user count by 1.
        self.userCount -= 1
        # server side message displaying.
        print(f"{self.yellow}User has been disconnected from the server, Current users: {self.userCount}{self.base}")
        # delete disconnected user's socket.
        del self.connected_user[socket]
        if socket.name is not None:
            del self.userNameKeyObjectValueDict[socket.name]
        # client side message displaying.
        # display new user disconnection notice to all the current online clients.
        for client_socket, username in self.connected_user.items():
            # if the user's username has not yet setted, inform them wihtout sepecific username.
            if username is None:
                message =f"{self.yellow}User has been disconnected from the chatroom and the server, Current users: {self.userCount}{self.base}"
                client_socket.send(message.encode())
            # if the user's in the chatroom with username
            else:
                # if the disconnected user's username has not set yet, inform it as "User".
                if socket.name == None:
                    socket.name = "User"
                message =f"{self.yellow}{socket.name} has been disconnected from the chatroom and the server, Current users: {self.userCount}{self.base}"
                client_socket.send(message.encode())
        socket.name = None
        
    def onMessage(self, socket, message):
        # This function takes two arguments: 'socket' and 'message'.
        #     'socket' can be used to send a message string back over the wire.
        #     'message' holds the incoming message string (minus the line-return).
    
        # convert the string to an upper case version
        # message = message.upper()

        # Just echo back what we received
        # message=message.encode()
        # socket.send(message)

        # if the message startswith /, command can be used.
        if message.startswith('/'):
            # if user only type '/', alert that user to use valid command and parameters.
            if len(message.strip()) == 1 and message[0] == '/':
                alert = f"{self.burgundy}Please type a valid command and parameters.\n" \
                f"Use /help to refer usage of command and parameters.{self.base}"
                socket.send(alert.encode())
            # remove '/' 
            message = message[1:]
            # split the message to seperate command and parameters.
            # type of the message variable is now list.
            message = message.strip().split()

            if len(message) > 0:
                command = message[0]
                parameters = ", ".join(message[1:])
                print(f"Command is :: {command}")
                print(f"Parameters are :: {parameters}")

                if command.strip().lower() == 'username':
                    username = parameters
                    # when the user tries to set their username as ' '.
                    if username != "" and ' ' not in username:
                        # if ther username has not yet taken and the user has not been regiesterd username before at all.
                        if username not in self.connected_user.values() and socket.name == None:
                                # increment the numser of user in the chatroom by 1.
                                self.userNoInChatRoom += 1
                                # set the username into socket.name.
                                socket.name = username
                                # set the socket's value from None to their username.
                                self.connected_user[socket] = username
                                # set the username as key and socket object as value.
                                self.userNameKeyObjectValueDict[username] = socket
                                # notice the user that the username has set.
                                alert = f"{self.yellow}Username has set to {username}{self.base}"
                                socket.send(alert.encode())
                                # notice all the chatroom connected user that the new user has connected to the chatroom.
                                for client_socket in self.userNameKeyObjectValueDict.values():
                                    message = f"{self.yellow}{socket.name} has been connected to the chatroom, Current user in the chat room: {self.userNoInChatRoom}{self.base}"
                                    client_socket.send(message.encode())
                        else:
                            # when the username is already set to the user.
                            if self.connected_user[socket] == username:
                                alert = f"{self.burgundy}Username already set to {username}{self.base}"
                                socket.send(alert.encode())
                            # if that username is taken by other user.
                            elif self.connected_user[socket] != username and username in self.connected_user.values():
                                alert = f"{self.burgundy}Username has already taken{self.base}"
                                socket.send(alert.encode())
                            # user with the username wants to change the username.
                            else:
                                del self.userNameKeyObjectValueDict[socket.name]
                                socket.name = username
                                self.connected_user[socket] = username
                                self.userNameKeyObjectValueDict[username] = socket
                                alert = f"{self.yellow}Username has changed to {username}{self.base}"
                                socket.send(alert.encode())
                    else:
                        alert = f"{self.burgundy}Spaces can not be included in username{self.base}"
                        socket.send(alert.encode())

                elif command.strip().lower() == 'pm':
                    receiverUsername = ""
                    # if the parameter is empty.
                    if socket.name is not None:
                        # check if the parameter is in right form
                        try:
                            receiverUsername, message = parameters.split(',', 1)
                        except ValueError:
                            alert = (f"{self.burgundy}Invalid usage: please use /pm <username> <message>.{self.base}")
                            socket.send(alert.encode())
                        if receiverUsername == "":
                            socket.send(f"{self.burgundy}Invalid usage: please use /pm <username> <message>.{self.base}".encode())
                        # check if the receiver's username is in the connected user list.
                        elif receiverUsername in self.userNameKeyObjectValueDict and receiverUsername != socket.name:
                            receiverSocket = self.userNameKeyObjectValueDict[receiverUsername]
                            message = ' '.join(message.split(", "))
                            privateMessageFrom = f"{self.cyan}Private message from {socket.name}: {message}{self.base}"
                            receiverSocket.send(privateMessageFrom.encode())
                            privateMessageTo = f"{self.margenta}Private message to {receiverUsername}: {message}{self.base}"
                            socket.send(privateMessageTo.encode())
                        # if the receiver's username is not in the connected userlist, alert it.
                        else:
                            alert = f"{self.burgundy}User name {receiverUsername} does not exsit{self.base}"
                            socket.send(alert.encode())
                    else:
                        socket.send(f"{self.burgundy}Set username before sending message.{self.base}".encode())

                # print out userlist.
                elif command.strip().lower() == 'userlist':
                    userList = []
                    for username in self.userNameKeyObjectValueDict.keys():
                        userList.append(username) 
                    userList = '\n'.join(userList)
                    userList = f"{self.yellow}{userList}{self.base}"
                    socket.send(userList.encode())

                # helper command
                elif command.strip().lower() == 'help':
                    help_message = f"{self.yellow}Available commands:\n" \
                    "/userlist: Get the list of currently connected users. Usage: /userlist\n" \
                    "/pm: Send a private message to a specific user. Usage: /pm <username>, <message_content>\n" \
                    "/help: Display this help message. Usage: /help\n" \
                    "/username: Set your username. Usage: /username <desired_username>\n" \
                    f"/close: Close the connection to the server. Useage: /close{self.base}"
                    socket.send(help_message.encode())

                elif command.strip().lower() == "close":
                    alert = f"{self.burgundy}closing connection with the server.{self.base}"
                    socket.send(alert.encode())
                    # close socket (automatically calls onDisconnect()
                    socket.close()
                    # Disconnect socket
                    return False

                else:
                    alert = f"{self.burgundy}Please type a valid command and parameters.\n" \
                    f"Use /help to refer usage of command and parameters.{self.base}"
                    socket.send(alert.encode())

        # if user just type a message, it then be a instant message to the whole connected users. 
        else:
            # if the message sender has not yet registered their username.
            if socket.name == None:
                alert = f"{self.burgundy}Set your username before sending a message{self.base}"
                socket.send(alert.encode())

            # when there is no user connected.
            elif len(self.userNameKeyObjectValueDict) <= 1:
                alert = f"{self.burgundy}There is no connected user to receive a message{self.base}"
                socket.send(alert.encode())

            # when a user type nothing, alert the user.
            elif message.strip() == '':
                alert = f"{self.burgundy}Type any message to send other than whitespace{self.base}"
                socket.send(alert.encode())

            # send a message to all the user in the chatroom, not to the user without username.
            else:
                for client_socket in self.userNameKeyObjectValueDict.values():
                    if client_socket == socket:
                        client_socket.send(f"{self.violet}Message to everyone: {message}{self.base}".encode())
                        continue
                    client_socket.send(f"{self.green}Message from {socket.name}: {message}{self.base}".encode())

        # Signify all is well
        return True
    

# Parse the IP address and port you wish to listen on.
ip = sys.argv[1]
port = int(sys.argv[2])

# Create an echo server.
server = MyServer()

# Start server
server.start(ip, port)

