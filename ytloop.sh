#!/bin/sh
# get video from youtube
youtube-dl -o fromyt.mp4 $1
# use ffmpeg to get the bit we care about
ffmpeg -ss $2 -t $3 -i fromyt.mp4 out.mp4
# copy it
cp out.mp4 next.mp4
cp out.mp4 prev.mp4
# stitch them together with mencoder
for ((i=2;i<=$4;i++))
do
    mencoder -oac pcm -ovc copy -idx -o out.mp4 prev.mp4 next.mp4
    rm prev.mp4
    mv out.mp4 prev.mp4
done
#cleanup
mv prev.mp4 out.mp4
rm fromyt.mp4 next.mp4
