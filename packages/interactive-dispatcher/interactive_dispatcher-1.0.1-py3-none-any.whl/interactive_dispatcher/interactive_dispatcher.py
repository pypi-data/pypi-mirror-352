# interactive_dispatcher.py
from __future__ import annotations
from typing import Callable, Tuple, Dict, Any, List, Final, Optional
from dataclasses import dataclass, field


class ReturnSignal:
    _registry: Final[Dict[str, ReturnSignal]] = {}

    def __new__(cls, name: str) -> ReturnSignal:
        raise RuntimeError("Use ReturnSignal.register(...) to create new signals.")

    def __repr__(self) -> str:
        return f"ReturnSignal.{self.name}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ReturnSignal) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    @classmethod
    def register(cls, *names: str) -> None:
        for name in names:
            key = name.upper()
            if key not in cls._registry:
                inst = object.__new__(cls)
                inst.name: str = key
                cls._registry[key] = inst
                setattr(cls, key, inst)  # Enables dot-access like Enum

    @classmethod
    def get(cls, name: str) -> Optional[ReturnSignal]:
        return cls._registry.get(name.upper())

    @classmethod
    def all(cls) -> List[ReturnSignal]:
        return list(cls._registry.values())


# Register default signals
ReturnSignal.register("CONTINUE", "BREAK", "PASS", "NONE")


@dataclass
class Action:
    function: Callable[..., Any]
    args: Tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MenuItem:
    keys: List[str]                          # e.g., ['yes', 'y']
    description: str                         # Menu display text
    actions: List[Action]                    # Multiple actions to run
    return_signal: ReturnSignal = ReturnSignal.NONE


def interactive_dispatcher(
    prompt: str,
    menu_items: List[MenuItem],
    *,
    top_sep_char: str = "=",
    top_sep_len: int = 40,
    bottom_sep_char: str = "-",
    bottom_sep_len: int = 40
) -> Tuple[List[Any], ReturnSignal]:
    """
    Displays a menu with optional separators, runs the selected list of actions,
    and returns results + a ReturnSignal.
    """
    print(top_sep_char * top_sep_len)
    print(f"\n{prompt}")
    for item in menu_items:
        keys_display = "/".join(item.keys)
        print(f"\t[{keys_display}]\t{item.description}")
    print(bottom_sep_char * bottom_sep_len)

    choice = input("Enter your choice: ").strip()

    for item in menu_items:
        if choice in item.keys:
            results = [
                action.function(*action.args, **action.kwargs)
                for action in item.actions
            ]
            return results, item.return_signal

    print("Invalid choice.")
    return [], ReturnSignal.NONE
