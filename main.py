# import matplotlib.pyplot as plt

from scalingparams import *
from lib import cratcalc2, numtrask, numhart, diffuse_to_threshold, default_dDmax_strategy, eqtimeton
import sys
import pickle
import os
from math import log10


def build_lookup_table(size, max_size_km_log10, lstep, initial_depth_diamter, visibility_threshold):
    def depth_greater_than_visibility_threshold():
        return current_depth_diamter > visibility_threshold

    def decrease_depth():
        depth_interval = 0.01
        return current_depth_diamter - depth_interval

    result = {}

    while size < max_size_km_log10:
        size_km = 10.0 ** size
        size_upper_km = 10.0 ** (size + lstep)
        size_mid = 10.0 ** (size + lstep / 2.0)

        one_year_freq_at_this_size = cratcalc2(size_km, size_upper_km, lstep)

        years_to_hart = numhart(size_km, size_upper_km)/one_year_freq_at_this_size
        years_to_trask = numtrask(size_km, size_upper_km) / one_year_freq_at_this_size

        depths_and_ages = []
        current_depth_diamter = initial_depth_diamter
        print(f"Crater Diameter: {10**size}")
        while depth_greater_than_visibility_threshold():

            kT_this_size = diffuse_to_threshold(default_dDmax_strategy, size_km * 1000.0, current_depth_diamter)
            
            kT_this_size_trask = kT_this_size / (eqtimeton(years_to_trask) / 1.0e6)
            kT_this_size_hart = kT_this_size / (eqtimeton(years_to_hart) / 1.0e6)
        
            depths_and_ages.append((current_depth_diamter, kT_this_size, kT_this_size_trask, kT_this_size_hart))


            print(f"\t dD: {current_depth_diamter} \n\t Effective Kappa: {kT_this_size}\n\t Trask: {kT_this_size_trask} \n\t Hart: {kT_this_size_hart}\n")
            current_depth_diamter = decrease_depth()


        result[size] = depths_and_ages
        
        # print(f"{10**size} ::: {depths_and_ages}\n\n")
        size = size + lstep

    return result


def save_lookup_table(path, table):
    with open(path, 'wb') as handle:
        pickle.dump(table, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load_lookup_table(path):
    with open(path, 'rb') as handle:
        table = pickle.load(handle)
    return table


def default_table_path():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = f"{dir_path}/../lookup_table.pickle"
    return path


def main():
    # probably best not to have this bigger than 200m because those aren't in equilibrium
    
    

    lstep = 0.1 # 0.015051499783199 / 2.0
    min_size_km_log10 = log10(3) #-3 - lstep / 2.0
    max_size_km_log10 = log10(6) # -0.7
    size = min_size_km_log10

    initial_depth = 0.21
    visibility_threshold = 0.04 if not visibilitythreshold else visibilitythreshold

    lookup_table = build_lookup_table(size, max_size_km_log10, lstep, initial_depth, visibility_threshold)

    save_lookup_table(default_table_path(), lookup_table)

    # plt.yscale('log')
    # plt.xlim([0.95, 250.0])
    # plt.ylim([1.0e-3, 1.0])
    #
    # plt.xscale('log')
    # plt.xlabel("Crater Diameter (m)")
    # plt.ylabel("Effective Kappa $(m^2/My)$")
    #
    # plt.scatter(sizes, kTrask, label='Trask/Nominal')
    # plt.scatter(sizes, kTraskO, label='Trask/FT2014')
    # plt.scatter(sizes, kTraskP, label='Trask/PowerdD')
    # plt.scatter(sizes, kTraskQ, label='Trask/Reduced')
    # plt.legend()
    # plt.savefig('FigS4.png', dpi=300)
    # plt.show()
    #
    # except(Usage, err):
    #     print(sys.stderr, err.msg)
    #     # print >>sys.stderr, "for help use --help"
    #     return 2


if __name__ == "__main__":
    sys.exit(main())
