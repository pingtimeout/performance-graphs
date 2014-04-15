#!/bin/sh

#
# This scripts generates graphs from a vmstat output.
#
# Usage : ./vmstat-to-gnuplot.sh vmstat-example
#
# The vmstat file MUST have the following columns :
# procs -----------memory---------- ---swap-- -----io---- --system-- -----cpu------
# r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
#

SIZE="1000,600"
GREEN="228B22"
YELLOW="FFD700"
RED="B22222"
GREY="7F7F7F"

cat << EOF | gnuplot > vmstat-procs.png
set term png size $SIZE
set grid layerdefault
plot \
 '$1' using 1 title 'Runnable queue' with lines lt rgb "#$GREEN", \
 '$1' using 2 title 'Blocked queue' with lines lt rgb "#$RED"
EOF

cat << EOF | gnuplot > vmstat-memory.png
set term png size $SIZE
set grid layerdefault
set format y "%.0s %cB"
set yrange [0:]
plot \
 '$1' using (\$4*1000) title 'Free memory' with lines lt rgb "#$GREEN", \
 '$1' using (\$3*1000) title 'Swapped memory' with lines lt rgb "#$RED"
EOF

cat << EOF | gnuplot > vmstat-swap-usage.png
set term png size $SIZE
set grid layerdefault
set format y "%.0s %cB"
set yrange [0:]
plot \
 '$1' using (\$7*1000) title 'Swap in' with lines lt rgb "#$YELLOW", \
 '$1' using (\$8*1000) title 'Swap out' with lines lt rgb "#$RED"
EOF

cat << EOF | gnuplot > vmstat-disk-usage.png
set term png size $SIZE
set grid layerdefault
set yrange [0:]
plot \
 '$1' using 9 title 'Blocks in' with lines lt rgb "#$YELLOW", \
 '$1' using 10 title 'Blocks out' with lines lt rgb "#$RED"
EOF

cat << EOF | gnuplot > vmstat-context-switches.png
set term png size $SIZE
set grid layerdefault
plot \
 '$1' using 12 title 'Context switches' with lines lt rgb "#$GREY"
EOF

cat << EOF | gnuplot > vmstat-cpu-usage.png
set term png size $SIZE
set grid layerdefault
set yrange [0:100]
plot \
 '$1' using 13 title 'CPU user load' with lines lt rgb "#$GREEN", \
 '$1' using 14 title 'CPU system load' with lines lt rgb "#$RED", \
 '$1' using 16 title 'CPU IO wait time' with lines lt rgb "#$YELLOW"
EOF

cat << EOF | gnuplot > vmstat-cpu-idle.png
set term png size $SIZE
set grid layerdefault
set yrange [0:100]
plot \
 '$1' using 15 title 'CPU idle' with lines lt rgb "#$GREY"
EOF

