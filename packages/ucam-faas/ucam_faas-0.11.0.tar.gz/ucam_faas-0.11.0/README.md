# UCam FaaS Library

This project contains a support library and base Docker image to be used to
create Function as a Service (FaaS) applications intended to be deployed to a
GCP cloud run environment.

It is highly opinionated and non-configurable by design.

## Usage

Install the library via pip:

```console
pip install ucam-faas
```

Install the library with testing support:

```console
pip install ucam-faas[testing]
```

The library provides a decorator to create a runnable application from a single
function. The function must accept a dictionary as an argument, and return
either a string or a dictionary as a response:

```python
# main.py
from ucam_faas import event_handler


@event_handler
def say_hello(event):
    return "hello!"
```

This can then be run as a FaaS app using:

```console
ucam-faas --debug --target say_hello
```

### Testing FaaS Functions

To unit test FaaS functions there are two available approaches. Firstly, the
unwrapped version of the function can be directly accessed. This is recommended
as the primary way to test FaaS functions and requires no additional
configuration:

```python
# test_my_event_handler.py
from main import say_hello

def test_say_hello():
    assert say_hello.__wrapped__({"event_key": "event_value"}) == "hello!"
```

The original function version is made available through the `__wrapped__`
variable.

Alternatively, if required, a support testing client can be used to instantiate
a version of the web application running the function. To do this the extra
"testing" must also be installed:

```shell
pip install ucam-faas[testing]
```

Then tests can register the provided `pytest` fixture and use it in tests:

```python
# test_my_event_handler.py
pytest_plugins = ["ucam_faas.testing"]

def test_say_hello(event_app_client):
    # Provide the target function for the test webapp
    eac = event_app_client("say_hello")
    response = eac.get("/")
    assert response.status_code == 200
```

Note that with this approach it is not necessary to import the function under
test, it is discovered and imported during the test webapp setup.

### Example

An example application and example tests can be found in this repository in the
`example` directory.

Note that the example dockerfile is part of the `Dockerfile` in the root and
therefore needs to be run from the root of the repository:

```console
docker build --target example .
```

## Local Development

Install poetry via:

```console
pipx install poetry
pipx inject poetry poethepoet[poetry_plugin]
```

Install dependencies via:

```console
poetry install
```

Build the library via:

```console
poetry build
```

Run the example application via:

```console
poetry poe example
```

Run the tests via:

```console
poetry poe tox
```

Note that the tests are found under the example directory, there are *currently*
no tests in the root library as the code is predominantly configuration and
setup, and example testing has been deemed sufficient.

### Dependencies

> **IMPORTANT:** if you add a new dependency to the application as described
> below you will need to run `docker compose build` or add `--build` to the
> `docker compose run` and/or `docker compose up` command at least once for
> changes to take effect when running code inside containers. The poe tasks have
> already got `--build` appended to the command line.

To add a new dependency *for the application itself*:

```console
poetry add {dependency}
```

To add a new development-time dependency *used only when the application is
running locally in development or in testing*:

```console
poetry add -G dev {dependency}
```

To remove a dependency which is no longer needed:

```console
poetry remove {dependency}
```

## CI configuration

The project is configured with Gitlab AutoDevOps via Gitlab CI using the .gitlab-ci.yml file.
