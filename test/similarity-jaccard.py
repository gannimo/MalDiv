#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathias Payer <mathias@nebelwelt.net>"
__description__ = "Test similarity of two binaries (by first extracting the code, then comparing the code sequences using a suffix tree)."
__version__ = filter(str.isdigit, "$Revision: 1 $")

import sys
from objdump import ObjDump
from suffix_tree import GeneralisedSuffixTree
from Bio import trie
import binascii
import gc

def union(a, b):
    inter = {}
    for it in a:
        val = a[it]
        inter[it] = val
    for it in b:
        val = b[it]
        if it in inter:
            inter[it] += val
        else:
            inter[it] = val
    return inter

def intersect(a, b):
    uni = {}
    for it in a:
        val = a[it]
        if it in b and b[it] == val:
            uni[it] = val
    for it in b:
        val = b[it]
        if it in a and a[it] == val:
            uni[it] = val
    return uni

def jaccardfun(bin1fun, bin1all, bin2fun, bin2all):
    bin12seqs = []
    avg = 0
    for fun in bin1fun:
        seq1 = bin1fun[fun]
        if not fun in bin2fun:
            bin12seqs = [1]
            avg = 0
            break
        seq2 = bin2fun[fun]
        uni = len(union(seq1, seq2))
        inter = len(intersect(seq1, seq2))
        #print fun+" "+str(inter)+"/"+str(uni)+"="+str(inter*1.0/uni)
        bin12seqs += [inter*1.0/uni]
        avg += inter*1.0/uni
    avg /= len(bin12seqs)
    stddev = 0
    for it in bin12seqs:
        stddev += (avg-it)*(avg-it)
    stddev /= len(bin12seqs)
  
    uni = len(union(bin1all, bin2all))
    inter = len(intersect(bin1all, bin2all))
    print "Total: "+str(inter)+"/"+str(uni)+"="+str(inter*1.0/uni)
    if avg != 0:
        print "Total/fun: "+str(avg)+" stddev: "+str(stddev)
    return inter*1.0/uni

def jaccard(bin1all, bin2all):
    uni = len(union(bin1all, bin2all))
    inter = len(intersect(bin1all, bin2all))
    return inter*1.0/uni

def parse(fil):
    bin1 = ObjDump(fil)
    badstrings = {".fini", ".init", "_init", "_start", "deregister_tm_clones", "register_tm_clones", "__do_global_dtors_aux", "frame_dummy", "__i686.get_pc_thunk.bx", "__libc_csu_init", "__libc_csu_fini", "_fini"}
    bin1all = {}
    for name, label in bin1.labels.iteritems():
        if name.find("@plt") == -1 and "instructions" in label and not name in badstrings:
            for instr in label["mnemonics"]:
                if instr in bin1all:
                    bin1all[instr] += 1
                else:
                    bin1all[instr] = 1
    return bin1all

def parseall(fil):
    bin1 = parse(fil+"1")
    bin2 = parse(fil+"2")
    bin3 = parse(fil+"3")
    return bin1, bin2, bin3

def doself(arg):
    r1 = jaccard(arg[0], arg[1])
    r2 = jaccard(arg[1], arg[2])
    r3 = jaccard(arg[0], arg[2])
    return (r1+r2+r3)/3

def dofull(arg1, arg2):
    r1 = jaccard(arg1[0], arg2[0])
    r2 = jaccard(arg1[0], arg2[1])
    r3 = jaccard(arg1[0], arg2[2])

    r4 = jaccard(arg1[1], arg2[0])
    r5 = jaccard(arg1[1], arg2[1])
    r6 = jaccard(arg1[1], arg2[2])

    r7 = jaccard(arg2[1], arg2[0])
    r8 = jaccard(arg2[1], arg2[1])
    r9 = jaccard(arg2[1], arg2[2])
    return (r1+r2+r3+r4+r5+r6+r7+r8+r9)/9

if __name__ == "__main__":
  # from argparse import ArgumentParser
  # parser = ArgumentParser(description=__description__)
  # parser.add_argument("-V", "--version", action="version", version="%(prog)s {:s}".format(__version__))
  # parser.add_argument("-f", "--file", type=str, metavar="filename", help="Filename of the first file to analyze", required=False) 
  # parser.add_argument("-f2", "--file2", type=str, metavar="filename2", help="Filename of the second file to analyze", required=False) 
  # parser.add_argument("-f3", "--file3", type=str, metavar="filename3", help="Filename of the third file to analyze", required=False) 
  # parser.add_argument("-f4", "--file4", type=str, metavar="filename4", help="Filename of the fourth file to analyze", required=False) 
  # args = parser.parse_args()

  benches = {}
  benchmarks = {"astar", "bzip2", "dealII", "gcc", "gobmk", "h264ref", "hmmer", "lbm", "libquantum", "mcf", "milc", "namd", "omnetpp", "perlbench", "povray", "sjeng", "soplex", "sphinx_livepretend", "Xalan"}
  for i in benchmarks:
    benches[i] = parseall(str(sys.argv[1]) + i + "-")

  single = []
  for bench in list(sorted(benches)):
      print bench+" "+str(round(doself(benches[bench]),2))
      single.append(round(doself(benches[bench]),2))
      
  import sys
  counter = 0
  for bench1 in list(sorted(benches)):
      counter += 1
      sys.stdout.write(str(counter))
      mx = single[counter-1] 
      for bench2 in list(sorted(benches)):
          if bench1 < bench2:
              cur = round(dofull(benches[bench1], benches[bench2]),2)
              if cur > mx:
                  mx = cur
      for i in range(counter):
          sys.stdout.write("&")
      if mx == single[counter-1]:
          sys.stdout.write("\\textbf{"+"{0:.2f}".format(single[counter-1])+"}")
      else:
          sys.stdout.write("{0:.2f}".format(single[counter-1]))
      for bench2 in list(sorted(benches)):
          if bench1 < bench2:
              sys.stdout.write(" & ")
              cur = round(dofull(benches[bench1], benches[bench2]),2)
              if cur > single[counter-1]:
                  sys.stdout.write("\\textbf{"+"{0:.2f}".format(round(dofull(benches[bench1], benches[bench2]),2))+"}")
              else:
                  sys.stdout.write("{0:.2f}".format(round(dofull(benches[bench1], benches[bench2]),2)))
      print "\\\\"
  
  # print "bzip2: "+str(doself(bzip2))+" "+str(dofull(bzip2, bzip2))
  # print "lbm: "+str(doself(lbm))
  
  # bin1 = ObjDump(args.file)
  # bin2 = ObjDump(args.file2)
  # bin3 = ObjDump(args.file3)
  # bin4 = ObjDump(args.file4)

  # badstrings = {".fini", ".init", "_init", "_start", "deregister_tm_clones", "register_tm_clones", "__do_global_dtors_aux", "frame_dummy", "__i686.get_pc_thunk.bx", "__libc_csu_init", "__libc_csu_fini", "_fini"}
  # bin1arr = []
  # bin1fun = {}
  # bin1all = {}
  # for name, label in bin1.labels.iteritems():
  #     if name.find("@plt") == -1 and "instructions" in label and not name in badstrings:
  #         for instr in label["instructions"]:
  #             for byte in instr:
  #                 bin1arr.append(byte)
  #         instrseq = {}
  #         for instr in label["mnemonics"]:
  #             if instr in instrseq:
  #                 instrseq[instr] += 1
  #             else:
  #                 instrseq[instr] = 1
  #             if instr in bin1all:
  #                 bin1all[instr] += 1
  #             else:
  #                 bin1all[instr] = 1
  #         bin1fun[name] = instrseq

  # bin2arr = []
  # bin2fun = {}
  # bin2all = {}
  # for name, label in bin2.labels.iteritems():
  #     if name.find("@plt") == -1 and "instructions" in label and not name in badstrings:
  #         for instr in label["instructions"]:
  #             for byte in instr:
  #                 bin2arr.append(byte)
  #         instrseq = {}
  #         for instr in label["mnemonics"]:
  #             if instr in instrseq:
  #                 instrseq[instr] += 1
  #             else:
  #                 instrseq[instr] = 1
  #             if instr in bin2all:
  #                 bin2all[instr] += 1
  #             else:
  #                 bin2all[instr] = 1
  #         bin2fun[name] = instrseq

  # bin3arr = []
  # bin3fun = {}
  # bin3all = {}
  # for name, label in bin3.labels.iteritems():
  #     if name.find("@plt") == -1 and "instructions" in label and not name in badstrings:
  #         for instr in label["instructions"]:
  #             for byte in instr:
  #                 bin3arr.append(byte)
  #         instrseq = {}
  #         for instr in label["mnemonics"]:
  #             if instr in instrseq:
  #                 instrseq[instr] += 1
  #             else:
  #                 instrseq[instr] = 1
  #             if instr in bin3all:
  #                 bin3all[instr] += 1
  #             else:
  #                 bin3all[instr] = 1
  #         bin3fun[name] = instrseq

  # bin4arr = []
  # bin4fun = {}
  # bin4all = {}
  # for name, label in bin4.labels.iteritems():
  #     if name.find("@plt") == -1 and "instructions" in label and not name in badstrings:
  #         for instr in label["instructions"]:
  #             for byte in instr:
  #                 bin4arr.append(byte)
  #         instrseq = {}
  #         for instr in label["mnemonics"]:
  #             if instr in instrseq:
  #                 instrseq[instr] += 1
  #             else:
  #                 instrseq[instr] = 1
  #             if instr in bin4all:
  #                 bin4all[instr] += 1
  #             else:
  #                 bin4all[instr] = 1
  #         bin4fun[name] = instrseq

  # jaccard(bin1fun, bin1all, bin2fun, bin2all)
  # jaccard(bin2fun, bin2all, bin3fun, bin3all)
  # jaccard(bin1fun, bin1all, bin3fun, bin3all)
  
  # bin1arrB = ''.join(chr(x) for x in bin1arr)
  # bin2arrB = ''.join(chr(x) for x in bin2arr)
  # bin3arrB = ''.join(chr(x) for x in bin3arr)

  # hex1arr = binascii.hexlify(bin1arrB)
  # hex2arr = binascii.hexlify(bin2arrB)
  # hex3arr = binascii.hexlify(bin3arrB)

  # matches = {}
  # stree = GeneralisedSuffixTree([hex1arr, hex2arr])
  # for shared in stree.sharedSubstrings(20):
  #     for seq, start, stop in shared:
  #         leng = (stop-start)/2
  #         if leng in  matches:
  #             matches[leng] += 1
  #         else:
  #             matches[leng] = 1
  # print matches

  # matches = {}
  # stree = GeneralisedSuffixTree([hex1arr, hex3arr])
  # for shared in stree.sharedSubstrings(20):
  #     for seq, start, stop in shared:
  #         leng = (stop-start)/2
  #         if leng in  matches:
  #             matches[leng] += 1
  #         else:
  #             matches[leng] = 1
  # print matches

  # matches = {}
  # stree = GeneralisedSuffixTree([hex2arr, hex3arr])
  # for shared in stree.sharedSubstrings(20):
  #     for seq, start, stop in shared:
  #         leng = (stop-start)/2
  #         if leng in  matches:
  #             matches[leng] += 1
  #         else:
  #             matches[leng] = 1
  # print matches

  # matches = {}

  # # try to free some memory
  # #stree = 0
  # #gc.collect()
  
  # stree = GeneralisedSuffixTree([hex1arr, hex2arr, hex3arr])
  # for shared in stree.sharedSubstrings(20):
  #     for seq, start, stop in shared:
  #         leng = (stop-start)/2
  #         if leng in  matches:
  #             matches[leng] += 1
  #         else:
  #             matches[leng] = 1
  # print matches

  # print '-'*70
      # for seq,start,stop in shared:
      #     print seq, '['+str(start)+':'+str(stop)+']',
      #     print stree.sequences[seq][start:stop],
      #     print stree.sequences[seq][:start]+'|'+stree.sequences[seq][start:stop]+\
      #         '|'+stree.sequences[seq][stop:]
  # trieobj = trie.trie()
  # trieobj[hex1arr] = 1
  # trieobj[hex2arr] = 2
  # #print bin1arrB
  # #print bin2arrB
  # print trieobj.keys()
