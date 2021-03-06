#!/usr/bin/env python
import gzip
from VcfFile import *
from VcfMetaLines import FormatLine
from optparse import OptionParser
from collections import Counter
import os
import pysam

def main():
    
    """ given a VCF file and bam file containing the sample(s) in the VCF this will add INFO and FORMAT tags 
    to indicate the count of reference and alt alleles observed in total and per-sample and print out a new VCF"""


    usage = "usage: %prog [option] file.vcf.gz"
    parser =OptionParser(usage)
    parser.add_option("--bam", type="string", dest="bam", default=None, help="bam file to perform pileup on")
    parser.add_option("--mapq", type="float", dest="mapq", default=0., help="Exclude alignments from analysis if they have a mapping less than mapq (default is 0)")
    parser.add_option("--bq", type ="float", dest="bq", default =0. , help="Exclude bases from analysis if their supporting base quality is less that --bq (default is 0)")
    parser.add_option("--includeDuplicates", action="store_false", dest="duplicate", help="include duplicate marked reads in analysis (turned off by default) ")
    (options, args)=parser.parse_args()
    if options.bam == None:
        sys.stderr.write("please provide a value to --bam option\n")
        sys.exit(1)
    
    vcfilename=args[0]
    
    bamfilename=options.bam
    
    ra_formatline=FormatLine("RA", number='1', type='Integer', description='number of reference alleles observed')
    aa_formatline=FormatLine("AA", number='1', type='Integer', description='number of alternate alleles observed')
    
    if os.path.exists(bamfilename+".bai") == False:
        sys.stderr.write("please check for existence of bam index file (*.bai)\n")
        exit(1)
        
    vcfobj=VcfFile(vcfilename)
    
    vcfh=gzip.open(vcfilename,'r')

    vcfobj.parseMetaAndHeaderLines(vcfh)
    vcfobj.addMetaFormatHeader(ra_formatline)
    vcfobj.addMetaFormatHeader(aa_formatline)
    vcfobj.addMetaInfoHeader("RA", "Integer", "1","total number of reference alleles observed" )
    vcfobj.addMetaInfoHeader("AA", "Integer", "1","total number of alternate alleles observed" )
    header=vcfobj.returnHeader()
    
    print header
    readgroupdict={}    
    pybamfile = pysam.Samfile(bamfilename, "rb" )
    rgdictlist=pybamfile.header['RG']
    for dictionary in rgdictlist:
        readgroupdict[ dictionary['ID'] ]= dictionary['SM']
    #print readgroupdict
    
    samples=vcfobj.getSampleList()
    
    #print samples
    
    for vrec in vcfobj.yieldVcfRecordwithGenotypes(vcfh):
        (chrom, start, end)=vrec.getChrom(), int( vrec.getPos() )-1, int(vrec.getPos() )
        #print chrom, str(start), str(end)
        #print vrec.getRef()
        #print vrec.toStringwithGenotypes()
        
        for pileupcolumn in pybamfile.pileup( chrom, start, end):
            if pileupcolumn.pos != end:
                continue
            #sys.stdout.write('chr'+chrom+ " " + str(start) +  " " + str(end) + " " + str(pileupcolumn.pos) + " ")
            #print 'coverage at base %s = %s' % (pileupcolumn.pos , pileupcolumn.n)
            
            seqdict={}
            sampledict={}
            for s in samples: sampledict[s]=[]
            #print sampledict
            for (base,count) in ( ('A',0), ('C',0), ('G',0), ('T',0), ('N',0) ):
                seqdict[base]=count
            
            for pileupread in pileupcolumn.pileups:
                
               
                if pileupread.alignment.is_duplicate == True and options.duplicate == False: continue
                if pileupread.alignment.mapq < options.mapq: continue
                if  ( ord ( pileupread.alignment.qual[ pileupread.qpos -1 ] )  - 33 ) < options.bq: continue
                seqdict[ pileupread.alignment.seq[pileupread.qpos-1] ] +=1
                readgroup=dict( pileupread.alignment.tags )['RG']
                
                sample=readgroupdict[readgroup]
                #print readgroup,sample, pileupread.alignment.seq[pileupread.qpos-1]
                sampledict[sample].append(pileupread.alignment.seq[pileupread.qpos-1])
                #print pileupread.alignment.seq, len(pileupread.alignment.seq), pileupread.qpos
            
            vrec.addInfo("RA="+str(seqdict[vrec.getRef()]))
            if vrec.getAlt() != ".":
                vrec.addInfo("AA="+str(seqdict[vrec.getAlt()]))
            zip_genos=vrec.zipGenotypes(samples)
            for (sample, vcfgenobj) in zip_genos:
               
                if len(sampledict[sample]) == 0:
                    vcfgenobj.addFormat("RA")
                    vcfgenobj.addFormat("AA")
                    continue
                else:
                    ra=0
                    aa=0
                    c=dict(Counter(sampledict[sample]))
                    if vrec.getRef() in c.keys():
                        ra=c[vrec.getRef()]
                    if vrec.getAlt() in c.keys():
                        aa=c[vrec.getAlt()]
                    vcfgenobj.addFormatVal('RA', str(ra))
                    vcfgenobj.addFormatVal("AA", str(aa))
            
            #for nt in ('A', 'C', 'G', 'T', 'N'):
            #    sys.stdout.write( str(seqdict[nt]) + " ")
            #sys.stdout.write("\n")
            print vrec.toStringwithGenotypes()
            
    pybamfile.close()
        
                
            
    
    
    
    
    
    
    


if __name__ == "__main__":
    main()

