#!/bin/bash

# python3 pTSimPy.py 62500 10 > tests/simpy.out &
# #pid=$! $
# psrecord $! --interval 1 --duration 100 --plot test.png

dist="100"
lookahead="0.1"
seed="10"
duration="10000"

help()
{
    echo "Usage: SIZE ENDTIME [ -d | --distance ]
                    [ -l | --lookahead ]
                    [ --seedR ]"
    exit 2
}

VALID_ARGUMENTS=$#

if [ "$VALID_ARGUMENTS" -lt 2 ];then
  if [ "$1" == "clean" ];then
    rm tests/Simian/*
    rm tests/Simulus/*
    rm tests/Simpy/*
    exit 2
  else
    help
  fi
fi

if [ "$3" == "-d" ] && [ "$VALID_ARGUMENTS" -gt 3 ]
then
    dist=$4
elif [ "$3" == "-l" ] && [ "$VALID_ARGUMENTS" -gt 3 ]
then
    lookahead=$4
elif [ "$3" == "--seedR" ] && [ "$VALID_ARGUMENTS" -gt 3 ]
then
    seed=$4
fi

if [ "$5" == "-d" ] && [ "$VALID_ARGUMENTS" -gt 5 ]
then
    dist=$6
elif [ "$5" == "-l" ] && [ "$VALID_ARGUMENTS" -gt 5 ]
then
    lookahead=$6
elif [ "$5" == "--seedR" ] && [ "$VALID_ARGUMENTS" -gt 5 ]
then
    seed=$6
fi

if [ "$7" == "-d" ] && [ "$VALID_ARGUMENTS" -gt 7 ]
then
    dist=$8
elif [ "$7" == "-l" ] && [ "$VALID_ARGUMENTS" -gt 7 ]
then
    lookahead=$8
elif [ "$7" == "--seedR" ] && [ "$VALID_ARGUMENTS" -gt 7 ]
then
    seed=$8
fi

python3 pTSimPy.py $1 $2 -d $dist -l $lookahead --seedR $seed > tests/Simpy/simpyS$1-D$dist-L$lookahead-SD$seed.out &
psrecord $! --interval 1 --duration $duration --plot tests/Simpy/simpyS$1-D$dist-L$lookahead-SD$seed.png

python3 pTSimulus.py $1 $2 -c 1 -d $dist -l $lookahead --seedR $seed > tests/Simulus/simulus1S$1-D$dist-L$lookahead-SD$seed.out &
psrecord $! --interval 1 --duration $duration --plot tests/Simulus/simulus1S$1-D$dist-L$lookahead-SD$seed.png

python3 pTSimulus.py $1 $2 -c 2 -d $dist -l $lookahead --seedR $seed > tests/Simulus/simulus2S$1-D$dist-L$lookahead-SD$seed.out &
psrecord $! --interval 1 --duration $duration --plot tests/Simulus/simulus2S$1-D$dist-L$lookahead-SD$seed.png

python3 pTSimian.py $1 $2 -d $dist -l $lookahead --seedR $seed > tests/Simian/simianS$1-D$dist-L$lookahead-SD$seed.out &
psrecord $! --interval 1 --duration $duration --plot tests/Simian/simianS$1-D$dist-L$lookahead-SD$seed.png
