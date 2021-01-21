================================
Deploying to Cloud Foundry
================================

**This section is only of interest to 18F team members.**

In general, you should not need to do any manual deployments of CALC because we use automated deploys from CircleCI for both our development and production deployed instances. See our [Release process](release.md) docs for how we tag and deploy new production releases.

### Prerequisites

Download the Cloud Foundry CLI according to the [cloud.gov instructions][].
Make sure you are using at least version v6.17.1, otherwise pushing
multiple apps at once might not work.

[cloud.gov instructions]: https://docs.cloud.gov/getting-started/setup/

You will also need to install the [`autopilot`](https://github.com/contraband/autopilot)
plugin for Cloud Foundry, which is used for zero-downtime deploys.
You can install via
`cf install-plugin autopilot -f -r CF-Community`.

### Logging in to cloud.gov from the terminal

CALC is deployed to the GovCloud instance of cloud.gov. You will need to login
to via the GovCloud api of cloud.gov:
`cf login -a api.fr.cloud.gov --sso`

Then target the org and space you want to work with. For example, if you wanted to work with the `dev` space:
`cf target -o fas-calc -s dev`

Manifest files, which contain import deploy configuration settings, are located
in the [manifests](../manifests/) directory of this project.

### Python dependencies in deployments 

Note that this project has two requirements files:

* `requirements.txt` for production dependencies
* `requirements-dev.txt` for development and testing dependencies

During local development and continuous integration testing,
`pip install -r requirements-dev.txt` is used, which installs both
development and production dependencies. During deployments, the Cloud
Foundry python buildpack uses only `requirements.txt` by default, so
only production dependencies will be installed.

### Cloud Foundry structure

* cloud.gov environment: `GovCloud`
* Organization: `fas-calc`
* Spaces: `dev`, `prod`
* Apps:
  * `dev` space:
   - `calc-dev`
   - `calc-rqworker`
   - `calc-rqscheduler`

  * `prod` space:
   - `calc-prod`
   - `calc-rqworker`
   - `calc-rqscheduler`
   - `calc-maintenance`

* Routes:
  * calc-dev.app.cloud.gov -> `dev` space, `calc-dev` app
  * calc-prod.app.cloud.gov -> `prod` space, `calc-prod` app
  * calc.gsa.gov -> `prod` space, `calc-prod` app
    or the maintenance page app, `calc-maintenance`

### Services

#### Service Account Service

CALC uses cloud.gov [service account services][service account] to provision cloud.gov credentials for automated deployments from CircleCI.

Each cloud.gov space that CALC uses has an associated service account with a name of the form `calc-<SPACE NAME>-deployer-circle`.

For information on how to create or rotate cloud.gov credentials from a service account service refer to the [cloud.gov docs][service account].

#### Identity Provider Service

CALC uses an [Identity Provider Service][IPS] to register with cloud.gov's User Account and Authentication (UAA)
server (see [Auth](auth.md) for more details).

A service and associated service key are needed for each cloud.gov space.
As an example, for the `dev` space, the commands to create the service and get its keys are:

```sh
cf create-service cloud-gov-identity-provider oauth-client calc-dev-uaa-client
cf create-service-key calc-dev-uaa-client calc-dev-uaa-client-service-key -c '{"redirect_uri": ["https://calc-dev.app.cloud.gov"]}'
cf service-key calc-dev-uaa-client calc-dev-uaa-client-service-key
```

The `cf service-key` command above will output a username and password pair that corresponds to the `UAA_CLIENT_ID` and `UAA_CLIENT_SECRET`
environment variables that will be used when setting up CALC's User Provided Service, described in the next section.

See the [Identity Provider Service docs][IPS] for up-to-date information on its use.

#### User Provided Service (UPS)

For cloud.gov deployments, this project makes use of a [User Provided Service (UPS)][UPS] to get its configuration
variables, instead of using the local environment.
You will need to create a UPS called `calc-env`, provide 'credentials' to it, and link it to the
application instance. This will need to be done for every Cloud Foundry `space`.

First, create a JSON file (e.g. `credentials-dev.json`) with all the configuration values specified as per the
[Environment variables](environment.md). **DO NOT COMMIT THIS FILE.**

```json
{
  "SECRET_KEY": "my secret key",
  "...": "other environment variables"
}
```

Then enter the following commands (filling in the main application instance name
for `<APP_INSTANCE>`) to create the user-provided service:

```sh
cf cups calc-env -p credentials-dev.json
cf bind-service <APP_INSTANCE> calc-env
cf restage <APP_INSTANCE>
```

You can update the user-provided service with the following commands:

```sh
cf uups calc-env -p credentials-dev.json
cf restage calc-dev
```

#### Database service

CALC uses PostgreSQL for its database.

```sh
cf create-service aws-rds <SERVICE_PLAN> calc-db
cf bind-service <APP_INSTANCE> calc-db
```

#### Redis service

CALC uses Redis along with [rq](http://python-rq.org/) for scheduling and processing
asynchronous tasks.

For production, use the `standard-ha` (high availability) plan. For non-production uses, use the `standard` plan.

```sh
cf create-service redis32 standard-ha calc-redis32
cf bind-service <APP_INSTANCE> calc-redis32
```

For more information on cloud.gov's Redis service, see its [docs](https://cloud.gov/docs/services/redis/).

### Deployed instances


The **development** instance of CALC ([https://calc-dev.app.cloud.gov](https://calc-dev.app.cloud.gov)) is deployed automatically when changes are merged into the `develop` branch.

The **production** instance of CALC, whose main app resides at [https://calc.gsa.gov](https://calc.gsa.gov), is deployed automatically from CircleCI when commits are pushed to the `master` branch.

Check out the `deploy` sections of the [CircleCI config](../.circleci/config.yml) for details and settings for automated deploys.

### Maintenance page app

We have a very simple maintenance page application that uses the CloudFoundry staticfiles
buildpack. This is a helpful application to use during periods of planned downtime, such as during a large database migration.

The maintenance page app code is in the [maintenance_page](../maintenance_page/) subdirectory.

If `calc-maintenance` is not running or has not been deployed yet:

```sh
cd maintenance_page
cf push
```

Once `calc-maintenance` is running:

```sh
cf map-route calc-maintenance calc.gsa.gov
cf unmap-route calc-prod
```

And then deploy the production app:

```sh
cf push -f manifests/manifest-prod.yml
```

One the deploy is successful:

```sh
cf map-route calc-prod calc.gsa.gov
cf unmap-route calc-maintenance
```

### Logs

Logs in cloud.gov-deployed applications are generally viewable by running
`cf logs <APP_NAME> --recent`.

Note that the web application and the worker applications have separate logs, so you will need to look at each individually.

If more detailed log analysis is needed, Kibana can be used to generate
a variety of visualizations and dashboards at
[https://logs.fr.cloud.gov](https://logs.fr.cloud.gov). For more details,
see the
[cloud.gov Logs documentation](https://cloud.gov/docs/apps/logs/).

### Initial superuser

After the initial setup of `calc-db` and a production app, you will need to
create a superuser account, after which you'll be able to login to the
Django admin panel to add additional user accounts. The easiest way to create
the initial superuser is to use `cf ssh` to get to the remote host
and run `python manage.py createsuperuser`. You'll need to do some environment
setup on the remote host, as described at [Cloud Foundry's SSH docs](https://docs.cloudfoundry.org/devguide/deploy-apps/ssh-apps.html#ssh-env):

```sh
export HOME=/path/to/app
export TMPDIR=/path/to/tmp
cd /path/to/app
source /path/to/app/.profile.d/python.sh
```

### Testing production deployments

Because reverse proxies like CloudFront can be misconfigured to prevent CALC from working properly, we've built a test suite that can be used to remotely test a production deployment of CALC. To use it, run:

```sh
docker-compose run app py.test production_tests
```

By default, the suite tests against `calc.gsa.gov`. If you'd like to test it against a different URL, you can do so with the `--origin` command-line option.

[service account]: https://cloud.gov/docs/services/cloud-gov-service-account/
[UPS]: https://docs.cloudfoundry.org/devguide/services/user-provided.html
[IPS]: https://cloud.gov/docs/services/cloud-gov-identity-provider/
[`README.md`]: https://github.com/18F/calc#readme
