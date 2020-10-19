# Deployment guide
This includes instructions for deploying Genotype in the Clinical Genomics :hospital: setting. General instructions for deployment is in the [development guide][development-guide]

## Branch model

Genotype if following the [GitHub flow][gh-flow] branching model which means that every time a PR is merged to master a new release is created.

## Requirements

- `bumpversion`, install with `pip install bumpversion`

## Steps

1. Check in the PR if the change is a minor, mayor or patch: ![Version][pr-version]
1. Make sure you are on `master` (`git checkout master`) and bump version according to step 1, example: `bumpversion minor`
1. Push the commit: `git push`
1. Push the tag: `git push --tags`
### hasta
1. First deploy on stage so log into hasta and run:
    - `us`
    - `cg deploy genotype`
1. Deploy in productions by running the following commands:
    - `down`
    - `up`
    - `cg deploy genotype`
### clinical-db
1. First deploy on stage so log into hasta and run:
    - `us`
    - `bash /home/proj/production/servers/resources/clinical-db.scilifelab.se/update-genotype-stage.sh master`
1. Deploy in productions by running the following commands:
    - `down`
    - `up`
    - `bash /home/proj/production/servers/resources/clinical-db.scilifelab.se/update-genotype-prod.sh`
1. Take a screen shot that includes the name of the environment and publish it as a comment on the PR: ![Deployed][confirm-deploy]
1. Great job :whale2:


[pr-version]: docs/img/version.png
[confirm-deploy]: docs/img/confirm_deploy.png
[development-guide]: http://www.clinicalgenomics.se/development/publish/prod/
[gh-flow]: http://www.clinicalgenomics.se/development/dev/models/#rolling-release-github-flow
