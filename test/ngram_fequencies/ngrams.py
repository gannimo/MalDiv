import argparse
from collections import defaultdict
import itertools
import pickle
import os.path
import sys
from sklearn.feature_extraction.text import CountVectorizer

MAX_N_GRAMS = 5

parser = argparse.ArgumentParser()
parser.add_argument('command', choices=['count', 'compare'],
                    help='command to run')
parser.add_argument('files', metavar='FILE', nargs='*',
                    help='files to compare')
args = parser.parse_args()


def run_counts():
    vectorizer = CountVectorizer(ngram_range=(1,MAX_N_GRAMS), min_df=1)
    ngrams_fit = vectorizer.fit_transform(sys.stdin)
    # print ngrams.get_feature_names()
    # print ngrams.vocabulary_.get('nop nop')

    ngrams = []
    for i in range(MAX_N_GRAMS):
        ngrams.append(defaultdict(int))
    for gram, count in zip(vectorizer.inverse_transform(ngrams_fit)[0], ngrams_fit.A[0]):
        ngrams[len(gram.split())-1][gram] = count

    for n in ngrams:
        total = 0
        for count in n.itervalues():
            total += count
        for gram in n:
            n[gram] /= float(total)

    pickle.dump(ngrams, sys.stdout)

def run_compare():
    data = []
    for name in args.files:
        with open(name) as f:
            data.append(pickle.load(f))
    
    for ngrams1, ngrams2 in itertools.combinations(data, 2):
        ngram_measures = []
        for name in args.files:
            sys.stdout.write(os.path.basename(name[:-14]))
            sys.stdout.write(',')
        for n1, n2 in zip(ngrams1, ngrams2):
            m = 1
            grams = set(n1.keys())
            grams |= set(n2.keys())
            for gram in grams:
                m -= (abs(n1[gram]-n2[gram])**2)/2.0
            ngram_measures.append(m)
            sys.stdout.write(str(m))
            sys.stdout.write(',')
        print

if args.command == 'count':
    run_counts()
elif args.command == 'compare':
    run_compare()
