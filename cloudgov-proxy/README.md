To deploy our CALC price list analysis branch, we set up an instance
of CALC on an AWS sandbox (because it's easy and doesn't eat up
cloud.gov usage quotas) and then configure a cloud.gov-based reverse
proxy to point at it, which gives us a memorable domain name and
HTTPS.

However, this needs to be done at the beginning of every week, because
that's how long AWS sandbox instances last.

The following instructions document how to accomplish this.

## Prerequisites

You will need the following:

* Write access to the Cloud Foundry organization, space, and app
  defined in [`.env.cloudgov-proxy`](.env.cloudgov-proxy).

* Write access to the Docker Hub organization and repo
  defined in [`.env.cloudgov-proxy`](.env.cloudgov-proxy).

* AWS sandbox access outlined in the
  [18F Before You Ship](https://pages.18f.gov/before-you-ship/infrastructure/sandbox/)
  guide.

You may also want to familiarize yourself with deploying CALC to
cloud environments via Docker, as described in the
[CALC Docker guide](../docs/docker.md).

## Deployment

These instructions assume you are going to create a docker machine called
`aws30`, substitute it for your own machine name as needed.

1. Merge `develop` into this branch if you haven't already, and
   make sure the tests pass.

2. From the root of the repository, run:

   ```
   ./create-aws-instance.sh aws30
   ```

   Now get some coffee because this will take a while to complete.

3. Modify the created `docker-compose.aws30.yml` to include the following
   `environment` entries under the `app` service:

   ```yaml
      - DEBUG_HTTPS=yup
      - 'NON_PROD_INSTANCE_NAME=<a href="https://github.com/18F/calc/pull/997">price list analysis</a>'
   ```

4. Run the following at the terminal:

   ```
   source activate-aws30
   docker-compose stop
   docker-compose up -d
   ```

5. This step is optional.

   Run `echo $DOCKER_HOST_IP` and visit that IP address in your web
   browser over HTTP (not HTTPS); everything should look OK, although
   there will probably be a note at the top advising you to change
   your site configuration. Don't worry about that for now, as
   we're about to fix that.

6. Run the following at the terminal:

   ```
   cd cloudgov-proxy
   ./cloud.gov-login.sh
   ```

   This will open a browser to have you login via 2FA to cloud.gov. It
   will automatically target the proper organization and space.

7. Now, in a new terminal, run:

   ```
   ./update-site.sh aws30
   ./cloud.gov-push.sh
   ```

You're done! Next week, the `aws30` machine will be automatically
cleaned up, so you'll want to remove its references on your machine
by running the following in the root directory of your repository:

```
rm *aws30*
docker-machine rm -f aws30
```
