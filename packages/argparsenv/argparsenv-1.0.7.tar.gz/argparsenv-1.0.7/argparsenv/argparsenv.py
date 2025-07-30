"""This module contains utilities for command line interfaces, icnluding argument parsing and configuration."""

from __future__ import annotations
import argparse
from os import (
    path as os_path,
    getenv as os_getenv,
    getcwd as os_getcwd,
)
from dotenv import load_dotenv
from overrides import override


class ArgumentParser(argparse.ArgumentParser):
    """Enhances the standard argparse.ArgumentParser by adding the ability to read\
            default values from environment variables."""

    def __init__(self, *args, **kwargs):
        """Initializes the parser and loads the environment variables from the .env file.
        *args: inherited from argparse.ArgumentParser
        **kwargs: inherited from argparse.ArgumentParser

        Initializes the parser with the given arguments and loads the environment variables.
        >>> parser = ArgumentParser(description="This is a parser")
        """
        super().__init__(*args, **kwargs)
        load_dotenv(os_path.join(os_getcwd(), ".env"))

    def get_value_from_environment(
        self, env_key: None | str, fallback_value: None | str
    ) -> None | str:
        """Looks up the value of the given environment variable and returns it if it is\
                set or the fallback value otherwise. If the environment variable is set\
                both via the environment and the .env file, the value from\
                the environment is used.

        Args:
            env_key: The name of the environment variable to look up.
            fallback_value: The value to return if the environment variable is not set.

        Returns:
            A string containing the value of the environment variable or the fallback\
                    value if the environment variable is not set. May be None.
        """
        if env_key:
            env_key = env_key.strip()
            if env_key := env_key.strip():
                if (env_value := os_getenv(env_key.strip())) is not None:
                    return env_value
        return fallback_value

    @override
    def add_argument(self, *args, **kwargs):
        """Adds an argument to the parser and (in additon to the inherited method)\
                overrides the default value with the value of the environment variable\
                if it is set.

        Args:
            *args: Inherited from argparse.ArgumentParser.add_argument.
            **kwargs: Inherited from argparse.ArgumentParser.add_argument.\
                    Additionally, the keyword argument `env_var` is added.\
                    If `env_var` is set, the default value is tried to be read from\
                    the environment variable with the given name.\

        Returns:
            The original return value of argparse.ArgumentParser.add_argument.

        Example:
        >>> p = ArgumentParser().add_argument("--port", dest="port", env_var="MY_APP_DB_PORT", default="3306", )
        """

        if "env_var" in kwargs:
            env_var = kwargs["env_var"]
            del kwargs["env_var"]
            kwargs["default"] = self.get_value_from_environment(
                env_var,
                kwargs["default"] if "default" in kwargs else None,
            )
        return super().add_argument(*args, **kwargs)
