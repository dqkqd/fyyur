import subprocess
import sys


def main() -> None:
    output = subprocess.run("python -m flask db check", shell=True, capture_output=True)
    if output.returncode:
        output_string = output.stderr.decode("utf-8")
        print(output_string)
        sys.exit(1)


if __name__ == "__main__":
    main()
