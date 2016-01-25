<p align="center">
  <a href="https://github.com/Clinical-Genomics/taboo">
    <img width="240px" height="180px" src="artwork/icon.png"/>
  </a>
</p>

# Taboo [![Documentation Status][readthedocs-img]][readthedocs-url] [![Build Status][travis-img]][travis-url]
Manage SNP calling comparisons at Clinical Genomics. The package exposes a CLI and a bare bones web interface to visualize results stored in a SQLite database.

## Install

```bash
$ git clone https://github.com/Clinical-Genomics/taboo && cd taboo
$ pip install --editable .
```

## CLI interface
For automation you interact with Taboo using either the command line interface or the Python API. I will focus on documenting the CLI for now.

### Base command: `taboo`
Some options work across all subcommands in Taboo. Especially important is the "config" command. By pointing to a config, you will be able to set important defaults that will enable Taboo to automate a lot of tedious boilerplate for you. Here is an [example config file](https://github.com/Clinical-Genomics/taboo/blob/master/tests/config/test.yaml).

- `--config`: load a Taboo config file (YAML)

```bash
$ taboo --config /path/to/config.yaml [subcommand]
```

### Initial setup: `init`
This request will setup a new database with empty tables.

- `--reset`: will reset an existing database

```bash
$ taboo init
```

### Load results: `load`
This command lets you load results from sequencing (`.vcf`) and MAF genotyping (`.xlsx`). It works on a per analysis/sample level which means that you can restart an upload and only the missing samples will be added the second time.

- `--include-key`: string to look for in sample id to determine which rows to include (Excel)
- `--force`: overwrite existing analyses

```bash
$ taboo load [INPUT_FILE]
```

### Compare results: `match`
Compare genotypes for an analysis across all alternative analyses. The result of the comparison is stored in the database.

### Show details: `show`
You can view detailed information about samples and analyses to manually inspect what the comparisons are based on. This can be useful if you detect some unexpected results.

### Start web server: `view`
Bring up a web server to visualize the database with samples in a web browser. From there you can upload results from genotyping and execute the comparison per sample. You will be able to see the status per sample as well as look at the sex determinations and whether they support the same conclusion.


## License
MIT. See the [LICENSE](LICENSE) file for more details.



[readthedocs-url]: https://readthedocs.org/projects/taboo/?badge=latest
[readthedocs-img]: https://readthedocs.org/projects/taboo/badge/?version=latest

[travis-url]: https://travis-ci.org/Clinical-Genomics/taboo
[travis-img]: https://img.shields.io/travis/Clinical-Genomics/taboo.svg?style=flat
