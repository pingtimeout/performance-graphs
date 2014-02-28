#!/usr/bin/env ruby

# 
# Copyright (c) 2014, Pierre Laporte
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


require 'csv'
require 'fileutils'


# Ajouter les méthodes nécessaires dans la classe Array
class Array
    # Ne fonctionne que pour les Array triés !
    def max
        at(length - 1)
    end

    # Ne fonctionne que pour les Array triés !
    def percentile(percentile)
        return at((percentile * length).ceil - 1)
    end

    def sum
        inject(0.0) { |result, el|
            result + el
        }
    end

    def mean 
        sum / size
    end
end



# Partir d'un fichier CSV qui contient [date; mesure]
ARGV.each do |filename|
    # Créer un dossier avec le nom du fichier sans ".csv"
    dataset = "statistics.#{filename.chomp(File.extname(filename))}"
    Dir.mkdir(dataset) unless File.directory?(dataset)

    # Calculer la moyenne, les pourcentiles (90, 99, 99.9) et le maximum
    measures = Hash.new
    CSV.foreach(filename, :headers => true) { |row|
        minute = row[0].gsub(/^(.{16}).*$/, '\1')
        measures[minute] = [] unless measures.key?(minute)
        measures[minute] << row[1].to_i
    }

    # Créer des fichiers .data distincts dans le dossier crée
    output_mean = File.open("#{dataset}/mean.data", File::WRONLY|File::CREAT) 
    output_90th = File.open("#{dataset}/90th-percentile.data", File::WRONLY|File::CREAT) 
    output_99th = File.open("#{dataset}/99th-percentile.data", File::WRONLY|File::CREAT) 
    output_99_9th = File.open("#{dataset}/99.9th-percentile.data", File::WRONLY|File::CREAT) 
    output_max = File.open("#{dataset}/max.data", File::WRONLY|File::CREAT) 
    measures.each do |minute, values|
        minute = "#{minute}:00"
        values_sorted = values.sort
        mean = values_sorted.mean

        output_mean.puts("#{minute} #{mean}") 
        output_90th.puts("#{minute} #{values_sorted.percentile(0.9)}")
        output_99th.puts("#{minute} #{values_sorted.percentile(0.99)}")
        output_99_9th.puts("#{minute} #{values_sorted.percentile(0.999)}")
        output_max.puts("#{minute} #{values_sorted.max}")
    end
    output_mean.close
    output_90th.close
    output_99th.close
    output_99_9th.close
    output_max.close

    # Créer un fichier .gnuplot pour générer les graphiques
    FileUtils.cp("mean.gnuplot", "#{dataset}/mean.gnuplot")
    open("#{dataset}/mean.gnuplot", 'a') { |f|
        f.puts("plot '#{dataset}/mean.data' using 1:3 with lines title 'Mean of #{dataset}'")
    }
    FileUtils.cp("percentiles.gnuplot", "#{dataset}/percentiles.gnuplot")
    open("#{dataset}/percentiles.gnuplot", 'a') { |f|
        f.puts("plot '#{dataset}/90th-percentile.data' using 1:3 with lines title '90th percentile of #{dataset}' ,\\")
        f.puts("     '#{dataset}/99th-percentile.data' using 1:3 with lines title '99th percentile of #{dataset}' ,\\")
        f.puts("     '#{dataset}/99.9th-percentile.data' using 1:3 with lines title '99.9th percentile of #{dataset}' ,\\")
        f.puts("     '#{dataset}/max.data' using 1:3 with lines title 'Max of #{dataset}'")
    }

    # Exécuter gnuplot sur ce fichier
    `gnuplot #{dataset}/mean.gnuplot > #{dataset}/mean.png`
    `gnuplot #{dataset}/percentiles.gnuplot > #{dataset}/percentiles.png`

    # Supprimer le fichier .gnuplot
#    FileUtils.rm("#{dataset}/mean.gnuplot")
#    FileUtils.rm("#{dataset}/percentiles.gnuplot")
end

