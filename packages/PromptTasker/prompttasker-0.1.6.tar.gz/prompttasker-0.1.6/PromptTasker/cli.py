import argparse
from .backend import run_task
import os

def main():
    parser = argparse.ArgumentParser(
        description=" :-> Prompt-based Task Runner "
    )
    parser.add_argument("--prompt", type=str, required=True, help="Prompt describing your task")
    args = parser.parse_args()
    result, output_path = run_task(args.prompt)

    if output_path:
        print(f"\nOutput saved at: {output_path}")
    else:
        print(f"\nResult: {result}")

if __name__ == "__main__":
    main()

