import argparse
import sys

from ._clean_environment_from_file import clean_environment_from_file
from ._convert_pip_to_conda import convert_pip_to_conda
from .utility import configure_global_logger


def main() -> None:
    """Main script for cleaning conda environments."""
    parser = argparse.ArgumentParser(
        prog="CondaDependencyCleaner",
        description="A helper tool to clean your conda environments and convert pip dependencies to conda.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands", required=True)

    """Parse arguments for cleaning."""
    clean_parser = subparsers.add_parser(
        "clean", help="Clean conda environments from transitive dependencies."
    )
    clean_parser.set_defaults(func=clean_environment_from_file)
    clean_parser.add_argument("filename", type=str, help="The conda environment file to clean.")
    clean_parser.add_argument(
        "-nf",
        "--new-filename",
        type=str,
        help="The new conda environment filename.",
        required=False,
    )
    clean_parser.add_argument(
        "--exclude-versions",
        help="Allows to exclude versions of the dependencies.",
        action="store_true",
    )
    clean_parser.add_argument(
        "--exclude-builds",
        help="Allows to exclude builds of the dependencies.",
        action="store_true",
    )

    """Parse arguments for converting."""
    convert_parser = subparsers.add_parser(
        "convert", help="Convert pip dependencies to conda dependencies."
    )
    convert_parser.set_defaults(func=convert_pip_to_conda)
    convert_parser.add_argument(
        "filename", type=str, help="The conda environment file to use for conversion."
    )
    convert_parser.add_argument(
        "-nf",
        "--new-filename",
        type=str,
        help="The new conda environment filename.",
        required=False,
    )
    convert_parser.add_argument(
        "-c",
        "--channels",
        nargs="+",
        help="The channels to use for conversion, seperated by spaces. (default: defaults conda-forge)",
        default=["defaults", "conda-forge"],
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    configure_global_logger()
    args = parser.parse_args()
    args.func(**vars(args))


if __name__ == "__main__":
    main()
