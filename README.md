<p align="center">
  <a href="https://github.com/Clinical-Genomics/taboo">
    <img width="240px" height="180px" src="artwork/icon.png"/>
  </a>
</p>

# Taboo [![Documentation Status][readthedocs-img]][readthedocs-url] [![Build Status][travis-img]][travis-url]
Manage SNP calling comparisons at Clinical Genomics. The package exposes a CLI and a bare bones web interface to visualize results stored in a SQLite database.

## Install

```bash
$ conda install -c bioconda pysam pyyaml sqlalchemy flask
$ pip install taboo==2.0.0-beta3
```

## Deploy to Amazon Elastic Beanstalk

This guide uses the command line utility for Elastic Beanstalk (EB): `eb`.

1. Create a new application by running `eb init` in the root of the repository.
2. Create a new environment by running `eb create taboo`
3. Configure environment variables in the AWS console under "Configuration/Software Configuration/" for the new environment.
    - `SQLALCHEMY_DATABASE_URI`: the connection URI for the database you are using
    - `TABOO_NO_SAVE`: don't bother storing uploaded Excel books since EB doesn't provide persistent storage. Just set it to "yes".
4. Install `taboo` locally and using the same connection URI run: `taboo --database [DB_URI] init <path to SNPs>`

## License
MIT. See the [LICENSE](LICENSE) file for more details.



[readthedocs-url]: https://readthedocs.org/projects/taboo/?badge=latest
[readthedocs-img]: https://readthedocs.org/projects/taboo/badge/?version=latest

[travis-url]: https://travis-ci.org/Clinical-Genomics/taboo
[travis-img]: https://img.shields.io/travis/Clinical-Genomics/taboo.svg?style=flat
