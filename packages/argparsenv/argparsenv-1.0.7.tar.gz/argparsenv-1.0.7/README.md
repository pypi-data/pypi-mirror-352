# argparsenv

This project extends python's argparse module to allow for environment variable overrides of command line arguments.

The rule for environment variable overrides is as follows:

1. If the argument is provided on the command line, the environment variable is ignored.
2. If the argument is not provided on the command line, the environment variable is used if it is set.
3. If the argument is not provided on the command line and the environment variable is not set, the default value is used.
4. If the argument is environment variable is set both on the command line and in the environment, the command line value is used.

## Installation

Stable release version:

```bash
pip install argparsenv
```

Latest development version:

```bash
pip install git+https://github.com/snaeil/argparsenv
```

## Usage

This module builds on top of python's standard library
[argparse](https://docs.python.org/3/library/argparse.html).

```python
import argparsenv

env_arg_parser = ArgumentParser()
env_arg_parser.add_argument(
    "--port",
    dest="port",
    env_var="MY_APP_DB_PORT",
    default="3306",
)
```

With this ArgumentParser instance, the port argument can be set in three ways:

1. On the command line:

```bash
python my_app.py --port 3307
```

2. As an environment variable (this can also be done by using a `.env` file):

```bash
export MY_APP_DB_PORT=3307
python my_app.py
```

3. Using the default value (here `3306`):

```bash
python my_app.py
```

## Contributing

Contributions are welcome!
For feature requests, bug reports or questions, please open an issue.
For code contributions, please open a pull request.

The development environment can be set up using `nix` and `devenv`:

1. Install nix package manager: `bash <(curl -L https://nixos.org/nix/install) --no-daemon`
2. Make sure, your `~/.config/nix/nix.conf` contains the following lines:
   ```nix
   experimental-features = nix-command flakes
   ```
3. Install [`devenv`](https://devenv.sh) by running:
   ```shell
   nix profile install --accept-flake-config 'nixpkgs#devenv'
   ```
4. Install [nix-direnv](https://github.com/nix-community/nix-direnv) by running:
   ```shell
   nix profile install 'nixpkgs#nix-direnv'
   ```
   Then add nix-direnv to `$HOME/.config/direnv/direnvrc`:
   ```bash
   source $HOME/.nix-profile/share/nix-direnv/direnvrc
   ```
5. Hook direnv into your shell by adding a line to your shell's configuration file (e.g. `~/.bashrc`),
   as described in the [direnv documentation](https://direnv.net/docs/hook.html):
6. You might have to open a new shell to make the changes take effect.
