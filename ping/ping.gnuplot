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

set term png size 1000,600
set grid layerdefault
plot '<cat' using 1 title 'Ping' with lines lt rgb "#7F7F7F"
