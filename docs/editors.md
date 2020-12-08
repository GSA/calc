## Editor integration

It's often convenient to install editor integrations for
CALC's languages to provide useful functionality like autocompletion
and instant feedback from CALC's [linters and type checkers](linting.md).
However, doing this often requires setting up CALC's JavaScript and/or
Python environment on the host system, outside of Docker.

### JavaScript

Setting up CALC's JavaScript environment can be accomplished by installing
[NodeJS][] and [yarn][] and running the following on your local machine:

```
yarn install --ignore-engines
```

At this point, you should be able to install any editor integrations for
JavaScript-related code, and they should work as expected.

### Python

Setting up CALC's Python environment can be accomplished by installing
the version of Python 3 specified in [runtime.txt](../runtime.txt). You
can then install virtualenv:

```
python3 -m pip install virtualenv
```

Then you can create a virtualenv in the `venv` directory:

```
python3 -m venv venv
```

You can now activate the virtualenv; on OSX/Linux, this is done via:

```
source venv/bin/activate
```

Or if you're on Windows, use:

```
venv\Scripts\activate
```

Now you can install development requirements:

```
pip install -r requirements-dev.txt
```

At this point you can run your text editor, and any Python-related
editor integrations you've installed should work as expected.

[NodeJS]: http://nodejs.org/
[yarn]: https://yarnpkg.com/
