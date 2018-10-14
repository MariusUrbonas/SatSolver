#!/usr/bin/python3
import sys
import getopt
import os
from cdcl import CDCL
import time

def usage():
    print ("usage: " + sys.argv[0] + " -i input_cnf_file: cnf file to solve -s: turn on statistics -h VSIDS|RAND: variable decision heuristic")

input_cnf_file = statistics = None
heuristic = 'VSIDS'

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:sh:')
except getopt.GetoptError as err:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_cnf_file = a
    elif o == '-s': # dictionary file
        statistics = True
    elif o == '-h': # postings file
        heuristic = a
    else:
        assert False, "unhandled option"


if input_cnf_file == None:
    usage()
    sys.exit(2)

if __name__ == "__main__":
    okSAT = CDCL(input_cnf_file, heuristic)
    start_time = time.time()
    answer = okSAT.solve()
    soved_time = time.time()
    if answer == 'UNSAT':
        print('UNSAT')
    else:
        answer.sort(key = lambda x: x.name)
        print(' '.join(map(str,(map(int, answer)))))
    if statistics:
        print("--- %s seconds ---" % (soved_time - start_time))
        print("Pick branching variable invoked %s times" % okSAT.stats()['Decisions'])
