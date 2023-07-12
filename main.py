# import matplotlib.pyplot as plt

from lib import cratcalc2, numtrask, numhart, diffuse_to_threshold, default_dDmax_strategy, eqtimeton, solve_for_t
from math import log10
from args import *
import sys
import pickle
import csv


def print_modeled_data(data):
    print(
            f"\t dD: {data[0]} \n\t Effective Kappa: {data[1]}\n\t Trask: {data[2]} \n\t Hart: {data[3]}\n \n\t CraterAge: {data[4]}\n")

def build_lookup_table(size, max_size_km_log10, diffusion_interval, initial_depth_diamter, visibility_threshold,
                       depth_interval):
    def depth_greater_than_visibility_threshold():
        return current_depth_diamter > visibility_threshold


    def decrease_depth():
        return current_depth_diamter - depth_interval

    result = {}

    
    while size < max_size_km_log10:
        size_km = 10.0 ** size
        size_upper_km = 10.0 ** (size + diffusion_interval)
        size_mid = 10.0 ** (size + diffusion_interval / 2.0)

        one_year_freq_at_this_size = cratcalc2(size_km, size_upper_km, diffusion_interval)

        years_to_hart = numhart(size_km, size_upper_km) / one_year_freq_at_this_size
        years_to_trask = numtrask(size_km, size_upper_km) / one_year_freq_at_this_size

        depths_and_ages = []
        current_depth_diamter = initial_depth_diamter
        print(f"Crater Diameter: {size_km}")
        while depth_greater_than_visibility_threshold():
            kT_this_size = diffuse_to_threshold(default_dDmax_strategy, size_km * 1000.0, current_depth_diamter)
            #kT_this_size = diffuse_to_threshold(default_dDmax_strategy, size_km, current_depth_diamter)

            kT_this_size_trask = kT_this_size / (eqtimeton(years_to_trask) / 1.0e6)
            kT_this_size_hart = kT_this_size / (eqtimeton(years_to_hart) / 1.0e6)

            data = (current_depth_diamter, kT_this_size, kT_this_size_trask, kT_this_size_hart, solve_for_t(kT_this_size))
           

            depths_and_ages.append(data)

            print_modeled_data(data)

            current_depth_diamter = decrease_depth()

        result[size_km] = depths_and_ages

        size = size + diffusion_interval

    return result


def save_lookup_table(path, table):
    with open(path, 'wb') as handle:
        pickle.dump(table, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load_lookup_table(path):
    with open(path, 'rb') as handle:
        table = pickle.load(handle)
    return table


def do_diffuse(args):
    diffusion_interval = get_diffusion_interval(args)
    min_size_km_log10 = log10(get_min_size(args))
    max_size_km_log10 = log10(get_max_size(args))
    initial_depth = get_initial_depth(args)
    visibility_threshold = get_visibility_threshold(args)
    depth_interval = get_depth_interval(args)

    lookup_table = build_lookup_table(min_size_km_log10, max_size_km_log10, diffusion_interval, initial_depth,
                                      visibility_threshold, depth_interval)

    save_lookup_table(default_table_path(), lookup_table)


def find_nearest(lst, K):
    return lst[min(range(len(lst)), key=lambda i: abs(lst[i] - K))]


def do_measure(args):
    def reshape_modeled_data(tuple_list):
        data = {}
        for t in tuple_list:
            data[t[0]] = t
        return data

    def in_range(value):
        if min_diameter <= value <= max_diameter:
            return True
        return False

    def find_best_fit(measured_depth_diameter, measured_diameter):
        nearest_modeled_diameter = find_nearest(list(lookup_table.keys()), measured_diameter)
        nearest_measurements = lookup_table[nearest_modeled_diameter]
        reshaped_data = reshape_modeled_data(nearest_measurements)
        nearest_depth_diameter = find_nearest(list(reshaped_data.keys()), measured_depth_diameter)
        best_fit = reshaped_data[nearest_depth_diameter]

        if verbosity >= 1:
            print(f"\n Measured Diameter: {measured_diameter}kn \n Nearest Modeled Diameter: {nearest_modeled_diameter}km")
            print(f"\t Measured dD {measured_depth_diameter}")
            print_modeled_data(best_fit)

        return best_fit

    csv_path = get_csv_path(args)
    table_path = get_lookup_table_path(args)
    diameter_header = get_measured_diameter_header(args)
    depth_diameter_header = get_measured_depth_diameter_header(args)
    min_diameter = get_min_diameter(args)
    max_diameter = get_max_diameter(args)
    outfile = get_output_file(args)
    output_suffix = get_output_suffix(args)
    include_trask = get_include_trask(args)
    include_hart = get_include_hart(args)
    visibility_threshold = get_visibility_threshold(args)
    verbosity = args.verbosity

    lookup_table = load_lookup_table(table_path)

    new_rows = []

    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        rows = list(reader)
        rejected = 0
        processed = 0
        not_in_range = 0

        for row in rows:
            row[f"modeled_dD_{output_suffix}"] = ''
            row[f"modeled_kT_{output_suffix}"] = ''
            if include_trask:
                row[f"modeled_trask_{output_suffix}"] = ''
            if include_hart:
                row[f"modeled_hart_{output_suffix}"] = ''
            row[f"modeled_craterage_{output_suffix}"] = ''

            try:
                measured_depth_diameter = float(row[depth_diameter_header])
                measured_diameter = float(row[diameter_header])

                if measured_depth_diameter <= visibility_threshold:
                    rejected += 1
                    continue

                if measured_depth_diameter > 0.21:
                    rejected += 1
                    continue


            except:
                if verbosity >= 2:
                    print(f"Unable to handle row {row}\n Skipping...\n")
                rejected += 1
                new_rows.append(row)
                continue

            if not in_range(measured_diameter):
                not_in_range += 1
                continue

            best = find_best_fit(measured_depth_diameter, measured_diameter)
            row[f"modeled_dD_{output_suffix}"] = best[0]
            row[f"modeled_kT_{output_suffix}"] = best[1]
            if include_trask:
                row[f"modeled_trask_{output_suffix}"] = best[2]
            if include_hart:
                row[f"modeled_hart_{output_suffix}"] = best[3]
            row[f"modeled_craterage_{output_suffix}"] = best[4]

            new_rows.append(row)
            processed += 1


        print(f"Skipped {rejected} rows. \nProcessed {processed} rows. \n{not_in_range} rows not in range.")


    with open(outfile, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, delimiter=',', fieldnames=list(new_rows[0].keys()))
        writer.writeheader()
        writer.writerows(new_rows)




def main(args):
    if args.command == "diffuse":
        do_diffuse(args)
        sys.exit(0)

    if args.command == "measure":
        do_measure(args)
        sys.exit(0)

    sys.exit(1)


if __name__ == "__main__":
    try:
        main(parse_args())
    except KeyboardInterrupt:
        print("User quitting...")
        sys.exit(1)
