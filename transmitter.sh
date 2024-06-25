#!/bin/zsh

# Server details
HOST="dapnet.afu.rwth-aachen.de"  # Replace with actual master IP address
PORT=43434

# Login credentials (replace with your credentials)
CALLSIGN="n0call"
AUTHKEY="key"

# Function to send data to server
send_data() {
  local data="$1"
  echo "$data" | nc -w 1 $HOST $PORT
}

# Build login message
login_data="[dapnet-lite v1.0.0 $CALLSIGN $AUTHKEY]\n"

# Send login data
send_data "$login_data"

# Process server response
while IFS=':' read -r response_type response_time; do
  if [[ $response_type -eq 2 ]]; then
    # Received server time, send dummy response (ignored by server now)
    send_data "2:$response_time:0000\n+\n"
  elif [[ $response_type -eq 3 ]] || [[ $response_type -eq 4  ]]; then
    # Received server time, send dummy response (ignored by server now)
    send_data "+\n"

    # Simulate receiving some messages (modify as needed)
    for msg_id in {01..05}; do
      message_data="6:1:11A8:3:#$msg_id message content!+ ujung!"
      send_data "#$msg_id"
      sleep 1  # Simulate processing delay
      send_data "+"
    done
    break;  # Exit after receiving a few messages
  else
    echo "Error: Unexpected response type: $response_type"
    exit 1
  fi
done < <(nc -w 5 $HOST $PORT)

echo "Finished communication with server."

