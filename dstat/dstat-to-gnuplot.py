#!/usr/bin/env python

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

# Use with the latest dstat version from Github
# dstat --proc \
#       --cpu \
#       --cpu-use \
#       --sys \
#       --mem-adv \
#       --swap \
#       --page \
#       --disk -D total \
#       --disk-tps \
#       --net \
#       --time \
#       --output my-dstat-output.csv

import argparse, csv, os
from functools import partial

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--device-order", nargs='+', default=[], help="Add an additional number so that the disk related files have the specified order, this parameter should be a space separated list of devices, ex: -d total sde sdd sdf sdg")
parser.add_argument("-f", "--files", nargs='+', required=True, help="dstat CSV files")
parser.add_argument("-g", "--additional-plot", nargs='+', default=[], help="Additional 'plot' subcommand that may be added in all graphs")
parser.add_argument("-o", "--output-directory", default=".", help="Output directory containing the graphs")
parser.add_argument("-p", "--prefix", default="dstat", help="Prefix all generated images with this string followed by a dash. Default: %(default)s")
parser.add_argument("-s", "--use-svg", action='store_true', help="Use the 'svg' gnuplot terminal instead of generating PNG images")
parser.add_argument("-v", "--verbose", action='store_true', help="Print debug messages")

args = parser.parse_args()

if args.verbose:
    print "Files: %s" % (args.files)
    print "Prefix: %s" % (args.prefix)
    print "Output directory: %s" % (args.output_directory)
    print "Additional graph (all): %s" % (args.additional_plot)
    print "Device order: %s" % (args.device_order)
    print "Use svg: %s" % (args.use_svg)



green="228B22"
yellow="FFD700"
red="B22222"
grey="7F7F7F"
size="1680,1050"
extension = "svg" if args.use_svg else "png"
terminal = "svg enhanced mouse" if args.use_svg else "png"

def generate_graph(output_file, plot_fragments, additional_commands=[]):
    """Generates a gnuplot graph in the given output file, plotting the given
    fragments. Additional gnuplot commands may be provided to customize the
    graph even more."""
    base = ['set output "%s/%s-%s.%s"' % (args.output_directory, args.prefix, output_file, extension),
            'set datafile separator ","',
            'set xdata time',
            'set timefmt "%d-%m %H:%M:%S"',
            'set format x "%m-%d %H:%M"',
            'set xtics rotate by -30',
            'set bmargin 5',
            'set term %s size %s' % (terminal, size),
            'set grid']
    lines = base + additional_commands
    lines.append("plot %s" % (", ".join(plot_fragments + args.additional_plot)))
    gnuplot_command = "\n".join(lines)
    if args.verbose:
        print "Executing:\n%s" % (gnuplot_command)
    os.system("echo '%s' | gnuplot" % (gnuplot_command))
    return



def generate_procs(file_number, inputfile, column_index):
    generate_graph("%d-procs" % (file_number),
                   ['"%s" using %d:%d every ::7 title "Runnable queue" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, column_index['system|time'], column_index['procs|run'], green),
                    '"%s" using %d:%d every ::7 title "Blocked queue" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, column_index['system|time'], column_index['procs|blk'], red)],
                   ['set title "Processes queues"'])

def generate_total_cpu_usage(file_number, inputfile, column_index):
    generate_graph("%d-cpu-activity" % (file_number),
                   ['"%s" using %d:%d every ::7 title "User" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, column_index['system|time'], column_index['total cpu usage|usr'], green),
                    '"%s" using %d:%d every ::7 title "System" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, column_index['system|time'], column_index['total cpu usage|sys'], red),
                    '"%s" using %d:%d every ::7 title "Wait" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, column_index['system|time'], column_index['total cpu usage|wai'], yellow)],
                   ['set yrange [0:]',
                    'set ytics 5',
                    'set title "CPU activity"'])
    generate_graph("%d-cpu-idle" % (file_number),
                   ['"%s" using %d:%d every ::7 title "Idle" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, column_index['system|time'], column_index['total cpu usage|idl'], grey)],
                   ['set yrange [0:]',
                    'set ytics 5',
                    'set title "CPU idle"'])

def generate_per_cpu_usage(file_number, inputfile, column_index):
    pass

def generate_system(file_number, inputfile, column_index):
    generate_graph("%d-context-switches" % (file_number),
                   ['"%s" using %d:%d every ::7 title "Context switches" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, column_index['system|time'], column_index['system|csw'], grey)],
                   ['set format y "%.0s %c"',
                    'set title "Context switches"'])

def generate_advanced_memory_usage(file_number, inputfile, column_index):
    generate_graph("%d-memory" % (file_number),
        ['"%s" using %d:%d every ::7 title "Free memory" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, column_index['system|time'], column_index['advanced memory usage|free'], green),
         '"%s" using %d:%d every ::7 title "Used memory" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, column_index['system|time'], column_index['advanced memory usage|used'], yellow),
         '"%s" using %d:%d every ::7 title "Cached memory" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, column_index['system|time'], column_index['advanced memory usage|cach'], grey)],
        ['set format y "%.0s %cB"',
         'set title "Memory usage"'])

def generate_swap(file_number, inputfile, column_index):
     generate_graph("%d-swap" % (file_number),
         ['"%s" using %d:%d every ::7 title "Swap in" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, column_index['system|time'], column_index['swap|free'], green),
          '"%s" using %d:%d every ::7 title "Swap out" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, column_index['system|time'], column_index['swap|used'], red)],
         ['set format y "%.0s %cB"',
          'set title "Swap (usage)"'])

def generate_paging(file_number, inputfile, column_index):
     generate_graph("%d-paging" % (file_number),
         ['"%s" using %d:%d every ::7 title "Swap in" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, column_index['system|time'], column_index['paging|in'], green),
          '"%s" using %d:%d every ::7 title "Swap out" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, column_index['system|time'], column_index['paging|out'], red)],
         ['set format y "%.0s %cB"',
          'set title "Swap activity (paging)"'])

def generate_dsk(file_number, device_number, device, inputfile, column_index):
    generate_graph("%d-%d-disk-%s-bandwidth" % (file_number, device_number, device),
                   ['"%s" using %d:%d every ::7 title "Blocks in (%s)" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, column_index['system|time'], column_index['dsk/%s|read' % (device)], device, yellow),
                    '"%s" using %d:%d every ::7 title "Blocks out (%s)" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, column_index['system|time'], column_index['dsk/%s|writ' % (device)], device, red)],
                   ['set format y "%.0s %cB"',
                    'set title "\'%s\' disk bandwidth usage"' % (device)])
    generate_graph("%d-%d-disk-%s-iops" % (file_number, device_number, device),
                   ['"%s" using %d:%d every ::7 title "Number of reads (%s)" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, column_index['system|time'], column_index['dsk/%s|#read' % (device)], device, yellow),
                    '"%s" using %d:%d every ::7 title "Number of writes (%s)" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, column_index['system|time'], column_index['dsk/%s|#writ' % (device)], device, red)],
                   ['set format y "%.0s %c"',
                    'set title "\'%s\' disk IOPS"' % (device)])

def generate_net(file_number, interface_number, interface, inputfile, column_index):
    generate_graph("%d-network-bandwidth" % (file_number),
                   ['"%s" using %d:%d every ::7 title "Packets received" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, column_index['system|time'], column_index['net/total|recv'], yellow),
                    '"%s" using %d:%d every ::7 title "Packets sent" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, column_index['system|time'], column_index['net/total|send'], red)],
                   ['set format y "%.0s %cB"',
                    'set title "Network bandwidth usage"'])




supported_categories = {'procs': partial(generate_procs, 1),                                  # --proc
                        'total cpu usage': partial(generate_total_cpu_usage, 2),              # --cpu
                        'per cpu usage': partial(generate_per_cpu_usage, 3),                  # --cpu-use
                        'system': partial(generate_system, 4),                                # --sys
                        'advanced memory usage': partial(generate_advanced_memory_usage, 5),  # --mem-adv
                        'swap': partial(generate_swap, 6),                                    # --swap
                        'paging': partial(generate_paging, 7),                                # --page
                        'dsk/total': partial(generate_dsk, 8, 0, 'total'),                    # --disk
                        'net/total': partial(generate_net, 9, 0, 'total')                     # --net
                        }

os.system("mkdir -p '%s'" % (args.output_directory))

for inputfile in args.files:
    if args.verbose:
        print "Processing %s" % (inputfile)

    with open(inputfile, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        next(reader) # Skip dstat version
        next(reader) # Skip dstat author
        next(reader) # Skip host
        next(reader) # Skip command line

        categories_raw = next(reader) # Retrieve column categories (empty column = same category as previous column)
        found_categories = set(categories_raw) - {''} # Identify the categories in this file
        categories_index = {} # Map every column number to the corresponding category
        last_category=""
        for idx, cat in enumerate(categories_raw):
            if(cat != ""):
                last_category = cat
            categories_index[idx] = last_category
        if args.verbose:
            print "Found categories: %s" % (categories_index)

        columns_raw = next(reader) # Retrieve columns names
        found_columns = set(columns_raw)
        column_index = {} # Map column names to Gnuplot suitable index
        for idx, col in enumerate(columns_raw):
            column_index[categories_index[idx] + "|" + col] = idx + 1 # Gnuplot starts counting at 1
        if args.verbose:
            print "Found columns: %s" % (found_columns)
            print "Column indexes: %s" % (column_index)

        devices = [] # Find devices if some were specified
        for column in columns_raw:
            if column.startswith("dsk/") and column.endswith(":read"):
                devices.append(column[4:-5])
        if args.verbose:
            print "Found devices: %s" % (devices)

        # Keep only the supported categories
        for category in set(supported_categories.keys()) & found_categories:
            supported_categories[category](inputfile, column_index)









