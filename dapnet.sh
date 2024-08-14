#!/bin/zsh
send_pocsag() {
   # sends audio though soundcard
   # via MPV
   echo $1
   printf $1 | ./pocsag > temp.pcm
   ffmpeg -f s16le -ar 22.05k -ac 1 -i temp.pcm temp.wav -y
   # Inverted phase
   # ffmpeg -f -s16le -ar 22.05k -ac 1 -af "aeval='-val(0)':c=same" -i temp.pcm temp.wav -y
   mpv temp.wav
   rm temp*
}
       
