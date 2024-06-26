import socket
import time
import os
# init functions
os.system("source ./dapnet.sh")
# Server details
HOST = "dapnet.afu.rwth-aachen.de"  # Replace with actual master IP address
PORT = 43434

# Login credentials
CALLSIGN = "your_callsign"
AUTHKEY = "your_authkey"

def send_data(sock, data):
  """Sends data to the server."""
  sock.sendall(data.encode())

def receive_data(sock):
  """Receives data from the server."""
  data = b''
  while True:
    chunk = sock.recv(1024)
    if not chunk:
      break
    data += chunk
  return data.decode()

def handle_message(message, sock):
  """Processes received messages and sends responses."""
  # Split message by ':' delimiter
  parts = message.split(':')
  message_type = int(parts[0])
  
  if message_type == 2:
    # Server time received, respond with time and confirmation
    response = f"{message}:0000\n+\n"
    send_data(sock, response)
  elif message.startswith("#"):
    # Parse page data
    data = message.split(":", 4)
    pocsag = {
        "message_type": int(parts[0]),  # Message type (e.g., 6 for text message)
        "speed": int(parts[1]),  # POCSAG transmission speed
        "ric": int(parts[2], 16),  # RIC/CAP code (hexadecimal)
        "function_bit": int(parts[3]),  # Function bit (should always be 3)
        "content": parts[4]  # Message content
    }
    # Handle sequence numbers
    current_number = int(message.split(':')[0][1:], 16)
    next_number = current_number + 1
    response = f"#{str(hex(next_number).strip('0x').upper())} +\n"
    send_data(sock, response)
    return pocsag
  else:
    # other message type, just respond with +
    send_data(sock, "+\n")

def main():
  """Main function for login and communication loop."""
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect((HOST, PORT))

  # Login handshake
  login_data = f"[dapnet-transmitter-lite v1.0.0 {CALLSIGN}{AUTHKEY}]"
  send_data(sock, login_data)
  response = receive_data(sock)
  if not response.startswith("2:"):
    print(f"Login failed: {response}")
    return

  # Keep connection alive and receive messages
  while True:
    data = receive_data(sock) or response
    for message in data.splitlines():
      # Respond based on expected format and message type
      pocsag = handle_message(message, sock)
      # send single message to the phy layer
      os.system(f'send_pocsag "{pocsag["ric"]}:{pocsag["content"]}"')
    time.sleep(1)  # Adjust delay as needed
    response = None

if __name__ == "__main__":
  main()
