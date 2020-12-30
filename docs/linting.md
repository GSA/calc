## Linting and strong typing

CALC uses a number of linters to maintain the style and hygiene of its
codebase, along with optional tools that provide type checking
functionality.

Note that all linters and type checkers must run without errors
in order for [Continuous integration](ci.md) to pass. See the
[Testing](testing.md) documentation for details on how to easily
run everything with one command.

You may also want to consider installing
[editor integrations](editors.md) for CALC's linters and type checkers.

### Linting

#### JavaScript

CALC's JavaScript code uses [eslint][] with a configuration based on
[Airbnb's JavaScript Style Guide][airbnb].  The configuration is
stored in [.eslintrc](../.eslintrc), while ignored files are
cataloged in [.eslintignore](../.eslintignore).

To run eslint on all JavaScript code, you can run:

```
docker-compose run app eslint .
```

The `.` can be replaced with the name of a file or directory to restrict
the scope of the linter. The linter will produce no output if it
finds no errors.

#### Python

CALC's Python code uses [flake8][] for general [PEP 8][] enforcement,
though we notably relax PEP 8's line length requirement.  The
configuration is located in [.flake8](../.flake8).

To run flake8 on all Python code, you can run:

```
docker-compose run app flake8 .
```

The `.` can be replaced with the name of a file or directory to restrict
the scope of the linter. The linter will produce no output if it
finds no errors.

### Type checking

#### JavaScript

Some of CALC's JavaScript source code uses [TypeScript][] to
for type-checking. This is done by adding
`// @ts-check` to the top of any JS file, and then adorning
any functions with JSDoc-style comments. See TypeScript's
documentation on [type checking JavaScript files][tsjs] for
more details.

CALC's TypeScript configuration is stored in
[tsconfig.json](../tsconfig.json).

To run TypeScript on all eligible JavaScript code, you can run:

```
docker-compose run app tsc
```

TypeScript will produce no output if it finds no errors.

#### Python

CALC's Python source code is type-checked using a fairly
lenient [mypy][] configuration.  In general, new code
is encouraged to use [Python 3 type hints][] where possible,
both to help document the code and to ensure type safety.

CALC's mypy configuration is stored in [mypy.ini](../mypy.ini).

To run mypy on all Python code, you can run:

```
docker-compose run app mypy .
```

The `.` can be replaced with the name of a file or directory to restrict
the scope of mypy. The tool will produce no output if it finds no errors.

[eslint]: https://eslint.org/
[airbnb]: https://github.com/airbnb/javascript
[flake8]: http://flake8.pycqa.org/en/latest/
[PEP 8]:https://www.python.org/dev/peps/pep-0008/
[TypeScript]: https://www.typescriptlang.org/
[tsjs]: https://github.com/Microsoft/TypeScript/wiki/Type-Checking-JavaScript-Files
[mypy]: http://mypy-lang.org/
[Python 3 type hints]: http://mypy.readthedocs.io/en/latest/cheat_sheet_py3.html
