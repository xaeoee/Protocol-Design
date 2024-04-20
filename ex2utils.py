"""

ex2utils.py- 
"""


import threading
import time
import socket as socketlib


class Socket():
	"""
	Mutable wrapper class for sockets.
	"""

	def __init__(self, socket):
		# Store internal socket pointer
		self._socket = socket
	
	def send(self, msg):
		# Ensure a single new-line after the message
		self._socket.send(msg.strip()+b"\n")
		
	def close(self):
		self._socket.close()
		

class Receiver():
	"""
	A class for receiving newline delimited text commands on a socket.
	"""

	def __init__(self):
		# Protect access
		self._lock = threading.RLock()
		self._running = True

	# 인스턴스가 호출될때 호출되는 함수
	def __call__(self, socket):
		"""Called for a connection."""
		# Set timeout on socket operations
		socket.settimeout(1)


		# Wrap socket for events
		wrappedSocket = Socket(socket)
		
		# Store the unprocessed data
		stored = ''
		chunk = ''
		
		# On connect!
		self._lock.acquire()
		self.onConnect(wrappedSocket)
		self._lock.release()
		
		# Loop so long as the receiver is still running
		while self.isRunning():
			# Take everything up to the first newline of the stored data
			(message, sep, rest) = stored.partition('\n')
			if sep == '': # If no newline is found, store more data...
				while self.isRunning():
					try:
						chunk = ''
						chunk = socket.recv(1024).decode() 
						stored += chunk
						break
					except socketlib.timeout:
						pass
					except:
						print('EXCEPTION')
				
				# Empty chunk means disconnect
				if chunk == '':
					break;

				continue
			else: # ...otherwise store the rest
				
				stored = rest			
			# Process the command
			self._lock.acquire()
			success = self.onMessage(wrappedSocket, message)
			self._lock.release()
			
			if not success:
				break;

		# On disconnect!
		self._lock.acquire()
		self.onDisconnect(wrappedSocket)		
		self._lock.release()
		socket.close()
		del socket
		
		# On join!
		self.onJoin()
			
	def stop(self):
		"""Stop this receiver."""
		self._lock.acquire()
		self._running = False
		self._lock.release()
		
	def isRunning(self):
		"""Is this receiver still running?"""
		self._lock.acquire()
		running = self._running
		self._lock.release()
		return running
		
	def onConnect(self, socket):
		pass

	def onMessage(self, socket, message):
		pass

	def onDisconnect(self, socket):
		pass

	def onJoin(self):
		pass

		
		
class Server(Receiver):

	def start(self, ip, port):
		# Set up server socket

		# 소캣을 객체를 생성, 이 때, 인자로 두 가지를 입력해야 하는데, 첫번째는 어드레스 패밀리(AF: Address Family)고, 두번째는 소켓 타입.
		serversocket = socketlib.socket(socketlib.AF_INET, socketlib.SOCK_STREAM)

		# 이 코드는 소켓 옵션을 설정하는 부분이다, setsockopt 메서드를 사용하여 소켓의 옵션을 설정할 수 있다.
		# SO_REUSEADDR: 이 옵션을 설정하면 소켓이 사용 중인 포트를 다른 소켓이 즉시 재사용할 수 있다, 일반적으로 소켓을 닫은 후 해당 포트를 다시 열 때 사용됨.
		# 소켓 연결이 끊어진 후 다시 동일한 포트를 사용하여 새로운 연결을 수락하는 데 유용함.
		# 예를 들어, 서버가 종료되고 포트가 여전히 사용 중인 상태에서 서버를 재시작하려고 할 때, 이 옵션을 설정하면 즉시 해당 포트를 재사용하여 새로운 서버 소켓을 열 수 있다.
		# 이렇게 하면 다른 프로세스가 해당 포트를 기다리는 동안에 시간을 절약할 수 있음.
		serversocket.setsockopt(socketlib.SOL_SOCKET, socketlib.SO_REUSEADDR, 1)

		# 생성된 소켓의 번호와 실제 어드레스 패밀리를 연결해주는 것.
		# 소켓과 AF를 연결하는 과정이라 하였으므로, 이 인자는 어드레스 패밀리가 된다. 앞부분은 ip, 뒷부분은 포트로 (ip, port) 형식으로 한 쌍으로 구성된 튜플이 곧 어드레스 패밀리.
		serversocket.bind((ip, int(port)))

		# bind가 끝나고 나면 listen하는 단계가 필요합니다. 이는 상대방의 접속을 기다리는 단계로 넘어가겠단 의미.
		# isten()안에 인자로 숫자 10이 입력되어 있는데, 이는 해당 소켓이 총 몇개의 동시접속까지를 허용할 것이냐는 이야기다.
		serversocket.listen(10)

		serversocket.settimeout(1)
		# On start!
		# server.py 파일에서 overriding 해서 쓰고있다.
		# 그냥 서버에 연결되었다고 프린트해주는거.
		self.onStart()

		# Main connection loop
		threads = []
		while self.isRunning():
			try:
				(socket, address) = serversocket.accept()
				# target은 실제로 스레드가 실행할 함수를 입력하면되고, 그 함수에게 전달할 인자를 args에 입력하시면 된다.
				# 여기서는 self를 호출하고, 거기에 인자로 소켓을 넘겨준다.
				# self객체를 호출했으니, 호출함수인 receiver 클래스 안에 __call__ 함수가 호출된다.
				thread = threading.Thread(target = self, args = (socket,))
				threads.append(thread)
				thread.start()
				
			except socketlib.timeout:
				pass
			except:
				self.stop()

		# Wait for all threads
		while len(threads):
			threads.pop().join()

		# On stop!
		self.onStop()

	def onStart(self):
		pass

	def onStop(self):
		pass



class Client(Receiver):
	
	def start(self, ip, port):
		# Set up server socket
		self._socket = socketlib.socket(socketlib.AF_INET, socketlib.SOCK_STREAM)
		self._socket.settimeout(1)
		self._socket.connect((ip, int(port)))

		# On start!
		self.onStart()

		# Start listening for incoming messages
		self._thread = threading.Thread(target = self, args = (self._socket,))
		self._thread.start()
		
	def send(self, message):
		# Send message to server
		self._lock.acquire()
		self._socket.send(message.strip()+b'\n')
		self._lock.release()
		time.sleep(0.5)

	def stop(self):
		# Stop event loop
		Receiver.stop(self)
		
		# Join thread
		if self._thread != threading.currentThread():
			self._thread.join()
		
		# On stop!
		self.onStop()		

	def onStart(self):
		pass

	def onStop(self):
		pass
		
	def onJoin(self):
		self.stop()
