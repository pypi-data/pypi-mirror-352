"""Collection of utility functions local to the models package"""

from jbutils.types import Function
from rich import print

from jbqt.models.model_consts import RegisteredFunctions


def register_fct(name: str, fct: Function, override: bool = False) -> None:
    if name not in RegisteredFunctions:
        RegisteredFunctions[name] = fct
        if override and name in RegisteredFunctions:
            # TODO improve logging
            print(
                f"[yellow][Warning][/yellow]: Function '{name}' already defined and was overwritten"
            )
    print(f"[yellow][Warning][/yellow]: Function '{name}' already defined")


def get_fct(name: str, fallback: Function | None = None) -> Function | None:
    return RegisteredFunctions.get(name, fallback)


__all__ = ["register_fct", "get_fct"]
