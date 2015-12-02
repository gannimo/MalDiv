#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathias Payer <mathias@nebelwelt.net>"
__description__ = "Test similarity of two binaries (by first extracting the code, then comparing the code sequences using a suffix tree)."
__version__ = filter(str.isdigit, "$Revision: 1 $")

import sys
from objdump import ObjDump
from suffix_tree import GeneralisedSuffixTree
#from Bio import trie
import binascii
import gc

def parse(fil):
    bin1 = ObjDump(fil)
    badstrings = {".fini", ".init", "_init", "_start", "deregister_tm_clones", "register_tm_clones", "__do_global_dtors_aux", "frame_dummy", "__i686.get_pc_thunk.bx", "__libc_csu_init", "__libc_csu_fini", "_fini"}
    bin1all = {}
    bin1fun = {}
    bin1arr = []
    for name, label in bin1.labels.iteritems():
        if name.find("@plt") == -1 and "instructions" in label and not name in badstrings:
            for instr in label["instructions"]:
                for byte in instr:
                    bin1arr.append(byte)
            instrseq = {}
            for instr in label["mnemonics"]:
                if instr in instrseq:
                    instrseq[instr] += 1
                else:
                    instrseq[instr] = 1
                if instr in bin1all:
                    bin1all[instr] += 1
                else:
                    bin1all[instr] = 1
            bin1fun[name] = instrseq
    return (bin1, bin1arr, bin1fun, bin1all)

def parseBench(f1, f2, f3, f4, f5):
    (bin1, bin1arr, bin1fun, bin1all) = parse(f1)
    (bin2, bin2arr, bin2fun, bin2all) = parse(f2)
    (bin3, bin3arr, bin3fun, bin3all) = parse(f3)
    (bin4, bin4arr, bin4fun, bin4all) = parse(f4)
    (bin5, bin5arr, bin5fun, bin5all) = parse(f5)

    bin1arrB = ''.join(chr(x) for x in bin1arr)
    bin2arrB = ''.join(chr(x) for x in bin2arr)
    bin3arrB = ''.join(chr(x) for x in bin3arr)
    bin4arrB = ''.join(chr(x) for x in bin4arr)
    bin5arrB = ''.join(chr(x) for x in bin5arr)

    hex1arr = binascii.hexlify(bin1arrB)
    hex2arr = binascii.hexlify(bin2arrB)
    hex3arr = binascii.hexlify(bin3arrB)
    hex4arr = binascii.hexlify(bin4arrB)
    hex5arr = binascii.hexlify(bin5arrB)

    matches = {}
    matches3 = {}
    matches4 = {}
    matches5 = {}
    stree = GeneralisedSuffixTree([hex1arr, hex2arr])
    for shared in stree.sharedSubstrings(20):
        for seq, start, stop in shared:
            if seq == 0:
                leng = (stop-start)/2
                if leng in  matches:
                    matches[leng] += 1
                else:
                    matches[leng] = 1
                match = hex1arr[start:stop]
                if match in hex3arr:
                    if leng in matches3:
                        matches3[leng] += 1
                    else:
                        matches3[leng] = 1
                    if match in hex4arr:
                        if leng in matches4:
                            matches4[leng] += 1
                        else:
                            matches4[leng] = 1
                        if match in hex5arr:
                            if leng in matches5:
                                matches5[leng] += 1
                            else:
                                matches5[leng] = 1
                        
    return (matches, matches3, matches4, matches5)
#    last = 9
#    for i in range(len(f1[0:-3])):
#        sys.stdout.write(" ")
#    sys.stdout.write("\t")
#    for i in range(len(matches)):
#        sys.stdout.write(str(i+10)+"\t")
#
#    sys.stdout.write("\n"+f1[0:-3]+"\t")
#    for i in sorted(matches):
#        sys.stdout.write(str(matches[i])+"\t")
#    sys.stdout.write("\n")
#
#    for i in range(len(f1[0:-3])):
#        sys.stdout.write(" ")
#    sys.stdout.write("\t")
#    for i in sorted(matches3):
#        sys.stdout.write(str(matches3[i])+"\t")
#    sys.stdout.write("\n")
#
#    for i in range(len(f1[0:-3])):
#        sys.stdout.write(" ")
#    sys.stdout.write("\t")
#    for i in sorted(matches4):
#        sys.stdout.write(str(matches4[i])+"\t")
#    sys.stdout.write("\n")
#
#    for i in range(len(f1[0:-3])):
#        sys.stdout.write(" ")
#    sys.stdout.write("\t")
#    for i in sorted(matches5):
#        sys.stdout.write(str(matches5[i])+"\t")
#    sys.stdout.write("\n")


def parseName(arg):
    return parseBench(arg, arg[0:-1]+"2", arg[0:-1]+"3", arg[0:-1]+"4", arg[0:-1]+"5")

def parseDir(arg):
    #benchmarks = {"astar", "bzip2", "dealII", "gcc", "gobmk", "h264ref", "hmmer", "lbm", "libquantum", "mcf", "milc", "namd", "omnetpp", "perlbench", "povray", "sjeng", "soplex", "sphinx_livepretend", "Xalan"}
    #benchmarks = {"astar", "bzip2", "dealII", "gobmk", "hmmer", "lbm", "libquantum", "mcf", "milc", "namd", "omnetpp", "povray", "sjeng", "soplex", "sphinx_livepretend"}
    #benchmarks = {"bzip2"}
    #benchmarks = {"astar", "bzip2", "lbm", "libquantum", "mcf", "milc", "sjeng" }
    benchmarks = {"h264ref", "hmmer","milc", "namd", "sjeng", "soplex", "sphinx_livepretend"} 
    results = {}

    for i in benchmarks:
        results[i] = parseName(arg+"/"+i+"-1")
    #    ctr = 2
    #    for res in results:
    #        sys.stdout.write("\n"+"{0: <11}".format(i+"-"+str(ctr))+" ")
    #        ctr = ctr+1
    #        for j in sorted(res):
    #            sys.stdout.write(str(res[j])+"\t")
    #        sys.stdout.write("\n")
                                                                                

    maxlen = 0
    for bench in results:
        if len(results[bench][0]) > maxlen:
            maxlen = len(results[bench][0])

    sys.stdout.write("{0: <11}".format("len")+" ")
    for i in range(maxlen):
        sys.stdout.write(str(i+10)+"\t")
    
    for bench in results:
        ctr = 2
        for res in results[bench]:
            sys.stdout.write("\n"+"{0: <11}".format(bench+"-"+str(ctr))+" ")
            ctr = ctr+1
            for j in sorted(res):
                sys.stdout.write(str(res[j])+"\t")
            sys.stdout.write("\n")

if __name__ == "__main__":
    #for i in {"./all/", "./control_flow50/", "./cfg50", "./gvdiv", "./inline50", "./randfunclist/", "./split50"}:
    #    parseDir(i);
    parseDir("./all/")
#  parseDir(sys.argv[1])

