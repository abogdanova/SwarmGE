#!/bin/bash

cd ~/source/PonyGE2/results/RegexImprovement/second_set
for experiment in 'rhh' 'PIgrow' 'seedonly'
  do
  grep -B3 "gen\ :" *"$experiment"*txt | awk '(($4=="1") || ($4=="100") || ($2=="best_ever")) { print }' | uniq > "$experiment"_all_results.txt
  grep -B1 gen "$experiment"_all_results.txt > "$experiment"_all_results_firstlast.txt
  awk '{ print $NF }' "$experiment"_all_results_firstlast.txt | grep -v "\-\-" > "$experiment"_just_vals.txt
  
  # ONLY works in console, likely due to escape issues
  start=0; while read line ; do if [ "$start" == "0" ] ; then first_chunk=$line ; start="1"; else echo "$first_chunk" "$line" ; start="0" ; fi  ; done < "$experiment"_just_vals.txt | uniq > "$experiment"_one_line.txt
  
  start=0; while read line ; do if [ "$start" == "0" ] ; then first_chunk=$line ; start="1"; else echo "$first_chunk" "$line" ; start="0" ; fi  ; done < "$experiment"_one_line.txt | uniq > "$experiment"_one_line_compare.txt
  # cat $experiment_one_line.txt

  awk '{ print ($1/$3) }' "$experiment"_one_line_compare.txt > "$experiment"_speedup.txt
  # echo "$experiment"_speedup.txt
  count=0
  full_line=""
  while read line 
  do
    count=$((count+1))
    full_line="$full_line $line"
    if [ $count -eq 9 ]
    then
      echo "$full_line"
      full_line=""
      count=0
    fi
  done < "$experiment"_speedup.txt > "$experiment"_table.txt
done

