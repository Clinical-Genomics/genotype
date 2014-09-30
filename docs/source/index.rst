.. taboo documentation master file, created by
   sphinx-quickstart on Mon Sep 29 02:32:16 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Taboo
=======
Taboo is simple genotype comparison tool. It can handle multiple VCF files with multiple samples. Taboo is extendible to allow for plugins that customize the output of the comparison.

Taboo is mainly a command line utility. I might specify a Python API in the future but for now only the CLI will stay reliably stable post release 1.0.


Motivation
------------
Comparing variants between samples and VCF files is a common task. However, I haven't found *the* VCF comparison tool.

Program that are `often recommended <https://www.biostars.org/p/59591/>`_ include *vcf-compare*, *vcfgtcompare*, *BEDTools*, and *GATK*. For convenience reasons I like to be independent of Java depedencies for doing simple stuff like this. I also think the output from VCFTools (vcf-compare) is confusing.

Therefore I decided to develop my own **simple** genotype comparison tools in Python. I will value transparency and easy of use.


Installation
--------------
Taboo is not currently on *pip* but I intend on registering it once I work out more specifically the scope of the package.

For now, install as:

.. code-block:: console

	$ pip install https://github.com/Clinical-Genomics/taboo/zipball/master

Dependencies
~~~~~~~~~~~~~

* VCFTools. I know, hypocrisy right? In my defence, I only use it to easily sort VCF files.

* PyVCF. I generally think the module is a little over-designed with custom classes galore. However, there are enough benefits and conveniences like "walk_together" included to not use it.


Usage
------
The main objective of the package is comparison of genotypes between samples. The package handles multi-sample VCFs as well as multiple VCFs.

The important thing is that they are sorted using the same key. The simplest way to do so is to use "vcf-sort" from the VCFTools library:

.. code-block:: console

	$ vcf-sort /path/to/sample.vcf > /path/to/sample.sorted.vcf

To compare each genotype across all samples in all files, issue the command:

.. code-block:: console

	$ ls
	sample1.sorted.vcf sample2.sorted.vcf
	$ taboo compare sample*.sorted.vcf > results.txt

You can then continue filtering the output as you wish. It might be interesting to:

.. code-block:: console

	$ grep discordant results.txt

What does it compare?
~~~~~~~~~~~~~~~~~~~~~~
Each comparison module is built as a plugin that can be turned on/off and additional plugins can be installed using *pip*. The builtin comparators include:

	- quality: the quality of the genotype call (GQ)

Clinical Genomics
~~~~~~~~~~~~~~~~~~~
Initially, some parts of the package will deal with tasks more or less specific to Clinical Genomics.

	1. A MAF Excel report can be converted to a VCF file. This enables standardized comparison of 2 VCFs.

	2. Trimming of large VCF files down to the variants of interest. This will use RS numbers as identifiers but could be expanded to chromosome, start, ref(, and alt).

	3. Splitting of multi-sample VCFs into multiple single-sample VCFs. This feature might not be needed in the future.


Roadmap & Wish list
---------------------

	- General approach to comparing genotypes across samples

		- Pipeable interface to filter results step-by-step

	- Phase out functionality specific to Clinical Genomics

	- Handle comparison of subsets of samples in multi-sample VCFs

	- Introduce logging into the module to include extra information (verbose mode)


Contributing
--------------
There's no point in contributing at the moment. I need to first make sure I have a grasp on the scope of the project.

Overview
~~~~~~~~~~~

	1. Parse/read VCF(s)
	2. Pass a list of genotype calls for each variant to a set of plugins
	  - each plugin gets a list of genotypes for a variant and returns some serializable data
	  - each plugin output is concatenated and builds the overall output
	  - examples: identical/different, hetero/homozygote (per sample), quality per sample etc.
	  - Taboo will be opinionated about how to serialize output data to make the tool more flexible (the serializer could also be a plugin...)
	3. Print each line to the console stdout

Building plugins
~~~~~~~~~~~~~~~~~
I will implement the plugins as entry points so that someone eles can write a plugin that will be easily installed to extend the output. Think like Flask Blueprints if that helps.

Further details to come at a later stage.
