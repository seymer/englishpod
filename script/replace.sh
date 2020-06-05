#!/bin/bash
for j in $(seq 0028 0030)
do
    echo $j
sed -i '' 's/0028dgdg/0028dg/'  englishpod_0028.html
done


