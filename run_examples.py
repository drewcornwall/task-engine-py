from examples import run_examples
import sys

example = sys.argv[1] if len(sys.argv) > 1 else input("Enter example name: ")


if __name__ == "__main__":
    run_examples(example)
