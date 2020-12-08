## Setup

CALC is primarily a [Django] project.

CALC uses [Docker][] and [Docker Compose][] to make setting up a development environment easier.

If you are unfamiliar with Docker or Docker Compose, read their docs as well as the [18F Docker guide][].

### Prerequisites

First, install [Docker](https://docs.docker.com/install/), as well as [Docker Compose](https://docs.docker.com/compose/install/) if it's not included in your system's Docker installation.

Check that both are installed by running:

```sh
docker -v
docker-compose -v
```

which will output the version numbers of each tool if the installation worked as expected.

### Configuration

During development, the project reads environment variables from a `.env` file, which
you can create by running:

```sh
cp .env.sample .env
```

Edit the `.env` file to your tastes. You shouldn't need to change much here; but if you'd like to see the available options, see [Environment variables](environment.md) for details on configuration.

You'll also need to symlink `docker-compose.local.yml` to `docker-compose.override.yml`. On Linux and OS X, this can be done via:

```sh
ln -sf docker-compose.local.yml docker-compose.override.yml
```

However, if you're on Windows, use:

```sh
mklink docker-compose.override.yml docker-compose.local.yml
```

If that doesn't work, you will have to copy the file instead of symlinking it.

### Installing or updating dependencies

Run

```sh
./docker-update.sh
```

This script will install/update all Python and Node dependencies, as well as apply any necessary database migrations.

You'll also want to run this script whenever you update your local repository via commands like `git pull` or `git checkout`.

### Loading data (optional)

You can optionally load some data into your dockerized database with:

```sh
docker-compose run app python manage.py load_api_data --end-page=5
```

This will load about 1000 rates from the production CALC instance into your local CALC instance.  You can increase the value passed to the `--end-page` argument to increase the amount of data that is copied over, or you can leave out the argument entirely to transfer all of CALC's data, but it may take some time.

### Starting the development server

Now you can start the development server:

```sh
docker-compose up
```

This will start up all required servers in containers and output their log information to `stdout`. It might take a couple minutes for all the front end assets to be built, but once you see a message that looks something like this:

```sh
gulp_1          | [19:15:54] -----------------------------------------
gulp_1          | [19:15:54] Visit your CALC at: http://localhost:8000
gulp_1          | [19:15:54] -----------------------------------------
```

You can visit http://localhost:8000/ to see your local CALC instance.

### More information

For more information on interacting with CALC's dockerized development environment, see the [Using Docker](docker.md) section of our docs.

[Django]: https://www.djangoproject.com/
[18F Docker guide]: https://github.com/18F/development-guide/blob/master/project_setup/docker/README.md
[Docker]: https://www.docker.com/
[Docker Compose]: https://docs.docker.com/compose/
[docker-machine-cloud]: https://docs.docker.com/machine/get-started-cloud/
