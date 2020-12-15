# NOTE:
#
# This file should be appended to Dockerfile to create Dockerfile.cloud.
# To "rebuild" Dockerfile.cloud, run:
#
#   cat Dockerfile Dockerfile.cloud-extras > Dockerfile.cloud

# The following lines set up our container for being run in a
# cloud environment, where folder sharing is disabled. They're
# irrelevant for a local development environment, where the /calc
# directory is mounted via folder share.

COPY . /calc/
