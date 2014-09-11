cd /mnt/hds/proj/bioinfo/ID_TYPING

taboo vcfify maf/reports/ID_FM3_SUMMARY_140604_MD_KD.xlsx references/base.vcf | taboo rename references/internal2customer.json >| analysis/id_fm3.customer.vcf

mkdir -p maf/samples/sorted
taboo split --out=maf/samples/ analysis/id_fm3.customer.vcf
cd maf/samples
for FILE in *.vcf; do
  vcf-sort $FILE > "sorted/${FILE}";
done
cd ../..

mkdir -p vcfs/slim/single
cd vcfs
for FILE in *.vcf; do
  taboo extract ../references/rsnumbers.fm3.txt $FILE | taboo filter | vcf-sort >| "slim/${FILE}";
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

unset FILE SAMPLE
