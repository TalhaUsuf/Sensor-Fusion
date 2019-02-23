#/bin/bash
while true
do
  read LINE < /dev/ttyACM1
  echo $LINE
done
