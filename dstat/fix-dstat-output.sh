#!/bin/bash

for f in "$@"
do
    perl -i~ -pe 'if($. > 6) { s/^(([^,]*,){7})(([^,]*,){3})(.*)$/$1$5/; }' $f
done
