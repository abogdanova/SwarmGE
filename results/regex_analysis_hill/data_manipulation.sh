#!/bin/bash

# cd ~/source/PonyGE2/results/gecco_regex_improvement_analysis

# commands to grab the latest results from cluster:
# rsync -azv galapagos:source/PonyGE2/src/2017*  .
# mkdir fin
# for file in $( grep 100$  201702* | grep gen\  | awk -F: '{ print $1 }' | sort | uniq ) ; do mv $file fin/ ; done
# best to check manually that there are only a few files which have not reached gen100 before deleting
# rm 2017020*txt
# mv fin/* .
# rmdir fin

for experiment in 'GP' 'hill'
do
    # in same order as listed in the paper
    problem_listing=( 'regex_mac_search' 'regex_mac_validation' 'regex_email_validation' 'regex_iso8601_datetime'  'regex_scientific_number' 'regex_d3_interpolate_number' 'regex_catastrophic_QT3TS_1' 'regex_catastrophic_csv' 'regex_PonyGE2_Grammar_File_Rule' )
    paste_string=""
    for prob in ${problem_listing[@]}
    do
        > "$experiment"_"$prob"_gen0_gen100_best.txt
        for file in $( ls 2*$prob*$experiment* )
        do
            grep -B3 -m1 gen\  $file | grep best_fitness | awk '{ print $3 }' | tr -d "\n"
            echo -n " "
            tac $file | grep -A3 -m2 gen\  | grep best_fitness | awk '{ print $3 }' | uniq
        done >> "$experiment"_"$prob"_gen0_gen100_best.txt
        awk '{ print ($1/$2) }'  "$experiment"_"$prob"_gen0_gen100_best.txt > "$experiment"_"$prob"_speedup.txt
        paste_string+=" $experiment"
        paste_string+="_"
        paste_string+="$prob"
        paste_string+="_speedup.txt"
    done
    paste -d \, $paste_string > "$experiment"_table_nohead.txt
    echo ${problem_listing[@]} | sed 's/\ /,/g' > "$experiment"_table.txt
    cat "$experiment"_table_nohead.txt >> "$experiment"_table.txt
    
done

#  for experiment in 'rhh' 'PIgrow' 'seedonly'
#    do
#    grep -B3 "gen\ :" *"$experiment"*txt | awk '(($4=="1") || ($4=="100") || ($2=="best_ever")) { print }' | uniq > "$experiment"_all_results.txt
#    grep -B1 gen "$experiment"_all_results.txt > "$experiment"_all_results_firstlast.txt
#    awk '{ print $NF }' "$experiment"_all_results_firstlast.txt | grep -v "\-\-" > "$experiment"_just_vals.txt
#    
#    # ONLY works in console, likely due to escape issues
#    start=0; while read line ; do if [ "$start" == "0" ] ; then first_chunk=$line ; start="1"; else echo "$first_chunk" "$line" ; start="0" ; fi  ; done < "$experiment"_just_vals.txt | uniq > "$experiment"_one_line.txt
#    
#    start=0; while read line ; do if [ "$start" == "0" ] ; then first_chunk=$line ; start="1"; else echo "$first_chunk" "$line" ; start="0" ; fi  ; done < "$experiment"_one_line.txt | uniq > "$experiment"_one_line_compare.txt
#    # cat $experiment_one_line.txt
#  
#    awk '{ print ($1/$3) }' "$experiment"_one_line_compare.txt > "$experiment"_speedup.txt
#    # echo "$experiment"_speedup.txt
#    count=0
#    full_line=""
#    while read line 
#    do
#      count=$((count+1))
#      full_line="$full_line $line"
#      if [ $count -eq 9 ] NOOOOOOOOO, we cannot assume there will be 9.
#      then
#        echo "$full_line"
#        full_line=""
#        count=0
#      fi
#    done < "$experiment"_speedup.txt > "$experiment"_table.txt
#  done

