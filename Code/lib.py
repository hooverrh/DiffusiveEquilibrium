import numpy as np
import math
from pynverse import inversefunc  # pip install pynverse  in relevant conda environment

from scalingparams import *
from functools import cache


def numhart(lowdiamkm, updiamkm):
    hartlow = (10.0 ** -1.14) * lowdiamkm ** -1.83
    harthigh = (10.0 ** -1.14) * updiamkm ** -1.83

    hart = (hartlow - harthigh) * surface_area

    return hart


def numtrask(lowdiamkm, updiamkm):
    trasklow = (10.0 ** -1.1) * lowdiamkm ** -2.0
    traskhigh = (10.0 ** -1.1) * updiamkm ** -2.0

    trask = (trasklow - traskhigh) * surface_area

    return trask


def npfcalc(size):
    # this finds the NPF ==> N(>=size) for crater with -crater size-.  From Neukum and Ivanov/2001.
    # sizes in km

    correctionfrom1millionyrsto1yr = 1.0e-6

    log10freq = 0.0

    npfcoeffs = [-6.076755981, -3.557528, 0.781027, 1.021521, -0.156012, -0.444058, 0.019977, 0.08685, -0.005874,
                 -0.006809, 0.000825, 0.0000554]
    for a in range(12):
        log10freq = log10freq + npfcoeffs[a] * ((math.log10(size)) ** a)

    cumfreq = correctionfrom1millionyrsto1yr * (10.0 ** log10freq)

    return cumfreq


def makegruns(minlogmassgrams=-18.0, maxlogmassgrams=2.0):
    # Note that the upper valid limit on Grun is 10^2 grams.  Need to solve for bigger particles some other way.

    logstep = 0.1

    # Constants below equation A2 from Grun
    grun_c_s = [4.00E+29, 1.50E+44, 1.10E-02, 2.20E+03, 1.50E+01]
    grun_y_s = [1.85E+00, 3.70E+00, -5.20E-01, 3.06E-01, -4.38E+00]

    grunsize_m = []
    grunflux = []
    masslog = minlogmassgrams

    while masslog <= maxlogmassgrams:
        massg = 10.0 ** masslog

        # converts particle mass to radius 
        grunsize = 0.01 * (
                    ((1.0 / (impactor_density / 1000.0)) * ((3.0 / 4.0) * (1.0 / math.pi) * massg)) ** (1.0 / 3.0))

        # equation A2 from Grun
        fluxone = (grun_c_s[0] * (massg ** grun_y_s[0]) + grun_c_s[1] * (massg ** grun_y_s[1]) + grun_c_s[2]) ** \
                  grun_y_s[2]
        fluxtwo = (grun_c_s[3] * (massg ** grun_y_s[3]) + grun_c_s[4]) ** grun_y_s[4]
        flux = fluxone + fluxtwo
        # fluxes are in per m2 per second
        # per km2 per yeaar
        flux_rescale = flux * 86400.0 * 365.25 * 1000000.0

        grunflux.append(flux_rescale)
        grunsize_m.append(grunsize)

        masslog = masslog + logstep

    return grunsize_m, grunflux


def hohocratersize(impradius):
    # Holsapple theory paper style
    # RELIES ON COMMON SCALING PARAMETERS FROM SCALINGPARAMS.PY  
    # Fixes errors in piV, 7/26

    impactor_mass = ((4.0 * math.pi) / 3.0) * impactor_density * (impradius ** 3.0)
    pi2 = (gravity * impradius) / (effective_velocity ** 2.0)
    pi3 = strength / (target_density * (effective_velocity ** 2.0))
    expone = (6.0 * nu - 2.0 - mu) / (3.0 * mu)
    exptwo = (6.0 * nu - 2.0) / (3.0 * mu)
    expthree = (2.0 + mu) / 2.0
    expfour = (-3.0 * mu) / (2.0 + mu)
    piV = K1 * (pi2 * (density_ratio ** expone) + ((K2 * pi3 * (density_ratio ** exptwo)) ** expthree)) ** expfour
    V = (impactor_mass * piV) / target_density  # m3 for crater
    craterrimrad = Kr * (V ** (1.0 / 3.0))
    cratersize = 2.0 * craterrimrad

    return cratersize


def default_dDmax_strategy(diameter, sigma):
    if diameter > 400:
        dDmax = 0.21
    elif diameter > 200:
        dDmax = 0.17
    elif diameter > 100:
        dDmax = 0.15
    elif diameter > 40:
        dDmax = 0.13
    elif diameter > 10:
        dDmax = 0.11
    else:
        dDmax = 0.1

    dDmax = dDmax + np.random.normal(0, sigma)
    return dDmax


def dDmax_strategy_q(diameter, sigma):
    if diameter > 400:
        dDmax = 0.189
    elif diameter > 200:
        dDmax = 0.153
    elif diameter > 100:
        dDmax = 0.135
    elif diameter > 40:
        dDmax = 0.117
    elif diameter > 10:
        dDmax = 0.099
    else:
        dDmax = 0.09

    dDmax = dDmax + np.random.normal(0, sigma)
    return dDmax


def dDmax_strategy_o(diameter, sigma):
    dDmax = 0.21
    return dDmax


def dDmax_strategy_p(diameter, sigma):
    dDmax = 0.0717 * diameter ** 0.169
    return dDmax


def diffuse_to_threshold(dDmax_strategy, diam, visibility_threshold):
    domainsizepx = 400
    sscale = diam / 100.0

    u = np.zeros((domainsizepx, domainsizepx))
    un = np.zeros((domainsizepx, domainsizepx))

    alpha = 1.0
    xcen = domainsizepx / 2
    ycen = domainsizepx / 2
    xvals = np.linspace(0, sscale * domainsizepx, num=domainsizepx) - (xcen * sscale)

    curradius = diam / 2.0
    currange = 1.5 * curradius

    px_r = (curradius / sscale)
    x, y = np.ogrid[:domainsizepx, :domainsizepx]
    distfromcen = (((x - xcen) ** 2.0 + (y - ycen) ** 2.0) ** 0.5) * sscale
    rangefromcen = distfromcen / curradius
    incrat = np.logical_and(rangefromcen >= 0.0, rangefromcen < 0.98)
    rim = np.logical_and(rangefromcen >= 0.98, rangefromcen < 1.02)
    outcrat = np.logical_and(rangefromcen >= 1.02, rangefromcen < 1.5)

    sigma = 0.0  # 35

    dDmax = dDmax_strategy(diam, sigma)

    interiorfloor = -(dDmax - 0.036822095) * diam

    # FRESH CRATER MODEL:  Basically what's in Fassett and Thomson, 2014, with a little fix implremented at the rim (whoops)
    # forced to have a flat floor to match dDMax at small sizes

    u[incrat] = (-0.228809953 + 0.227533882 * rangefromcen[incrat] + 0.083116795 * (
                rangefromcen[incrat] ** 2.0) - 0.039499407 * (rangefromcen[incrat] ** 3.0)) * diam
    u[rim] = 0.036822095 * diam
    u[outcrat] = (0.188253307 - 0.187050452 * rangefromcen[outcrat] + 0.01844746 * (
                rangefromcen[outcrat] ** 2.0) + 0.01505647 * (rangefromcen[outcrat] ** 3.0)) * diam
    u[u < interiorfloor] = interiorfloor

    # courant criteria and timesteps
    dtst = 0.5 * (sscale ** 2.0) / (2 * alpha)

    r = dtst * alpha / (sscale ** 2.0)

    dD = (np.max(u) - np.min(u)) / diam
    step = 0

    # Standard Explicit diffusion equations; modified from my old Matlab code
    while dD >= visibility_threshold:
        un[1:-1, 1:-1] = u[1:-1, 1:-1] + r * (
                    (u[2:, 1:-1] + u[:-2, 1:-1]) + (u[1:-1, 2:] + u[1:-1, :-2] - 4 * u[1:-1, 1:-1]))
        u = np.copy(un)
        step = step + 1
        dD = (np.max(u) - np.min(u)) / diam

    kappaT = step * dtst
    return kappaT


def cratcalc2(size_km, size_km_upper, lstep):
    epsilon = 1.0e-9  # need a small value to get off boundary
    # these are sizes in m,  assuming hohoscaling, and grunfluxes (per km2 per yr)
    grunimpradii_m, grunfluxes = makegruns()
    grundiameters = [hohocratersize(r) for r in grunimpradii_m]
    grundiameterslog = [math.log10(el) for el in grundiameters]
    grunfluxeslog = [math.log10(el) for el in grunfluxes]
    size = size_km * 1000.0
    sizeu = size_km_upper * 1000.0
    slog = math.log10(size)
    sulog = math.log10(sizeu)
    if size < 10.0:
        # In range where need to interpolate between Neukum at 10m and whatever the maximum Grun diameter is
        if sulog > grundiameterslog[-1]:
            interpdiams = [grundiameterslog[-1] - 0.5 * lstep, 1 + 0.5 * lstep]
            interpfreqs = [cratcalc2(10 ** (grundiameterslog[-1] - lstep - epsilon - 3.0),
                                     10 ** (grundiameterslog[-1] - epsilon - 3.0), lstep),
                           (10 ** math.log10(npfcalc(0.01)) - 10 ** math.log10(npfcalc(10 ** (-2.0 + lstep))))]
            interpfreqsl = [math.log10(el) for el in interpfreqs]
            dfluxintlog = np.interp((slog + sulog) / 2.0, interpdiams, interpfreqsl)
            dflux = 10 ** dfluxintlog

        elif sulog <= grundiameterslog[-1]:
            fluxintlog = np.interp(slog, grundiameterslog, grunfluxeslog)
            fluxint = 10.0 ** fluxintlog
            fluxuintlog = np.interp(sulog, grundiameterslog, grunfluxeslog)
            fluxuint = 10.0 ** fluxuintlog
            dflux = fluxint - fluxuint
        else:
            # this branch only happens if there is a bug.
            dflux = np.nan

        globalfreq = surface_area * dflux
    elif size >= 10.0:
        globalfreq = surface_area * (npfcalc(size_km) - npfcalc(size_kmupper))
    else:
        # this branch should never happen, unless there is a bug.
        globalfreq = np.nan

    return globalfreq


def neqtime(time):
    timeMa = time / 1.0e6
    timeCorMa = (0.0000000000000544 * (math.exp(0.00693 * timeMa) - 1) + 0.000000838 * timeMa) / 0.000000838
    # convert back to Neukum-eq years (not physical years, for the early chronology!)
    timeCor = timeCorMa * 1.0e6

    print(f"time::: {time } \n\ttimeMa ::: {timeMa}\n\ttimeCorMa ::: {timeCorMa} \n\ttimeCor ::: {timeCor}")

    return timeCor


eqtimeton = inversefunc(neqtime)
