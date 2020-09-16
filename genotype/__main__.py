"""
genotype.__main__
~~~~~~~~~~~~~~~~~~~~~
                             __
   ____   ____   ____   _____/  |_ ___.__.______   ____
  / ___\_/ __ \ /    \ /  _ \   __<   |  |\____ \_/ __ \
 / /_/  >  ___/|   |  (  <_> )  |  \___  ||  |_> >  ___/
 \___  / \___  >___|  /\____/|__|  / ____||   __/ \___  >
/_____/      \/     \/             \/     |__|        \/

The main entry point for the command line interface.

Invoke as ``genotype`` (if installed)
or ``python -m genotype`` (no install required).
"""
import sys

from genotype.cli.base_cmd import root

if __name__ == "__main__":
    # exit using whatever exit code the CLI returned
    sys.exit(root())
