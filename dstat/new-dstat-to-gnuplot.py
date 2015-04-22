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

import argparse, csv, os

parser = argparse.ArgumentParser()
parser.add_argument("-b", "--disk-bandwidth-graph", nargs="+", help="Additional 'plot' subcommands that may be added in disk-bandwidth graphs")
parser.add_argument("-d", "--device-order", nargs='+', help="Add an additional number so that the disk related files have the specified order, this parameter should be a comma separated list of devices, ex: -d total sde sdd sdf sdg")
parser.add_argument("-f", "--files", nargs='+', required=True, help="dstat CSV files")
parser.add_argument("-g", "--graph", help="Additional 'plot' subcommand that may be added in all graphs")
parser.add_argument("-i", "--disk-iops-graph", nargs="+", help="Additional 'plot' subcommands that may be added in disk-IOPS graphs")
parser.add_argument("-o", "--output-directory", default=".", help="Output directory containing the graphs")
parser.add_argument("-p", "--prefix", default="dstat", help="Prefix all generated images with this string followed by a dash. Default: %(default)s")
parser.add_argument("-c", "--use-canvas", action='store_true', help="Use the 'canvas' gnuplot terminal instead of generating PNG images")
parser.add_argument("-v", "--verbose", action='store_true', help="Print debug messages")

args = parser.parse_args()



if args.verbose:
    print "Files: %s" % (args.files)
    print "Prefix: %s" % (args.prefix)
    print "Output directory: %s" % (args.output_directory)
    print "Additional graph (all): %s" % (args.graph)
    print "Additional graph (IOPS): %s" % (args.disk_iops_graph)
    print "Additional graph (bandwidth): %s" % (args.disk_bandwidth_graph)
    print "Device order: %s" % (args.device_order)
    print "Use canvas: %s" % (args.use_canvas)



green="228B22"
yellow="FFD700"
red="B22222"
grey="7F7F7F"
size="1680,1050"
extension = "html" if args.use_canvas else "png"
terminal = "canvas standalone mousing" if args.use_canvas else "png"
def generate_graph(output_file, plot_fragments, additional_commands=[]):
    """Generates a gnuplot graph in the given output file, plotting the given
    fragments. Additional gnuplot commands may be provided to customize the
    graph even more."""
    base = ['set output "%s/%s-%s.%s"' % (args.output_directory, args.prefix, output_file, extension),
            'set datafile separator ","',
            'set xtics rotate by -45',
            'set xdata time',
            'set timefmt "%d-%m %H:%M:%S"',
            'set format x "%m-%d %H:%M"',
            'set term %s size %s' % (terminal, size),
            'set grid layerdefault']
    if args.graph is not None:
        plot_fragments.append(args.graph)
    lines = base + additional_commands
    lines.append("plot %s" % (", ".join(plot_fragments)))
    gnuplot_command = "\n".join(lines)
    if args.verbose:
        print "Executing:\n%s" % (gnuplot_command)
    os.system("echo '%s' | gnuplot" % (gnuplot_command))
    return



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
        categories = {}
        last_category=""
        for idx, cat_raw in enumerate(categories_raw):
            if(cat_raw != ""):
                last_category = cat_raw
            categories[idx] = last_category
        if args.verbose:
            print "Found categories: %s" % (categories)

        columns = next(reader) # Index column names by column number, associating them with their category
        if args.verbose:
            print "Found columns: %s" % (columns)
        index = {}
        for idx, col in enumerate(columns):
            index[categories[idx] + "|" + col] = idx + 1 # Gnuplot starts counting at 1
        if args.verbose:
            print "Column indexes: %s" % (index)

        devices = [] # Find devices if some were specified
        for column in columns:
            if column.startswith("dsk/") and column.endswith(":read"):
                devices.append(column[4:-5])
        if args.verbose:
            print "Found devices: %s" % (devices)

        generate_graph("1-procs",
                ['"%s" using %d:%d every ::7 title "Runnable queue" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['procs|run'], green),
                 '"%s" using %d:%d every ::7 title "Blocked queue" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['procs|blk'], red)],
                ['set title "Processes queues"'])

        generate_graph("2-memory",
                ['"%s" using %d:%d every ::7 title "Free memory" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['advanced memory usage|free'], green),
                 '"%s" using %d:%d every ::7 title "Used memory" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['advanced memory usage|used'], yellow),
                 '"%s" using %d:%d every ::7 title "Swapped memory" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['swap|used'], red),
                 '"%s" using %d:%d every ::7 title "Cached memory" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['advanced memory usage|cach'], grey)],
                ['set format y "%.0s %cB"',
                 'set title "Memory usage"'])

        generate_graph("3-swap",
                ['"%s" using %d:%d every ::7 title "Swap in" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['paging|in'], green),
                 '"%s" using %d:%d every ::7 title "Swap out" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['paging|out'], red)],
                ['set format y "%.0s %cB"',
                 'set title "Swap activity (paging)"'])

        if args.disk_iops_graph:
            disk_iops_additional_graphs = args.disk_iops_graph
        else:
            disk_iops_additional_graphs = []
        if args.disk_bandwidth_graph:
            disk_bandwidth_additional_graphs = args.disk_bandwidth_graph
        else:
            disk_bandwidth_additional_graphs = []
        if args.device_order is not None:
            for idx, device in enumerate(args.device_order):
                generate_graph("4-%d-disk-%s-bandwidth" % (idx, device),
                        disk_bandwidth_additional_graphs +
                        ['"%s" using %d:%d every ::7 title "Blocks in (%s)" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['dsk/%s|dsk/%s:read' % (device, device)], device, yellow),
                         '"%s" using %d:%d every ::7 title "Blocks out (%s)" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['dsk/%s|dsk/%s:writ' % (device, device)], device, red)],
                        ['set format y "%.0s %cB"',
                         'set title "%s bandwidth usage"' % (device)])
                generate_graph("4-%d-disk-%s-iops" % (idx, device),
                        disk_iops_additional_graphs +
                        ['"%s" using %d:%d every ::7 title "Number of reads (%s)" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['dsk/%s|dsk/%s:#read' % (device, device)], device, yellow),
                         '"%s" using %d:%d every ::7 title "Number of writes (%s)" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['dsk/%s|dsk/%s:#writ' % (device, device)], device, red)],
                        ['set title "%s IOPS"' % (device)])
        else:
            for device in devices:
                generate_graph("4-disk-%s-bandwidth" % (device),
                        disk_bandwidth_additional_graphs +
                        ['"%s" using %d:%d every ::7 title "Blocks in (%s)" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['dsk/%s|dsk/%s:read' % (device, device)], device, yellow),
                         '"%s" using %d:%d every ::7 title "Blocks out (%s)" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['dsk/%s|dsk/%s:writ' % (device, device)], device, red)],
                        ['set format y "%.0s %cB"',
                         'set title "%s bandwidth usage"' % (device)])
                generate_graph("4-disk-%s-iops" % (device),
                        disk_iops_additional_graphs +
                        ['"%s" using %d:%d every ::7 title "Number of reads (%s)" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['dsk/%s|dsk/%s:#read' % (device, device)], device, yellow),
                         '"%s" using %d:%d every ::7 title "Number of writes (%s)" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['dsk/%s|dsk/%s:#writ' % (device, device)], device, red)],
                        ['set title "%s IOPS"' % (device)])

        generate_graph("5-network-bandwidth",
                ['"%s" using %d:%d every ::7 title "Packets received" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['net/total|recv'], yellow),
                 '"%s" using %d:%d every ::7 title "Packets sent" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['net/total|send'], red)],
                ['set format y "%.0s %cB"',
                 'set title "network bandwidth usage"'])

        generate_graph("6-context-switches",
                ['"%s" using %d:%d every ::7 title "Context switches" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['system|csw'], grey)],
                ['set title "Context switches"'])

        generate_graph("7-cpu-activity",
                ['"%s" using %d:%d every ::7 title "CPU user load" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['total cpu usage|usr'], green),
                 '"%s" using %d:%d every ::7 title "CPU system load" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['total cpu usage|sys'], red),
                 '"%s" using %d:%d every ::7 title "CPU system load" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['total cpu usage|wai'], yellow)],
                ['set title "CPU activity"'])
        generate_graph("7-cpu-idle",
                ['"%s" using %d:%d every ::7 title "CPU idle" with points pointtype 7 pointsize 0.5 linetype rgb "#%s"' % (inputfile, index['system|time'], index['total cpu usage|idl'], grey)],
                ['set title "CPU idle"']
        )

