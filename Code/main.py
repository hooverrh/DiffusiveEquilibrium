import math
import optparse
import sys
from functools import cache

# import matplotlib.pyplot as plt

from scalingparams import *
from lib import cratcalc2, numtrask, diffuse_to_threshold, default_dDmax_strategy, eqtimeton


def build_lookup_table(size, max_size_km_log10, lstep, depth, visibility_threshold):
    def depth_less_than_visibility_threshold():
        return depth < visibility_threshold

    def decrease_depth():
        depth_interval = 0.01
        return depth - depth_interval

    result = {}

    while size < max_size_km_log10:
        size_km = 10.0**size
        size_upper_km = 10.0**(size+lstep)
        size_mid = 10.0**(size+lstep/2.0)

        one_year_freq_at_this_size = cratcalc2(size_km, size_upper_km, lstep)

        years_to_trask = numtrask(size_km, size_upper_km) / one_year_freq_at_this_size
        
        depths_and_ages = []
        while depth_less_than_visibility_threshold():

            kT_thissize = diffuse_to_threshold(default_dDmax_strategy, size_km * 1000.0, depth)
            kT_thissizeT = kT_thissize/(eqtimeton(years_to_trask) / 1.0e6)
            
            depths_and_ages.append((depth, kT_thissizeT))

        result[size] = depths_and_ages
        size = size+lstep

    return result
   
def main():
    # try:
    #     try:
    #         usage = "usage: KappaforGrunEquil_changingFlat.py\n"
    #         parser = optparse.OptionParser(usage=usage)
    #         (options, inargs) = parser.parse_args()
    #         # if not inargs: parser.error("Example text")    Currently setup for no arguments so this is pointless.
    #         # firstarg=inargs[0]
    #
    #     except (optparse.OptionError):
    #         raise Usage(optparse.OptionError)

    # probably best not to have this bigger than 200m because those aren't in equilibrium
    lstep = 0.015051499783199/2.0
    minsizekmlog10 = -3-lstep/2.0
    maxsizekmlog10 = -0.7
    size = minsizekmlog10

    initial_depth = 0.21
    visibility_threshold = 0.04 if not visibilitythreshold else visibilitythreshold

    lookup_table = build_lookup_table(size, maxsizekmlog10, lstep, initial_depth, visibility_threshold)





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
