#!/usr/bin/env python
import sys
import os
import string
import re
from optparse import OptionParser

from VcfFile import *

""" concatenate an arbritary number of VCF files into a single file and print to STDOUT
    NOTE: - doesn't check for equivalent metadata ## lines  across files             """

def main():
    usage = "usage: %prog  --in file.vcf --in file2.vcf [ ... ] "
    parser = OptionParser(usage)
    parser.add_option("--in", action="append", dest="vcf_list", help="file to concatenate")
    parser.add_option("--printmetalines", action="store_true", dest="metalines", default=False, help="print metalines beginning with ##")
    (options, args)=parser.parse_args()
    commandline=" ".join(sys.argv)
    print "##commandLine " + commandline
   

    firstfile=options.vcf_list.pop(0)
    vcfh=open(firstfile, 'r')
    vcfobj=VcfFile(file)
    vcfobj.parseMetaAndHeaderLines(vcfh)
    vcfobj.printMetaInfoLines()
    for line in vcfobj.yieldVcfDataLine(vcfh):
        print line

    for file in options.vcf_list:
        vcfh=open(file, 'r')
        vcfobj=VcfFile(file)
      
        #parse its metainfo lines (ones that begin with ##)
        vcfobj.parseMetaAndHeaderLines(vcfh)
        
        if options.metalines == False:
            for line in vcfobj.yieldVcfDataLine(vcfh):
                print line
            else:
                vcfobj.printMetaInfoLines()
                for line in vcfobj.yieldVcfDataLine(vcfh):
                    print line
       

if __name__ == "__main__":
    main()
