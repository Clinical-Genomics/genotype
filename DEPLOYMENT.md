# Deployment guide
This includes instructions for deploying Genotype in the Clinical Genomics :hospital: setting. General instructions for deployment is in the [development guide][development-guide]

## Branch model

Genotype if following the [GitHub flow][gh-flow] branching model which means that every time a PR is merged to master a new release is created.

1. Select "Squash and merge" to merge branch into default branch (master/main).


2. A prompt for writing merge commit message will pop up.


3. Find the title of the pull request already pre-filled in the merge commit title, or copy and paste 
the title if not.


4. Append version increment value `( major | minor | patch )` to specify what kind of release is to be created.


5. Fill in markdown formatted changelog in merge commit comment details:

` ### Added `

` ### Changed `

` ### Fixed `

6. Review the details once again and merge the branch into master.


7. Wait for GitHub actions to process the event, bump version, create release, publish to Dockerhub and PyPi where applicable.

8. First deploy on stage so log into hasta and run:
    - `us`
    - `bash /home/proj/production/servers/resources/hasta.scilifelab.se/update-tool-stage.sh -e S_genotype -t genotype -b master`
9. Deploy in productions by running the following commands:
    - `down`
    - `up`
    - `bash /home/proj/production/servers/resources/hasta.scilifelab.se/update-genotype-prod.sh`
10. Take a screen shot that includes the name of the environment and publish it as a comment on the PR: ![Deployed][confirm-deploy]
11. Great job :whale2:


[pr-version]: docs/img/version.png
[confirm-deploy]: docs/img/confirm_deploy.png
[development-guide]: http://www.clinicalgenomics.se/development/publish/prod/
[gh-flow]: http://www.clinicalgenomics.se/development/dev/models/#rolling-release-github-flow
