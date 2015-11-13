# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [0.4.0] - 2015-11-13
### Added
- use logging module in CLI
- store sex prediction from excel report in database
- force option for re-uploading existing samples

### Changed
- Failed uploads are only skipped (upload)
- List samples from database without ids
- "experiment" now included in "show" output

## [0.3.1] - 2015-09-25
### Fixed
- Support latest `vcf_parser`

## [0.3.0] - 2015-09-08
### Changed
- Require a RS reference for matching
- Remove dependencies

## [0.2.0] - 2015-06-26
### Changed
- Change ``Sample.origin`` to ``Sample.experiment``

### Added
- Add ``Sample.source``
- Update interface accordingly

## [0.0.1] - 2014-12-09
First draft release. Everything is new.
