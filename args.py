import argparse
def parse_args():
    parser = argparse.ArgumentParser(
        prog='Diffusive Equilibrium',
    )

    parser.add_argument("--min-crater-size", type=float,
                        help="""
                        This is the starting crater diameter in kilometers.
                        This is expected to be a float. For example, if the starting crater size is 800 meters,
                        then you should provide: --min-crater-size 0.8
                        """)
    parser.add_argument("--max-crater-size", type=float,
                        help="""
                        This is the end crater diameter in kilometers.
                        This is expected to be a float. For example, if the largest crater diameter is 5 kilometers,
                        then you should provide: --max-crater-size 5.0
                        """)
    parser.add_argument("--initial-depth", type=float,
                        help="""
                        This is the starting depth diameter, the diffusion will run from the initial depth to the visibility threshold
                        This is expected to be a float. For example: --initial-depth 0.21
                        """)
    parser.add_argument("--visibility-threshold", type=float,
                        help="""
                        This is the end depth diameter, the diffusion will run from the initial depth to the visibility threshold
                        This is expected to be a float. For example: --visibility-threshold 0.04
                        """)
    parser.add_argument("--diffusion-interval", type=float,
                        help="""
                        This is the interval between each iteration of the diffusion.
                        This is expected to be a float. For example: --diffusion-interval 0.015051499783199
                        """)
    

    parser.add_argument("--depth-diameter-interval", type=float,
                        help="""
                        This is the size of the interval as the craters depth / diameter shrinks from its initial depth to the visibility threshold
                        This is expected to be a float. For example: --depth-diameter-interval 0.1
                        """)
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



