import importlib


def run_examples(example_name: str):
    try:
        module = importlib.import_module(f"examples.{example_name}")

        run_function = getattr(module, 'run')

        run_function()
    except ModuleNotFoundError:
        raise Exception(f"Module for example '{example_name}' not found")
    except AttributeError:
        raise Exception(f"'run' function not found in the '{example_name}' example module")
