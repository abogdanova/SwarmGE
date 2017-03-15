#!/bin/bash

# Take a regex string,
# parse it to genome with ReverseGE,
# improve with PonyGE2

regex_string="$1"
if [[ -z "$regex_string" ]]
then
    exit 1
fi
grammar_file="PCRE.bnf" # "$2"
regex_genome_file=regex_genome_$(date +"%Y%m%d%H%M%S").txt
params_template="template_seedonly_regex.txt"
parameters_file=gen_seedonly_regex_"$(echo $regex_string | sha1sum | awk '{ print $1 }')".txt

grep SEED_GENOME ../parameters/"$parameters_file"

if [[ "$?" -ne 0 ]] # if the seed genome is not set in the parameters file, parse the regex and add it
then
    cat ../parameters/template_seedonly_regex.txt > ../parameters/"$parameters_file"
    
    parser_dir="../ReverseGE"
    cur_dir="$(pwd)"
    # check the grammar file is the latest
    rsync -av ../grammars/"$grammar_file" "$parser_dir"/grammars/
    
    cd "$parser_dir"/src
    python3.5 LR_Parser.py --target "$regex_string" --grammar_file $grammar_file > "$regex_genome_file"
    
    echo "# ""$regex_string" >> "$cur_dir"/../parameters/"$parameters_file"
    cat "$regex_genome_file" |
        grep -A1 Genome |
        tr -d '\n' |
        sed 's/Genome:/SEED_GENOME:\ \ \ \ \ /g' >> "$cur_dir"/../parameters/"$parameters_file"
    
    echo "$regex_string" >> "$regex_genome_file"
    cat ../grammars/"$grammar_file" >> "$regex_genome_file"
    sha1sum ../grammars/"$grammar_file" >> "$regex_genome_file"
    cd $cur_dir
fi

echo " " 
# python3.5 ponyge.py --parameters test_seedonly_regex_catastrophic_csv_hill_schc.txt
echo "Parameters file exists: ""$cur_dir"/../parameters/"$parameters_file"
echo " " 
echo "Now run one of these:"
echo " "
echo "    python3.5 ponyge.py --parameters \"$parameters_file\""
echo " "
echo "(or in screen) "
echo " "
echo "    while [ 1 -eq 1 ] ; do for file in \$( ls ../parameters/*regex_* | awk -F\/ '{ print $NF }' | shuf ) ; do python3.5 ponyge.py --parameters $file > \$(date +\"%Y%m%d%H%M%S\")_\$(hostname)_\"\$file\"_Seed_raw_results.txt ; done ; done"

# while [ 1 -eq 1 ] ; do for file in $( ls ../parameters/*regex_* | awk -F\/ '{ print $NF }' | shuf ) ; do python3.5 ponyge.py --parameters $file > $(date +"%Y%m%d%H%M%S")_$(hostname)_"$file"_Seed_raw_results.txt ; done ; done
# while [ 1 -eq 1 ] ; do for file in $( ls ../parameters/*regex_* | awk -F\/ '{ print $NF }' | shuf ) ; do python3.5 ponyge.py --search_loop algorithm.hill_climbing.LAHC_search_loop --parameters $file > $(date +"%Y%m%d%H%M%S")_$(hostname)_"$file"_Seed_LAHC_raw_results.txt ; done ; done
# while [ 1 -eq 1 ] ; do for file in $( ls ../parameters/*regex_* | awk -F\/ '{ print $NF }' | shuf ) ; do python3.5 ponyge.py --search_loop algorithm.hill_climbing.SCHC_search_loop --parameters $file > $(date +"%Y%m%d%H%M%S")_$(hostname)_"$file"_Seed_SCHC_raw_results.txt ; done ; done
