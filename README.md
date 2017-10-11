<p align="center">
  <a href="https://github.com/Clinical-Genomics/genotype">
    <img width="240px" height="180px" src="artwork/icon.png"/>
  </a>
</p>

# Genotype [![Documentation Status][readthedocs-img]][readthedocs-url] [![Build Status][travis-img]][travis-url]
Manage SNP calling comparisons at Clinical Genomics. The package exposes a CLI and a bare bones web interface to visualize results stored in a SQLite database.

## Install

```bash
$ conda install -c bioconda pysam pyyaml sqlalchemy flask
$ pip install genotype==2.0.0-beta3
```

## License
MIT. See the [LICENSE](LICENSE) file for more details.



[readthedocs-url]: https://readthedocs.org/projects/genotype/?badge=latest
[readthedocs-img]: https://readthedocs.org/projects/genotype/badge/?version=latest

[travis-url]: https://travis-ci.org/Clinical-Genomics/genotype
[travis-img]: https://img.shields.io/travis/Clinical-Genomics/genotype.svg?style=flat
