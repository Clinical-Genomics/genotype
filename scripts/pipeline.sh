taboo vcfify meta/base.vcf ID_FM3_SUMMARY_140604_MD_KD.xlsx | taboo rename meta/internal2customer.json >| fm3.customer.vcf

mkdir -p maf_samples/sorted
taboo split --out=maf_samples/ fm3.customer.vcf
cd maf_samples
for FILE in *.vcf; do
  vcf-sort $FILE > "sorted/${FILE}"
done
cd ..

mkdir -p mip_samples/slim/singles
cd mip_samples
for FILE in *.vcf; do
  taboo extract ../meta/rsnumbers.fm3.txt $FILE | taboo filter | vcf-sort >| "slim/${FILE}"
done

cd slim
for FILE in *.vcf; do
  taboo split --out=singles/ $FILE
done

cd ../..

while read SAMPLE; do
  echo $SAMPLE
  taboo compare maf_samples/sorted/${SAMPLE}*.vcf mip_samples/slim/singles/${SAMPLE}*.vcf
done < meta/sample_ids.txt

unset FILE SAMPLE
