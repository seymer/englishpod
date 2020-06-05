#!/bin/sh
    for file in ./*; do
    temp_file=`basename $file`
    echo $temp_file	
done
