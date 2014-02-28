# Mean and percentiles graphs

The script generate-stats.rb takes one or more CSV files as arguments and generates statistics on the contained values.

## CSV format

The input CSV files must have the following format :

* No headers
* Comma-separated values
* The time at which a value was measured ("YYYY-mm-dd HH:MM:SS")
* The value as an integer

Example :
```csv
2014-02-25 15:00:00,128
2014-02-25 15:00:00,20
2014-02-25 15:00:00,101
2014-02-25 15:00:00,36
2014-02-25 15:00:00,44
2014-02-25 15:00:00,50
2014-02-25 15:00:00,28
```

## Output

The script procudes two graphs :

* One graph "mean.png" contains the evolution of the mean over the given period
* One graph "percentiles.png" contains the evolution of the 90th, 99th, 99.9th and maximum over the given period

The metrics are consolidated on a per-minute basis.

# Licence

Copyright (c) 2014, Pierre Laporte

This code is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License version 3 only, as
published by the Free Software Foundation.

This code is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License
along with this work; if not, see <http://www.gnu.org/licenses/>.

