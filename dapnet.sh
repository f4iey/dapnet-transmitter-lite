#!/bin/zsh

format_data() {
   # takes dapnet messages, parse them and 
   # puts then into RIC:MSG format

}

send_pocsag() {
   # sends audio though soundcard
   # via MPV
   echo $1
   printf $1 | ./pocsag > temp.pcm
   ffmpeg -f s16le -ar 22.05k -ac 1 -i temp.pcm temp.wav -y
   mpv temp.wav
   rm temp*
}
       
