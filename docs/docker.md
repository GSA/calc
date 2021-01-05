## Using Docker

<div class="admonition tip">
<p class="admonition-title">Tip</p>

If you're ever having problems because `docker-compose up` explodes in an unfriendly way, it's quite likely that `./docker-update.sh` will fix it.

</div>

For setup instructions on using Docker and Docker Compose for CALC's development environment, see our [Setup](setup.md) guide.

### Updating the containers

Whenever you update your repository via e.g. `git pull` or
`git checkout`, you should update your containers by running:

```
./docker-update.sh
```

### Starting over

If your Docker setup appears to be in an irredeemable state
and `./docker-update.sh` doesn't fix it--or
if you just want to free up extra disk space used up by
CALC--you can destroy everything by running:

```
docker-compose down -v
```

Note that this will delete all the data in your CALC
instance's database.

At this point you can re-run `./docker-update.sh` to set
everything up again.

### Accessing the app container

Command-line snippets in this developer documentation often start
with `docker-compose run app`, which gets repetitive. One
way to avoid this is to run:

```sh
docker-compose run app bash
```

This will run an interactive bash session inside the main app container.
In this container, the `/calc` directory is mapped to the root of
the repository on your host; you can run any command, like `manage.py`
or `py.test`, from there.

### A `manage.py` shortcut

Note that if you don't have Django installed on your host system, you
can just run `python manage.py` directly from outside the container--the
`manage.py` script has been modified to run itself in a Docker container
if it detects that Django isn't installed.

### Custom dependencies

Feel free to install custom Python dependencies, e.g. your favorite
debugging library, in your container via
`docker-compose run app pip install`.

For custom node dependencies, you can use
`docker-compose run app yarn add`. However, note that this will
modify your `package.json` and `yarn.lock`, which you probably
won't want to commit to git. You'll have to either make sure
not to commit those files, or undo the installation once
you're finished using the package with
`docker-compose run app yarn remove`.

### Debugging Python

CALC's `requirements-dev.txt` file will install [`ipdb`][].

To drop into an interactive debugging section:

1. In a _separate terminal_ from the one that's already
   running `docker-compose up`, run:

   ```
   docker attach calc_app_1
   ```

   We'll call this the "debugging terminal".

2. Add `import ipdb; ipdb.set_trace()` at whatever line you want
   to invoke the debugger at (this is a standard Python convention).

3. Trigger a code path that executes the line you just added.
   You should see the debugger start up in your debugging terminal.
   (You'll also see it start up in the `docker-compose up` terminal,
   but you can ignore that.)

4. Debug as you normally would. (If you're unfamiliar with the
   debugger, here's a [handy list of `ipdb` commands][ipdb_intro].)

5. Once you're done, **do not press `Ctrl + C`**.  Instead,
   type `continue` into the debugger, and then press `Ctrl + P`
   followed by `Ctrl + Q` to detach the debugger terminal
   from the app container and return to the shell.

[`ipdb`]: https://pypi.python.org/pypi/ipdb
[ipdb_intro]: https://www.safaribooksonline.com/blog/2014/11/18/intro-python-debugger/

### Changing the exposed port

If you don't want to serve your app on port 8000, you can change
the value of `DOCKER_EXPOSED_PORT` in your `.env` file.

### Deploying to cloud environments

The Docker setup can also be used to deploy to cloud environments.

To do this, you'll first need to
[configure Docker Machine for the cloud][docker-machine-cloud],
which involves provisioning a host on a cloud provider and setting up
your local environment to make Docker's command-line tools use that
host. For example, to do this on Amazon EC2, you might use:

```
docker-machine create aws16 --driver=amazonec2 --amazonec2-instance-type=t2.large
```

Docker Machine's cloud drivers intentionally don't support
folder sharing, which means that you can't just edit a file on
your local system and see the changes instantly on the remote host.
Instead, your app's source code is part of the container image. To
facilitate this, you'll need to create a new Dockerfile that augments
your existing one:

```
cat Dockerfile Dockerfile.cloud-extras > Dockerfile.cloud
```

Also, unlike local development, cloud deploys don't support an
`.env` file. So you'll want to create a custom
`docker-compose.override.yml` file that defines the app's
environment variables, and also points to the alternate Dockerfile:

```
cp docker-compose.cloud.yml docker-compose.override.yml
```

You can edit this file to add or change environment variables as needed.

You'll also want to tell Docker Compose what port to listen on,
which can be done in the terminal by running
`export DOCKER_EXPOSED_PORT=8000`.

At this point, you can use Docker's command-line tools and CALC's
Docker-related scripts, and your actions will take effect on the remote
host instead of your local machine.

So, you should first run `./docker-update.sh` to set everything up,
followed by `docker-compose up`. Now you should have a server
running in the cloud!

**Note:** A script, [create-aws-instance.sh](../create-aws-instance.sh),
actually automates all of this for you, but it's coupled to Amazon
Web Services (AWS). You're welcome to use it directly or edit it to
your own needs. Run it without any arguments for help.

**Note:** As mentioned earlier, your app's source code is part of
the container image. This means that every time you make a source code
change, you will need to re-run `./docker-update.sh`.

[docker-machine-cloud]: https://docs.docker.com/machine/get-started-cloud/
