import socket
import os
import math
import time

# init functions
os.system("source ./dapnet.sh")
# Server details
HOST = "dapnet.afu.rwth-aachen.de"  # Replace with actual master IP address
PORT = 43434
TIMESLOTS = ''

# Login credentials
CALLSIGN = "your_callsign"
AUTHKEY = "your_authkey"

# PTT via GPIO
import RPi.GPIO as GPIO
PTT_PIN = 11
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PTT_PIN, GPIO.OUT)
GPIO.output(PTT_PIN, GPIO.HIGH) # change state according to ptt triggering

def send_data(sock, data):
  """Sends data to the server."""
  sock.sendall(data.encode())

def receive_data(sock):
  """Receives data from the server."""
  return sock.recv(1024).decode()

def get_timeslot():
  """Returns the current timeslot"""
  t = math.floor(time.time() / 100)
  return hex((t >> 6) & 0xF).strip('0x').upper()

def handle_message(message, sock):
  """Processes received messages and sends responses."""
  global TIMESLOTS
  if message.startswith("2"):
    # Server time received, respond with time and confirmation
    response = f"{message}:0000\r\n+\r\n"
    send_data(sock, response)
  elif message.startswith("#"):
    # Parse page data
    parts = message[4:].split(":", 4)
    pocsag = {
        "message_type": int(parts[0]),  # Message type (e.g., 6 for text message)
        "speed": int(parts[1]),  # POCSAG transmission speed
        "ric": int(parts[2], 16),  # RIC/CAP code (hexadecimal)
        "function_bit": int(parts[3]),  # Function bit (should always be 3)
        "content": parts[4]  # Message content
    }
    # Handle sequence numbers
    current_number = int(message[1:3], 16)
    next_number = current_number + 1 if current_number < 255 else 0
    response = f"#{str(hex(next_number).strip('0x').upper())} +\r\n" if next_number >= 10 else f"#0{str(hex(next_number).strip('0x').upper())} +\r\n"
    send_data(sock, response)
    return pocsag
  elif message.startswith("4"):
      # timeslots the transmitter is allowed to use
      TIMESLOTS = message[2:]
      send_data(sock, "+\r\n")
  else:
    # other message type, just respond with +
    send_data(sock, "+\r\n")

def make_batch_string(queue):
  """Create the batch string by appending to array"""
  batch_str = ""
  for ric in queue: batch_str += ric + ':' + queue[ric] + '\\n'
  return batch_str

def main():
  """Main function for login and communication loop."""
  queue = {}
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect((HOST, PORT))
  print("connection established...")

  # Login handshake
  login_data = f"[dapnet-transmitter-lite v1.0.0 {CALLSIGN} {AUTHKEY}]\r\n"
  print("attempting to login...")
  send_data(sock, login_data)

  # Keep connection alive and receive messages
  while True:
    data = receive_data(sock)
    for message in data.splitlines():
      # Respond based on expected format and message type
      print(message)
      pocsag = handle_message(message, sock)
      # send single message to the phy layer
      if pocsag is not None: queue.update({pocsag["ric"]: pocsag["content"]})
      if get_timeslot() in TIMESLOTS and bool(queue): 
        # PTT
        GPIO.output(PTT_PIN, GPIO.LOW)
        os.system(f'send_pocsag "{make_batch_string(queue)}"')
        GPIO.output(PTT_PIN, GPIO.HIGH)
        queue.clear()

if __name__ == "__main__":
  main()
