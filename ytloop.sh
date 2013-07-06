#!/bin/sh
# figure out if we are working from a video or a file
if [[ $1 =~ "^http" || $1 =~ "^www" ]]
then
    # make a temporary file to hold the video
    TMPFILE=`mktemp fromytXXXXX`
    # get video from youtube
    youtube-dl -o $TMPFILE $1
    VIDEO=$TMPFILE
else #this is just a file that already exists
    VIDEO=$1
fi
# make a tmpfile to hold the bit we care about
BITTMP=`mktemp bitXXXX.mp4`
# use ffmpeg to get the bit we care about
ffmpeg -i $VIDEO -ss $2 -t $3 -y $BITTMP

# make three tmpfiles
SWAPTMP=`mktemp swapXXXX`
PREVTMP=`mktemp prevXXXX`

# copy it
cp $BITTMP $PREVTMP

# stitch them together with mencoder
for ((i=2;i<=$4;i++))
do
    mencoder -oac pcm -ovc copy -idx -o $SWAPTMP $PREVTMP $BITTMP
    rm $PREVTMP
    mv $SWAPTMP $PREVTMP
done
#cleanup
mv $PREVTMP $5
rm $BITTMP
