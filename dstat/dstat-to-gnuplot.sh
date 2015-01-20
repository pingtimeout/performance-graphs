#!/bin/sh

#
# Copyright (c) 2015, Pierre Laporte
#
# This code is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3 only, as
# published by the Free Software Foundation.
#
# This code is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with this work; if not, see <http://www.gnu.org/licenses/>.
#

#
# This scripts generates graphs from a dstat output.
#
# Usage : ./dstat-gnuplot.sh dstat-example node-1-
#
# The dstat file MUST have the following columns :
# ---procs--- ------memory-usage----- ----swap--- ---paging-- -dsk/total- -net/total- ---system-- ----total-cpu-usage---- ----system----
# run blk new| used  buff  cach  free| used  free|  in   out | read  writ| recv  send| int   csw |usr sys idl wai hiq siq|     time
#  14   0   0|4926M  159M 7019M 2939M|   0     0 |   0     0 |2560k    0 |2233k 1894k|  19k   41k| 70  25   2   0   0   3|15-01 15:10:51
#
# Use the following dstat command : dstat -pmsgdnyct --output file
#

SIZE="1000,600"
GREEN="228B22"
YELLOW="FFD700"
RED="B22222"
GREY="7F7F7F"

# dstat outputs
cat << EOF | gnuplot > $2dstat-procs.png
set datafile separator ","
set term png size $SIZE
set grid layerdefault
plot \
 '$1' using 1 title 'Runnable queue' with lines lt rgb "#$GREEN", \
 '$1' using 2 title 'Blocked queue' with lines lt rgb "#$RED"
EOF

cat << EOF | gnuplot > $2dstat-memory.png
set datafile separator ","
set term png size $SIZE
set grid layerdefault
set format y "%.0s %cB"
set yrange [0:]
plot \
 '$1' using 7 title 'Free memory' with lines lt rgb "#$GREEN", \
 '$1' using 8 title 'Swapped memory' with lines lt rgb "#$RED"
EOF

cat << EOF | gnuplot > $2dstat-swap-usage.png
set datafile separator ","
set term png size $SIZE
set grid layerdefault
set format y "%.0s %cB"
set yrange [0:]
plot \
 '$1' using 10 title 'Swap in' with lines lt rgb "#$YELLOW", \
 '$1' using 11 title 'Swap out' with lines lt rgb "#$RED"
EOF

cat << EOF | gnuplot > $2dstat-disk-usage.png
set datafile separator ","
set term png size $SIZE
set grid layerdefault
set yrange [0:]
plot \
 '$1' using 12 title 'Blocks in' with lines lt rgb "#$YELLOW", \
 '$1' using 13 title 'Blocks out' with lines lt rgb "#$RED"
EOF

cat << EOF | gnuplot > $2dstat-context-switches.png
set datafile separator ","
set term png size $SIZE
set grid layerdefault
plot \
 '$1' using 17 title 'Context switches' with lines lt rgb "#$GREY"
EOF

cat << EOF | gnuplot > $2dstat-cpu-usage.png
set datafile separator ","
set term png size $SIZE
set grid layerdefault
set yrange [0:100]
plot \
 '$1' using 18 title 'CPU user load' with lines lt rgb "#$GREEN", \
 '$1' using 19 title 'CPU system load' with lines lt rgb "#$RED", \
 '$1' using 21 title 'CPU IO wait time' with lines lt rgb "#$YELLOW"
EOF

cat << EOF | gnuplot > $2dstat-cpu-idle.png
set datafile separator ","
set term png size $SIZE
set grid layerdefault
set yrange [0:100]
plot \
 '$1' using 20 title 'CPU idle' with lines lt rgb "#$GREY"
EOF

