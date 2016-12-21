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

## Deploy to Amazon Elastic Beanstalk

This guide uses the command line utility for Elastic Beanstalk (EB): `eb`.

1. Create a new application by running `eb init` in the root of the repository.
2. Create a new environment by running `eb create genotype`
3. Configure environment variables in the AWS console under "Configuration/Software Configuration/" for the new environment.
    - `SQLALCHEMY_DATABASE_URI`: the connection URI for the database you are using
    - `GENOTYPE_NO_SAVE`: don't bother storing uploaded Excel books since EB doesn't provide persistent storage. Just set it to "yes".
4. Install `genotype` locally and using the same connection URI run: `genotype --database [DB_URI] init <path to SNPs>`

## License
MIT. See the [LICENSE](LICENSE) file for more details.



[readthedocs-url]: https://readthedocs.org/projects/genotype/?badge=latest
[readthedocs-img]: https://readthedocs.org/projects/genotype/badge/?version=latest

[travis-url]: https://travis-ci.org/Clinical-Genomics/genotype
[travis-img]: https://img.shields.io/travis/Clinical-Genomics/genotype.svg?style=flat
