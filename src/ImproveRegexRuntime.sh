#!/bin/bash

# Take a regex string,
# parse it to genome with ReverseGE,
# improve with PonyGE2

parameters_file="$1"
regex_string="$2"
grammar_file="PCRE.bnf" # "$2"
regex_genome_file=regex_genome_$(date +"%Y%m%d%H%M%S").txt

grep SEED_GENOME ../parameters/"$parameters_file"

if [[ "$?" -eq 1 ]] # if the seed genome is not set in the parameters file, parse the regex and add it
then
    parser_dir="../ReverseGE"
    cur_dir="$(pwd)"
    # check the grammar file is the latest
    rsync -av ../grammars/"$grammar_file" "$parser_dir"/grammars/
    
    cd "$parser_dir"/src
    python3.5 LR_Parser.py --target "$regex_string" --grammar_file $grammar_file > "$regex_genome_file"

    cat "$regex_genome_file" |
        grep -A1 Genome |
        tr -d '\n' |
        sed 's/Genome:/SEED_GENOME:\ \ \ \ \ /g' >> "$cur_dir"/../parameters/"$parameters_file"
    
    echo "$regex_string" >> "$regex_genome_file"
    cat ../grammars/"$grammar_file" >> "$regex_genome_file"
    sha1sum ../grammars/"$grammar_file" >> "$regex_genome_file"
    cd $cur_dir
fi
    
# python3.5 ponyge.py --parameters test_seedonly_regex_catastrophic_csv_hill_schc.txt
echo "Running: python3.5 ponyge.py --parameters \"$parameters_file\""
python3.5 ponyge.py --parameters "$parameters_file"
