#!/bin/bash

SET=all

ls ../bins/$SET/* | parallel -j16 \
    "objdump -d {} --no-show-raw-insn \
        | cut -d ':' -f 2 \
        | cut -d ' ' -f 1 \
        | sed -e 's/\t//' -e 's/ //' -e '/^$/d' \
        | tr '\n' ' ' \
        | python ngrams.py count > {}-ngrams.pickle"

for b in astar bzip2 dealII gcc gobmk h264ref hmmer lbm libquantum mcf milc namd omnetpp perlbench povray sjeng soplex specrand sphinx_livepretend Xalan
do
    parallel python ngrams.py compare ::: `ls ../bins/$SET/$b*.pickle` ::: `ls ../bins/$SET/$b*.pickle`
done

# SET=baseline

# BINS="astar bzip2 dealII gcc gobmk h264ref hmmer lbm libquantum mcf milc namd omnetpp perlbench povray sjeng soplex specrand sphinx_livepretend Xalan"
# parallel python ngrams.py compare "../bins/$SET/{1}-ngrams.pickle" "../bins/$SET/{2}-ngrams.pickle" ::: $BINS ::: $BINS
