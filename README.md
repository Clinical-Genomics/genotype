<p align="center">
  <a href="https://github.com/Clinical-Genomics/taboo">
    <img width="240px" height="180px" src="artwork/icon.png"/>
  </a>
</p>

# Taboo genotype comparison pipeline [![Documentation Status][readthedocs-img]][readthedocs-url]
Taboo provides an automated pipipeline for comparing genotypes between different VCFs.

## Goal
This project intends to automate a pipeline for processing and comparing 1) a MAF generated Excel-book with genotypes and 2) multiple NGS generated VCF-files.

## Scope
The project will be immediately usable internally at Clinical Genomics. I don't intend to generalize the functionality further in the near future.

## Components
Each component is a separate command line call.

1. Converting a MAF Excel file to the standard VCF-format.
2. Splitting a VCF-file with multiple samples into multiple files with one sample each.
3. Extracting a subset of variants based on RS-number from a VCF-file.
4. Comparing genotypes across VCF-files.
5. Translating sample ids through a JSON dictionary.

## Install for development

```bash
$ git clone https://github.com/Clinical-Genomics/taboo && cd taboo
$ pip install --editable .
```

## Dependencies:
- [Convertion table][biomart-link] (RS number -> Genomic position and more)

### VCFTools
Download [vcftools](http://sourceforge.net/projects/vcftools/files/).

```bash
$ cd /path/to/vcftools_0.1.12a
$ make
$ make install
# Copy files in ./bin to $PATH
# Copy files in lib/perl5/site_perl to .../site/lib
```

## License
MIT. See the [LICENSE](LICENSE) file for more details.



[readthedocs-url]: https://readthedocs.org/projects/taboo/?badge=latest
[readthedocs-img]: https://readthedocs.org/projects/taboo/badge/?version=latest

[biomart-link]: http://www.ensembl.org/biomart/martview/7e283b1844f188e5b4d0638de21a9062?VIRTUALSCHEMANAME=default&ATTRIBUTES=hsapiens_snp.default.snp.chr_name|hsapiens_snp.default.snp.chrom_start|hsapiens_snp.default.snp.refsnp_id|hsapiens_snp.default.snp.allele&FILTERS=hsapiens_snp.default.filters.variation_source."dbSNP"|hsapiens_snp.default.filters.snp_filter."rs9434742,rs3753313,rs2076457,rs1065772,rs1056847,rs11264295,rs2296288,rs4804,rs1044973,rs2241801,rs3814354,rs1043833,rs1469375,rs2633852,rs1054975,rs1531875,rs2279077,rs11797,rs868891,rs1565377,rs900171,rs1056932,rs231399,rs2236052,rs3733276,rs6855349,rs6855305,rs10069050,rs8654,rs41115,rs42427,rs2273235,rs2273234,rs1050775,rs3734404,rs4871,rs204883,rs1015149,rs6883,rs16888055,rs648396,rs3734441,rs3752714,rs218965,rs7953,rs2159158,rs710098,rs1045510,rs1045511,rs2013586,rs3812471,rs11789987,rs2787374,rs8507,rs1056171,rs2229974,rs2250411,rs7070678,rs7076239,rs10763354,rs1675133,rs918144,rs587985,rs7300444,rs2075378,rs1059360,rs8716,rs10876422,rs2271189,rs3825175,rs5744857,rs14105,rs7797,rs10144418,rs7250,rs3825555,rs13065,rs1803283,rs501231,rs2970357,rs12906163,rs325400,rs8024370,rs1805105,rs26840,rs1049208,rs887854,rs1050068,rs1050069,rs2075511,rs4077410,rs1131220,rs7195377,rs3809871,rs216193,rs12452857,rs507577,rs2070106,rs2228253,rs2228251,rs2229358,rs2230772,rs1037256,rs674402,rs9302885,rs3809997,rs759073,rs7255265,rs3745681,rs2279003,rs12602,rs2292812,rs10423138,rs3764535,rs6110019,rs3810526,rs495337,rs492702,rs2229741,rs2839181,rs11702450,rs4488761,rs4633,rs12148,rs4898,rs1043031,rs1043034,rs11010"&VISIBLEPANEL=resultspanel
