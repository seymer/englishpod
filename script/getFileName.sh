#!/bin/sh
    for file in ../html/*; do
    temp_file=`basename $file`
    echo $temp_file	
done
