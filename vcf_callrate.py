#!/usr/bin/python
import sys
import os
import string
import re
from optparse import OptionParser

from VcfFile import *

def main():
    usage = "usage: %prog [options] file.vcf"
    parser = OptionParser(usage)
    parser.add_option("--filter", type="string", dest="filter", help="analyze only those  records matching filter (default is None)", default=None)
    parser.add_option("--info", type="string", dest="infotag", help="INFO tag id that annotates what type of variant the VCF record is", default="TYPE")
    parser.add_option("--type", type="string", dest="variantype", help="type of variant (SNP INS DEL)", default=None)
    (options, args)=parser.parse_args()


    vcfilename=args[0]
    vcfh=open(vcfilename,'r')

    #instantiate a VcfFile object
    vcfobj=VcfFile(vcfilename)
    #parse its metainfo lines (ones that begin with ##)
    vcfobj.parseMetaLines(vcfh)
    vcfobj.addMetaInfoHeader("CR", "D", 1, "site call rate")
    vcfobj.printMetaLines()

    vcfh.seek(0)


    vcfobj.parseHeaderLine(vcfh)
    vcfobj.printHeaderLine()
    
    samplelist = vcfobj.getSampleList()
    sampleCalls={} #key sample name value #called genotypes
    for s in samplelist: sampleCalls[s]=0



    totalrecords=0
    for vrec in vcfobj.yieldVcfRecordwithGenotypes(vcfh ):
        if vrec.getFilter() != options.filter and options.filter != None : continue
        totalrecords+=1
        sitecallrate=vrec.siteCallrate()
        vrec.appendInfoString("CR="+str(sitecallrate))
        vrec.sampleCallrate(samplelist,sampleCalls)
        #print vrec.toStringwithGenotypes()

    for s in samplelist:
        callrate=float(sampleCalls[s])/float(totalrecords)
        print s, sampleCalls[s], totalrecords, callrate

if __name__ == "__main__":
    main()
