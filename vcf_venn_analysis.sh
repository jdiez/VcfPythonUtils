#!/bin/bash
#encapsulate intersection analysis for a pari of vcf files
#do venn analysis for pair of vcf files
VCF1=$1
VCF2=$2

if [[ $VCF1 == "" ]] | [[ $VCF2 == "" ]]; then
  echo "Usage: vcf_venn_analysis.sh file1.vcf file2.vcf"
  exit 1
fi

# Check the vcf file exists.
if [ ! -f $VCF1 ]; then
  echo "Cannot find index file: $VCF1"
  exit 1
fi

# Check the vcf file exists.
if [ ! -f $VCF2 ]; then
  echo "Cannot find index file: $VCF1"
  exit 1
fi

# extract the snps that pass filters
echo "extract PASS snps from $VCF1 $VCF2"
vcf_extract_variantclass.py  --info TYPE --type snp --filter PASS $VCF1 > 1.pass.snps.vcf
vcf_extract_variantclass.py  --info TYPE --type snp --filter PASS $VCF2  > 2.pass.snps.vcf


vcf_intersect.py 1.pass.snps.vcf 2.pass.snps.vcf > 1.intersect.2.pass.snps.vcf
echo "intersection of PASS snps $VCF1 $VCF2"
grep -v \# 1.intersect.2.pass.snps.vcf  | wc -l


vcf_intersect.py --v  1.pass.snps.vcf 2.pass.snps.vcf > 1.diff.2.pass.snps.vcf
echo "uniq fraction PASS snps $VCF1"
grep -v \# 1.diff.2.pass.snps.vcf | wc -l

vcf_intersect.py --v  2.pass.snps.vcf 1.pass.snps.vcf > 2.diff.1.pass.snps.vcf
echo "uniq fraction PASS snps $VCF2"
grep -v \# 2.diff.1.pass.snps.vcf | wc -l

echo "extract filter snps from $VCF1 $VCF2"
vcf_extract_variantclass.py  --info TYPE --type snp --filter . $VCF1  > 1.filtered.snps.vcf
vcf_extract_variantclass.py  --info TYPE --type snp --filter . $VCF2  > 2.filtered.snps.vcf

echo "unique snps in $genomic_original_filter not detected in $WGA_original_filter"
vcf_intersect.py --v 1.diff.2.pass.snps.vcf --filter PASS  2.filtered.snps.vcf

echo "unique snps in $VCF1  filtered in $VCF2"
vcf_intersect.py  1.diff.2.pass.snps.vcf --filter PASS  2.filtered.snps.vcf >  1.uniq.pass.2.filtered.vcf
grep -v \# 1.uniq.pass.2.filtered.vcf | wc -l

echo "unique snps in $VCF1  not detetected in filtered  in $VCF2"
vcf_intersect.py  --v  1.diff.2.pass.snps.vcf --filter PASS  2.filtered.snps.vcf   | grep -v \# | awk '{print $1 "\t" $2-1 "\t" $2}' > 1.pass.uniq.bed
wc -l 1.pass.uniq.bed

echo "unique snps in $VCF2  not detetected in filtered  in $VCF1"
vcf_intersect.py  --v  2.diff.1.pass.snps.vcf --filter PASS  1.filtered.snps.vcf   | grep -v \# | awk '{print $1 "\t" $2-1 "\t" $2}' > 2.pass.uniq.bed
wc -l 2.pass.uniq.bed
