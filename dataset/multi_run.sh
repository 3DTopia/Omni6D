#!/bin/bash
Njob=4
split=$1
device=$2

# Njob=<number-of-jobs-in-a-GPU>
# split=<train/val/test>
# device=<GPU-id>

for ((i=0; i<$Njob; i++)); do

{
    echo  "progress $i is running"
    bash run_batch.sh ${split} ${device} & 
    sleep 5
}

done

wait    

echo -e "time-consuming: $SECONDS seconds"  