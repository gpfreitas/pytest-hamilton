

# Pytest Plugin "Hello World" Example
This is a complete, minimal example of a standalone pytest plugin. It adds a custom command-line flag (`--name`) and a fixture (`hello`) that uses it.
## 1. Directory StructureCreate a folder named `pytest-hello` and place these two files inside it:

```text
pytest-hello/
├── pyproject.toml      # Registration & Metadata
└── pytest_hello.py     # Plugin Logic (Hooks & Fixtures)
```

## 2. The Logic (pytest_hello.py)

This file defines how the plugin interacts with pytest. It uses a hook to add a CLI option and a fixture to provide data to tests. [1] 

```
import pytest
def pytest_addoption(parser):
    """
    A pytest HOOK that adds a custom command line option.
    Docs: https://docs.pytest.org
    """
    group = parser.getgroup("helloworld")
    group.addoption(
        "--name",
        action="store",
        default="World",
        help="The name to use in the hello fixture"
    )

@pytest.fixturedef hello(request):
    """
    A FIXTURE that reads the custom command line option.
    """
    name = request.config.getoption("name")
    return f"Hello, {name}!"
```

## 3. The Registration (pyproject.toml) [2] 

This file tells Python (and pytest) that this package exists. The [project.entry-points.pytest11] section is the "magic" that makes pytest find the plugin automatically when it is installed. [3] 

```
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "pytest-hello"
version = "0.1.0"
dependencies = ["pytest>=7.0.0"]

[project.entry-points.pytest11]
hello = "pytest_hello"
```

## 4. How to Install and Test

To see your plugin in action, follow these steps in your terminal:

### Step A: Install the plugin locally [4] 

Navigate into the pytest-hello directory and run:

```
pip install -e .
```

### Step B: Create a test file

Create a file named `test_plugin.py` anywhere on your machine:

```
def test_my_plugin(hello):
    print(f"\nPlugin says: {hello}")
    assert "Hello" in hello
```

### Step C: Run pytest

Run the test normally, or pass your new custom flag:

## Default behavior

pytest -s test_plugin.py

## Using the custom flag

pytest -s --name=Alice test_plugin.py

------------------------------
Key Concepts for Beginners

   1. Hooks: Functions starting with pytest_ are "hooks." Pytest calls them at specific times (like during startup or after a test fails).
   2. Entry Points: Pytest looks specifically for the pytest11 entry point in your pyproject.toml. Without this, the plugin won't be "discovered" automatically.
   3. Local vs. Global: If you don't want to make a package, you can put the code from pytest_hello.py into a file named conftest.py in your test folder. Pytest treats conftest.py as a local, automatic plugin. [5, 6, 7, 8, 9] 



[1] [https://pythontest.com](https://pythontest.com/testandcode/episodes/pytest-plugins/)
[2] [https://www.bitecode.dev](https://www.bitecode.dev/p/testing-with-python-part-3-pytest)
[3] [https://www.druva.com](https://www.druva.com/blog/mastering-pytest-creating-custom-plugins#:~:text=Here%2C%20entry_points%20is%20a%20parameter%20used%20to,and%20use%20your%20plugin%20when%20it%27s%20installed.)
[4] [https://git.ifas.rwth-aachen.de](https://git.ifas.rwth-aachen.de/templates/ifas-python-template/-/blob/master/README.md#:~:text=Unit%20Testing%20The%20unit%20tests%20are%20performed,is%20necessary%20to%20install%20the%20project%20locally.)
[5] [https://www.codementor.io](https://www.codementor.io/@adammertz/writing-a-simple-pytest-hook-zc5wvoj5t#:~:text=Writing%20a%20simple%20Pytest%20hook%20Pytest%20is,all%20be%20references%20via%20the%20API%20docs.)
[6] [https://docs.pytest.org](https://docs.pytest.org/en/stable/how-to/writing_plugins.html#:~:text=pytest%20looks%20up%20the%20pytest11%20entrypoint%20to,defining%20it%20in%20your%20pyproject.%20toml%20file.)
[7] [https://www.datacamp.com](https://www.datacamp.com/tutorial/pyright#:~:text=I%20use%20the%20global%20installation%20for%20quick,one%2Doffs%20without%20adding%20to%20your%20global%20packages.)
[8] [https://docs.pytest.org](https://docs.pytest.org/en/stable/reference/plugin_list.html#:~:text=Pytest%20Plugin%20List%20%C2%B6%20name%20summary%20last_release,create%20test%20doubles%20Oct%2016%2C%202022%20pytest%2Dcamel%2Dcollect)
[9] [https://docs.pytest.org](https://docs.pytest.org/en/stable/how-to/usage.html)

