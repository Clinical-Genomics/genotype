# Taboo - genotype comparison tool

Taboo is meant to be used to compare genotypes from different assays. We send samples for genotyping before they are taken into our lab. At the end of our workflow we compare that sequence SNPs correlate with the genotyped results.

## Web server

Taboo comes with handle web interface that enables most of the features available from the command line. You can start the server by running:

```bash
$ taboo serve
```

You will need to provid config values in the config file which are passed along to the server.

## Usage

This section describes how Taboo is intended to be used by describing user flows.

### Genotype results

Results are delivered as Excel sheets with each sample being represented by a row in on the the sheets. There's genotype information for each of the SNPs as well as three predictive markers for the sex of the sample.

**TIGGER**: Excel book is delivered (from MAF)

**PROCESS**

1. Upload Excel book via web interface or to server and add via command line

    ```bash
    $ taboo load /path/to/genotype-results.xlsx
    ```

    Taboo will automatically detect the type of file and upload the results to the database for all samples. You can restrict samples by supplying the `--include-key` option which will look for a string in each of the sample ids to load.

### Sequence results

Results come in the form of BCF files and needs to be properly indexed. There's intentionally no support for regular VCFs. Taboo handles multi-sample BCFs and will load each sample.

**TRIGGER**: New BCF file generated from variant calling pipeline

**PROCESS**

1. Point Taboo in the direction of a BCF file.

    ```bash
    $ taboo load /path/to/variants.bcf
    ```

    Taboo will automatically detect the type of file based on the file extension.

### Re-loading data

Taboo has been designed to allow reload of data without causing problems. Sample records will be created when needed. However, there are cases when samples are genotyped/sequenced multiple times. The way that Taboo deals with this is to overwrite the old data and place an automated comment in the sample record. This happens automatically based on the sample id.

### Add sex information

Taboo will also keep track of sex determinations from different analyses. When you check a sample it will take this into consideration and fail a sample where sex is reported differently from the various assays.

Sex is automatically parsed from the Excel sheet from genotyping. In addition you need to add information about the expected sex (sample leve) and the sex determined through sequencing. There's many ways to do it but Taboo only keeps track of one sex per analysis.

Adding the expected sex (male) for the sample:

```bash
$ taboo add-sex --sample male ADM12344A2
```

Adding the predicted sex (female) from sequencing:

```bash
$ taboo add-sex --analysis sequence female ADM12344A2
```

### Checking samples

Taboo checks samples for issues and marks them as either "pass" or "fail". It has three points of failure:

1. Too many no-calls from genotyping: this could indicate a sample contamination
2. Different sex annotated between: expected/genotype/sequence
3. Too many mismatches/too few matches between genotype/sequence SNPs

The cutoffs for 1 and 3 are configurable through the config file. There's a handy command which will let you run the check for all sample that have all relevant information uploaded and haven't already been marked as "pass" or "fail".

### Clearing up issues

When a sample has been marked as "fail", it's up to the user to lanch an investigation into why the issue has occured. When things are cleared up you can manually change the flag to "pass". You are required to write a comment explaining why.

You can also mark a sample as 'cancelled'. This is useful is the sample was sent for genotyping before it e.g. failed in library preparation or sequencing. It will in most cases be handled as a passing sample or ignored. You can of course also remove the sample but it you reload the results it will appear again without a proper trace back.
