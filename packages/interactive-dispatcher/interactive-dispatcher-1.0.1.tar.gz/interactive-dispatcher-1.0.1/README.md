# Interactive Dispatcher
**Interactive Dispatcher** is a lightweight and customizable command-line menu system that allows you to define interactive options with corresponding return signals and handler functions. It is especially useful for CLI tools, REPLs, configuration managers, or anything needing a user-driven menu interface.

---

## Features
- Customizable option prompts
- Signal-returning dispatch mechanism
- Easy-to-extend architecture
- Supports looped interactions
- Clean, readable, and minimal dependency footprint
- Add your own signals to finely control the logic flow

---

## Installation
```bash
pip install interactive-dispatcher
```

---

## Example
```python
# example.py
from interactive_dispatcher import Action, MenuItem, ReturnSignal, interactive_dispatcher

# Register a custom signal
ReturnSignal.register("RESTART")

# Sample functions
def greet(name: str) -> str:
    print(f"Hello, {name}!")
    return f"Greeted {name}"

def log(msg: str) -> str:
    print(f"[Log] {msg}")
    return "Logged"

def exit_program() -> str:
    print("Goodbye!")
    return "Exited"

# Menu configuration
menu: list[MenuItem] = [
    MenuItem(
        keys=["greet", "g"],
        description="Greet a user and log the action",
        actions=[
            Action(function=greet, args=("Alice",)),
            Action(function=log, args=("Greeting sent to Alice",))
        ],
        return_signal=ReturnSignal.CONTINUE
    ),
    MenuItem(
        keys=["restart", "r"],
        description="Restart the application",
        actions=[
            Action(function=log, args=("Restarting...",))
        ],
        return_signal=ReturnSignal.RESTART
    ),
    MenuItem(
        keys=["exit", "e", "q"],
        description="Exit the program",
        actions=[
            Action(function=exit_program)
        ],
        return_signal=ReturnSignal.BREAK
    )
]

# Dispatcher loop
while True:
    results, signal = interactive_dispatcher("Choose an option:", menu)
    print(f"Results: {results}")
    print(f"ReturnSignal: {signal}")

    if signal == ReturnSignal.BREAK:
        break
    elif signal == ReturnSignal.RESTART:
        print("Restarting...\n")

```
## Output
![alt text](image.png)

---

## Purpose
Interactive Dispatcher abstracts away repetitive CLI input logic and allows developers to:
- Focus on logic instead of input parsing
- Use readable "signals" to handle control flow
- Easily integrate menus inside other CLI tools

---

## Customization
You can fully customize menu prompts, signals, or plug the dispatcher into larger CLI apps.

### With Callable Handlers
```python
from interactive_dispatcher import InteractiveDispatcher

def greet():
    print("Hello!")

def farewell():
    print("Goodbye!")

dispatcher = InteractiveDispatcher(
    title="Greeting Menu",
    options={
        "Say Hello": greet,
        "Say Goodbye": farewell,
        "Exit": "exit"
    }
)

while True:
    signal = dispatcher.run()
    if signal == "exit":
        break

```

---

## Return Signal Philosophy
Instead of tightly coupling option text and logic, each option can return a signal string which you can route freely in your application logic.

This approach gives you:

- Flexibility
- Testability
- Clean separation of concerns

---

## Use Cases
Use cases are mostly limited to CLI driven interfaces where you want something light, easy and maintainable.
- Interactive CLI tools and wrappers
- Shell-like applications
- Configuration or wizard interfaces
- Automation Scripts

---

## Advantages
- Simple interface with powerful control
- Works seamlessly in loops
- Easily composable with your business logic
- Minimal code makes it easy to test


