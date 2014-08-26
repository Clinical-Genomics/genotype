# Taboo ID Typing Pipeline [![PyPI version][fury-image]][fury-url] [![Build Status][travis-image]][travis-url]
Taboo provides an automated pipipeline for comparing genotypes from different assays.

Taboo consist of a range of tools to compare id typing using both standard sequencing analysis pipline (VCF) with old-school microarray (MA) genotyping results.

MA results arrive in an Excel sheet and is transformed to be comparable with VCF results. They meet halfway in a new format that can be used for the comparison.

Question: combine all samples in one large VCF-file or split into sample specific...

Step 1: Consolidate formats for comparison
- The MAF Excel sheet will go through processing steps to convert it to a VCF-file.

1. Convert MAF Excel book to 1 VCF-file per sample
2. Fetch/symlink MIP VCF-file (1 per sample)
    - Always store up-to-date folder of all MIP sample VCFs (cronjob)
3. Compare each sample using dict (sample names)
4. Consolidate comparison across all samples


## Install for development

```bash
$ pip install --editable .
```


## Workflow

### Preparing MIP files
for FILE in *.vcf; do taboo extract ../rsnumbers.fm3.txt $FILE | taboo filter | vcf-sort >| "slim/$FILE"; done

### bgzip and tabix
bgzip /path/to/some.vcf
tabix -p vcf /path/to/some.vcf.gz
vcf-merge [vcf_file] | bgzip -c > ./merged.vcf.gz

1. List of samples with genotypes
    - ``0;ID-000026T;0;0;0;0;C C;C C;T T;T C;G G;C T``

2. Reduced list of samples with genotypes
    - ``ID-000026T;C C;C C;T T;T C;G G;C T``

3. List of variants with sample genotypes
    - ``rs10069050;A T;T T;T T;A A``

    + Store/Write list of samples with VCF header

4. List of VCF rows
    - ``5;89820984;rs10069050;T;C;.;.;.;GT;A/T;T/T;T/T;A/A``

    + rs10069050          => ``5;89820984;rs10069050;T;C;.;.;.``
    + ``A T;T T;T T;A A`` => ``GT;A/T;T/T;T/T;A/A``

Dependencies:
- [Convertion table][biomart-link] (RS -> Pos)


### VCFTools & Tabix
Download [vcftools](http://sourceforge.net/projects/vcftools/files/).

```bash
$ cd /path/to/vcftools_0.1.12a
$ make
$ make install
# Copy files in ./bin to $PATH
# Copy files in lib/perl5/site_perl to .../site/lib
$ brew install tabix
```

## Uploading a package to Pypi (securely)
1. Create some distributions in the normal way:
```bash
$ python setup.py sdist bdist_wheel
```

2. Upload with twine:
```bash
$ twine upload dist/*
```

3. Done!

# Tips

## Assertions vs. exceptions
Asserts should be used to test conditions that should never happen. The purpose is to crash early in the case of a corrupt program state.

Exceptions should be used for errors that can conceivably happen, and you should almost always create your own Exception classes.

For example, if you're writing a function to read from a configuration file into a dict, improper formatting in the file should raise a ConfigurationSyntaxError, while you can assert that you're not about to return None.

Assertions shouldn't determine control-flow and should be possible to optimize away without stopping the code from working.

You can use assertions to test for errors that happen as a result of your own code. Use exceptions when dealing with input from a user or external file.

Assertions in some sense test for errors that should be impossible. Anything that you haven't planned for to possibly happen. Exceptions test for possible but exceptional errors.

Ref: http://stackoverflow.com/questions/944592

## Use from __future__ import ...
In whatever script you need it, not just in one single location

## Bump version
bumpversion [patch, minor, major] --commit --tag

## String interpolation

### Reusable string interpolation
"Hello %(name)s" % dict(name='Robin')


## Contributing
Anyone can help make this project better - read [CONTRIBUTION][CONTRIBUTION.md] to get started!


## License
MIT. See the [LICENSE](LICENSE) file for more details.


[fury-url]: http://badge.fury.io/py/taboo
[fury-image]: https://badge.fury.io/py/taboo.png

[travis-url]: https://travis-ci.org/robinandeer/taboo
[travis-image]: https://travis-ci.org/robinandeer/taboo.png?branch=develop

[biomart-link]: http://www.ensembl.org/biomart/martview/7e283b1844f188e5b4d0638de21a9062?VIRTUALSCHEMANAME=default&ATTRIBUTES=hsapiens_snp.default.snp.chr_name|hsapiens_snp.default.snp.chrom_start|hsapiens_snp.default.snp.refsnp_id|hsapiens_snp.default.snp.allele&FILTERS=hsapiens_snp.default.filters.variation_source."dbSNP"|hsapiens_snp.default.filters.snp_filter."rs9434742,rs3753313,rs2076457,rs1065772,rs1056847,rs11264295,rs2296288,rs4804,rs1044973,rs2241801,rs3814354,rs1043833,rs1469375,rs2633852,rs1054975,rs1531875,rs2279077,rs11797,rs868891,rs1565377,rs900171,rs1056932,rs231399,rs2236052,rs3733276,rs6855349,rs6855305,rs10069050,rs8654,rs41115,rs42427,rs2273235,rs2273234,rs1050775,rs3734404,rs4871,rs204883,rs1015149,rs6883,rs16888055,rs648396,rs3734441,rs3752714,rs218965,rs7953,rs2159158,rs710098,rs1045510,rs1045511,rs2013586,rs3812471,rs11789987,rs2787374,rs8507,rs1056171,rs2229974,rs2250411,rs7070678,rs7076239,rs10763354,rs1675133,rs918144,rs587985,rs7300444,rs2075378,rs1059360,rs8716,rs10876422,rs2271189,rs3825175,rs5744857,rs14105,rs7797,rs10144418,rs7250,rs3825555,rs13065,rs1803283,rs501231,rs2970357,rs12906163,rs325400,rs8024370,rs1805105,rs26840,rs1049208,rs887854,rs1050068,rs1050069,rs2075511,rs4077410,rs1131220,rs7195377,rs3809871,rs216193,rs12452857,rs507577,rs2070106,rs2228253,rs2228251,rs2229358,rs2230772,rs1037256,rs674402,rs9302885,rs3809997,rs759073,rs7255265,rs3745681,rs2279003,rs12602,rs2292812,rs10423138,rs3764535,rs6110019,rs3810526,rs495337,rs492702,rs2229741,rs2839181,rs11702450,rs4488761,rs4633,rs12148,rs4898,rs1043031,rs1043034,rs11010"&VISIBLEPANEL=resultspanel
