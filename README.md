<p align="center">
  <a href="https://github.com/Clinical-Genomics/genotype">
    <img width="240px" height="180px" src="artwork/icon.png"/>
  </a>
</p>


# Genotype 
![Build Status - Github][gh-actions-badge]
[![Coverage Status][coveralls-image]][coveralls-url]
[![GitHub issues-closed][closed-issues-img]][closed-issues-url]
[![Average time to resolve an issue][ismaintained-resolve-img]][ismaintained-resolve-url]
[![Percentage of issues still open][ismaintained-open-rate-img]][ismaintained-open-rate-url]
[![CodeFactor][codefactor-badge]][codefactor-url]
[![Code style: black][black-image]][black-url]
Manage SNP calling comparisons at Clinical Genomics. The package exposes a CLI and a bare bones web interface to visualize results stored in a SQLite database.

## Install

```bash
$ conda install -c bioconda pysam pyyaml sqlalchemy flask
$ pip install genotype
```

## Help?

Please check out the documentation


[readthedocs-url]: https://readthedocs.org/projects/genotype/?badge=latest
[readthedocs-img]: https://readthedocs.org/projects/genotype/badge/?version=latest

[gh-actions-badge]: https://github.com/Clinical-Genomics/genotype/workflows/Tests%20and%20Coverage/badge.svg
[closed-issues-img]: https://img.shields.io/github/issues-closed/Clinical-Genomics/genotype.svg
[closed-issues-url]: https://GitHub.com/Clinical-Genomics/genotype/issues?q=is%3Aissue+is%3Aclosed
[ismaintained-resolve-img]: http://isitmaintained.com/badge/resolution/Clinical-Genomics/genotype.svg
[ismaintained-resolve-url]: http://isitmaintained.com/project/Clinical-Genomics/genotype
[ismaintained-open-rate-img]: http://isitmaintained.com/badge/open/Clinical-Genomics/genotype.svg
[ismaintained-open-rate-url]: http://isitmaintained.com/project/Clinical-Genomics/genotype
[codefactor-badge]: https://www.codefactor.io/repository/github/clinical-genomics/genotype/badge
[codefactor-url]: https://www.codefactor.io/repository/github/clinical-genomics/genotype
[black-image]: https://img.shields.io/badge/code%20style-black-000000.svg
[black-url]: https://github.com/psf/black

[coveralls-url]: https://coveralls.io/github/Clinical-Genomics/genotype
[coveralls-image]: https://coveralls.io/repos/github/Clinical-Genomics/genotype/badge.svg?branch=master
