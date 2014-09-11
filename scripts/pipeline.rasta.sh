cd /mnt/hds/proj/bioinfo/ID_TYPING
MAF_REPORT=maf/reports/ID_FM2_SUMMARY_140307_AF_KD.xlsx
SAMPLES_TO_ANALYZE=references/samples-20140709.txt

taboo vcfify "maf/reports/${MAF_REPORT}" references/base.vcf | taboo rename references/internal2customer.json >| "analysis/$(basename $MAF_REPORT).customer.vcf"

mkdir -p maf/samples/sorted
taboo split --out=maf/samples/ "analysis/$(basename $MAF_REPORT).customer.vcf"
cd maf/samples
for FILE in *.vcf; do
  vcf-sort $FILE > "sorted/${FILE}";
done
cd ../..

mkdir -p vcfs/slim/single
cd vcfs
for FILE in *.vcf; do
  taboo extract ../references/rsnumbers.txt $FILE | taboo filter | vcf-sort >| "slim/${FILE}";
done

cd slim
for FILE in *.vcf; do
  taboo split --out=single/ $FILE;
done
cd ../..

while read SAMPLE; do
  do echo $SAMPLE >> analysis/results.txt;

  taboo compare maf/samples/sorted/${SAMPLE}*.vcf vcfs/slim/single/${SAMPLE}*.vcf >> analysis/results.txt
done < references/sample_ids.txt

unset FILE SAMPLE MAF_REPORT SAMPLES_TO_ANALYZE
