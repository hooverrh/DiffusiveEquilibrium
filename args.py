import argparse
import string
import sys
import os
from datetime import datetime
import random


def build_diffusion_parser(subparsers):
    diffusion_parser = subparsers.add_parser(name="diffuse")

    diffusion_parser.add_argument("--min-crater-size", type=float,
                                  help="""
                        This is the starting crater diameter in kilometers.
                        This is expected to be a float. For example, if the starting crater size is 800 meters,
                        then you should provide: --min-crater-size 0.8
                        """)
    diffusion_parser.add_argument("--max-crater-size", type=float,
                                  help="""
                        This is the end crater diameter in kilometers.
                        This is expected to be a float. For example, if the largest crater diameter is 5 kilometers,
                        then you should provide: --max-crater-size 5.0
                        """)
    diffusion_parser.add_argument("--initial-depth", type=float,
                                  help="""
                        This is the starting depth diameter, the diffusion will run from the initial depth to the visibility threshold
                        This is expected to be a float. For example: --initial-depth 0.21
                        """)
    diffusion_parser.add_argument("--visibility-threshold", type=float,
                                  help="""
                        This is the end depth diameter, the diffusion will run from the initial depth to the visibility threshold
                        This is expected to be a float. For example: --visibility-threshold 0.04
                        """)
    diffusion_parser.add_argument("--diffusion-interval", type=float,
                                  help="""
                        This is the interval between each iteration of the diffusion.
                        This is expected to be a float. For example: --diffusion-interval 0.015051499783199
                        """)

    diffusion_parser.add_argument("--depth-diameter-interval", type=float,
                                  help="""
                        This is the size of the interval as the craters depth / diameter shrinks from its initial depth to the visibility threshold
                        This is expected to be a float. For example: --depth-diameter-interval 0.1
                        """)
    


def get_measured_diameter_header(args):
    if not args.measured_diameter_header:
        print(f"--measured-diameter-header is not set. This is a required field")
        sys.exit(1)
    return args.measured_diameter_header


def get_measured_depth_diameter_header(args):
    if not args.measured_diameter_header:
        print(f"--measured-depth-diameter-header is not set. This is a required field")
        sys.exit(1)
    return args.measured_depth_diameter_header


def get_min_diameter(args):
    default = 0.0
    if not args.minimum_diameter:
        print(f"--minimum-diameter not set, using the default starting crater diameter {default}km ")
        return default
    print(f"Using user provided minimum crater diamter {args.minimum_diameter}km")
    return args.minimum_diameter


def get_max_diameter(args):
    default = 999999999.0
    if not args.maximum_diameter:
        print(f"--maximum-diameter not set, using the default starting crater diameter {default}km ")
        return default
    print(f"Using user provided maximum crater diamter {args.maximum_diameter}km")
    return args.maximum_diameter


def get_output_file(args):
    default = str(datetime.now()) + ".csv"
    if not args.output_file:
        print(f"--output-file not set. Using {default}")
        return default
    if not str(args.output_file).endswith(".csv"):
        return args.output_file + ".csv"
    return args.output_file


def get_output_suffix(args):
    default = ''.join(random.choice(string.ascii_uppercase) for i in range(3))
    if not args.output_suffix:
        print(f"--output-suffix not set. Using {default}")
        return default
    return args.output_suffix


def get_include_trask(args):
    default = False
    if args.include_trask:
        print(f"--include-trask is set")
        default = True
    return default


def get_include_hart(args):
    default = False
    if args.include_hart:
        print(f"--include-hart is set")
        default = True
    return default


def build_measure_parser(subparsers):
    parser = subparsers.add_parser(name="measure")

    parser.add_argument("--lookup-table-path", type=str,
                        help="""
                        *OPTIONAL*
                        This is the path to the lookup table. It should be a pickle file. Use relative path
                        """)
    parser.add_argument("--csv-path", type=str, required=True,
                        help="""
                        *REQUIRED*
                        This is the path to the CSV file
                        """)
    parser.add_argument("--measured-diameter-header", type=str, required=True,
                        help="""
                        *REQUIRED*
                        This is the name of the column containing measure diameter
                        """)
    parser.add_argument("--minimum-diameter", type=float, required=False,
                        help="""
                        *OPTIONAL*
                        This is the smallest diameter crater in the csv that will be processed
                        This should be a float. For example:
                        --minimum-diameter 0.8
                        for a crater whose diameter is 800m
                        """)
    parser.add_argument("--maximum-diameter", type=float, required=False,
                        help="""
                        *OPTIONAL*
                        This is the largest diameter crater in the csv that will be processed
                        This should be a float. For example:
                        --max-diameter 0.8
                        for a crater whose diameter is 800m
                        """)
    parser.add_argument("--measured-depth-diameter-header", type=str, required=True,
                        help="""
                        *REQUIRED*
                        This is the name of the column containing measure depth diameter ratio
                        """)

    parser.add_argument("--output-file", type=str,
                        help="""
                        *OPTIONAL*
                        Name of the CSV file which will be generated when run.
                        If no file is provided an automatically generated with be created.
                        This will overwrite a existing file of the same name.
                        """)

    parser.add_argument("--output-suffix", type=str,
                        help="""
                        *OPTIONAL*
                        A suffix that will be affixed to the headers for modeled data.
                        If omitted a random 3 character string will be used instead
                        """)

    parser.add_argument("--verbosity", type=int, default=0,
                        help="""
                        *OPTIONAL*
                        This will print additional log statements
                        Values:
                            0: Standard logging for normal execution
                            1: Additional Info
                            2: Debug Info
                            3: Warning

                        Example: --verbosity 1
                        """)
    parser.add_argument("--include-trask", action='store_true',
                        help="""
                        *OPTIONAL*
                        This will include the Trask values into the resultant csv file

                        Example: --include-trask
                        """)
    parser.add_argument("--include-hart", action='store_true',
                        help="""
                        *OPTIONAL*
                        This will include the Hart values into the resultant csv file

                        Example: --include-hart
                        """)
    parser.add_argument("--visibility-threshold", type=float,
                                  help="""
                        This is the end depth diameter, the diffusion will run from the initial depth to the visibility threshold
                        This is expected to be a float. For example: --visibility-threshold 0.04
                        """)


def get_csv_path(args):
    if not args.csv_path:
        print(f"--csv-path not set. This is required")
        sys.exit(1)
    print(f"Using csv file {args.csv_path}")
    return args.csv_path


def default_table_path():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = f"{dir_path}/../lookup_table.pickle"
    return path


def get_lookup_table_path(args):
    if not args.lookup_table_path:
        print(f"--lookup-table-path is not set. Using default lookup table path {default_table_path()}")
        return default_table_path()
    print(f"Using user provided lookup table {args.lookup_table_path}")
    return args.lookup_table_path


def parse_args():
    parser = argparse.ArgumentParser(
        prog='Diffusive Equilibrium',
    )
    subparsers = parser.add_subparsers(dest="command")

    build_diffusion_parser(subparsers)
    build_measure_parser(subparsers)

    return parser.parse_args()


def get_min_size(args):
    default_min = 3
    if not args.min_crater_size:
        print(f"--min-crater-size not set, using the default starting crater diameter {default_min}km ")
        return default_min
    print(f"Using user provided minimum crater diamter {args.min_crater_size}km")
    return args.min_crater_size


def get_max_size(args):
    default_max = 6.0
    if not args.min_crater_size:
        print(f"--max-crater-size not set, using the default starting crater diameter {default_max}km ")
        return default_max
    print(f"Using user provided maximum crater diamter {args.max_crater_size}km")
    return args.max_crater_size


def get_initial_depth(args):
    default_depth = 0.21
    if not args.initial_depth:
        print(f"--initial-depth not set, using the default depth/diameter ratio {default_depth}")
        return default_depth
    print(f"Using user provided initial depth diameter ratio {args.initial_depth}")
    return args.initial_depth


def get_visibility_threshold(args):
    default_depth = 0.04
    if not args.visibility_threshold:
        print(f"--visbility-threshold not set, using the default visibility threshold {default_depth}")
        return default_depth
    print(f"Using user provided visibility threshold {args.visibility_threshold}")
    return args.visibility_threshold


def get_diffusion_interval(args):
    default_interval = 0.015051499783199
    if not args.diffusion_interval:
        print(f"--diffusion-interval not set, using the default diffusion interval {default_interval}")
        return default_interval / 2
    print(f"Using user provided diffusion interval {args.diffusion_interval}")
    return args.diffusion_interval / 2


def get_depth_interval(args):
    default_interval = 0.01
    if not args.depth_diameter_interval:
        print(f"--depth-diameter-interval not set, using the default depth interval{default_interval}")
        return default_interval
    print(f"Using user provided depth interval {args.depth_diameter_interval}")
    return args.depth_diameter_interval
