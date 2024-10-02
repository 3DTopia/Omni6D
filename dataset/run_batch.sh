#!/bin/bash
split=$1
device=$2
for i in {1..500}; do
    echo "Iteration: $i"
    echo "Using device: $device"
    CUDA_VISIBLE_DEVICES=${device} blenderproc run dataset.py --split ${split}
done

