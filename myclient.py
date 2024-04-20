"""
IRC Client Example

This script is an IRC (Internet Relay Chat) client exemplar that connects to a server and sends messages to it. It includes error handling for connection issues, unexpected exceptions, and keyboard interrupts.

To run this script, follow these steps:
1. Ensure you have Python installed on your system (Python 3.x is recommended).
2. Save this script as "myclient.py" in a directory of your choice.
3. Ensure you have the "ex2utils.py" file in the same directory as "myclient.py". This file contains utility functions used by the client.
4. Open a terminal or command prompt.
5. Navigate to the directory containing "myclient.py" and "ex2utils.py".
6. Run the following command to start the client:
   python3 myclient.py <server_ip> <server_port>
   Replace <server_ip> with the IP address of the server you want to connect to, and <server_port> with the port number the server is listening on.
7. Once the client is connected to the server, you can start sending messages. Type your message and press Enter to send it to the server.
8. To gracefully disconnect from the server and exit the client, use /close command.

For testing purposes, you can follow this protocol to demonstrate the functionality provided within the IRC protocol:
1. Connect to the server by running the script with the server's IP address and port.
2. Send messages to the server by typing them in the terminal and pressing Enter.
3. Ensure that messages sent by other clients connected to the server are received and displayed by your client.
4. Test error handling by intentionally disconnecting the server or causing network issues.
5. Test keyboard interrupts by pressing Ctrl+C to disconnect from the server.
6. Verify that the client exits gracefully without errors.
7. Repeat the steps above to test various scenarios and ensure robustness of the client.

Note: This script assumes that the server is already running and accessible at the specified IP address and port.
"""

import sys
from ex2utils import Client

import time

class IRCClient(Client):
    def __init__(self):
        super(IRCClient, self).__init__()
        self.burgundy = "\033[1;31;43m"
        self.base = "\033[0m"

    def onMessage(self, socket, message):
        # print the message
        print(message)
        # *** process incoming messages here ***
        return True

# Parse the IP address and port you wish to connect to.
try:
    ip = sys.argv[1]
    port = int(sys.argv[2])
# when the user's input arguments are not in the right formant.
except IndexError:
    print("\033[1;31;43m" + "List index out of range. Proper usage: python3 myclient.py localhost 8090" + "\033[0m")
    sys.exit(1)

# Create an IRC client.
client = IRCClient()

# Start server
try:
    client.start(ip, port)
# when the server has not yet running.
except ConnectionRefusedError:
    print(f"{client.burgundy}Server has not yet established, failed to connect.{client.base}")
    sys.exit(1)
# when ther is unexpected errors.
except:
    print(f"{client.burgundy}Unexpected error has occured. failed to connect.{client.base}")
    sys.exit(1)

    
while client.isRunning():
    # take input, strip input, send to server as message
    try:
        message = input().strip()
        client.send(message.encode())
    # when server has closed with keyboard interrupt or any unexpected issues.
    except OSError:
        print(f"{client.burgundy}Server has closed, disconnecting from the server.{client.base}")
        client.stop()
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"{client.burgundy}\nKeyboard interrupted, disconnecting from the server.{client.base}")
        client.stop()
        sys.exit(1)
    except:
        print(f"{client.burgundy}Unexpected error has occured. disconnecting from the server{client.base}")
        client.stop()
        sys.exit(1)

#stops client
client.stop()
