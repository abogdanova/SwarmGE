
#!/bin/bash

cd ~/source/PonyGE2/results
# for file in $(ls gecco_regex_improvement_analysis/) ; do echo $file >> best_ever.txt ; grep "best_ever" gecco_regex_improvement_analysis/$file | uniq >> best_ever.txt ; echo " " >> best_ever.txt ; done
# grep -B1 Individual best_ever.txt | grep -v "\-\-"  > best_ever_cleaned.txt 

line_count=0

while read line 
do
    ((line_count++))
    current="$line"
    ind_count=$(echo -e "$last""\n""$current" | grep -c Individual)
    if [ $ind_count -eq 2 ]
    then
        last_clean=$(echo "$last" | awk '{ print $4 }')
        current_clean=$(echo "$current" | awk '{ print $4 }')
        
        if [ "$last_clean" != "$current_clean" ]
        then            
            last_fit=$(echo "$last" | awk '{ print $NF }')
            current_fit=$(echo "$current" | awk '{ print $NF }')
            #            echo "-----  $last_clean     $current_clean"
            calc_string=$(echo -n "((($last_fit)-($current_fit))/($last_fit))*100" | sed -e 's/[eE]/\*10\^/g')
            echo "scale=10; $calc_string" | bc | tr -d "\n"  # or something
            echo -n "     "
            
            last_len=$(echo -n "$last_clean" | wc -c )
            current_len=$(echo -n "$current_clean" | wc -c )
#            echo "-----  $last_len     $current_len"
                        
            #cmp <( echo "$last_clean" ) <( echo "$current_clean" ) | cut -d " " -f 5 | tr -d ,
            diff_start=$(cmp <(echo "$last_clean") <(echo "$current_clean") | cut -d " " -f 5 | tr -d ,)
            diff_start_count=$((diff_start - 1 ))
#            echo "-----  $diff_start_count"
            diff_end=$(cmp <(echo "$last_clean" | rev) <(echo "$current_clean" | rev) | cut -d " " -f 5 | tr -d ,)
            diff_end_count=$((diff_end - 1 ))
#            echo "-----  $diff_end_count"
            #    echo $diff_start_index" "$diff_end_count
            
            last_end_index=$((last_len - diff_end_count))
            diff_count=$((last_end_index - diff_start_count ))
            # prevent a bug where the strings differ, but differ by the same characters,
            # if 3 extra characters, but prefix is the same and suffix is the same leaving only 1 character difference by this method
            if [ $diff_count -lt 1 ]; then diff_count=0 ; fi 
            echo -n "${last_clean:$diff_start_count:$diff_count}"
            
            current_end_index=$((current_len - diff_end_count))
            diff_count=$((current_end_index - diff_start_count ))
            if [ $diff_count -lt 1 ]; then diff_count=0 ; fi 
            echo -n "   -->   ""${current_clean:$diff_start_count:$diff_count}"
            echo "        line:$line_count"
        fi
    fi
    last="$current"
done < best_ever_cleaned.txt  

cd - 
