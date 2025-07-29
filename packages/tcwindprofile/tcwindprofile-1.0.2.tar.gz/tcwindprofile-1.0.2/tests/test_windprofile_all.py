# test_windprofile_all.py

## Create a fast and robust radial profile of the tropical cyclone rotating wind from inputs Vmax, R34kt, latitude, and Vtrans.


import os
import sys

# Add parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import math

############################################################
# NHC/Best Track Operational Inputs
VmaxNHC_kt = 100  # [kt]; NHC storm intensity (point-max wind speed)
Vtrans_kt = 20    # [kt]; storm translation speed, usually estimated from adjacent track points; used to estimate azimuthal-mean Vmax (Vmaxmean_ms = VmaxNHC_ms - 0.55*Vtrans_ms)
lat = 20  # [degN]; default 20N; storm-center latitude
R34ktNHCquadmax_nautmi = (135 + 150 + 145 + 150) / 4 # average NHC R34kt radius (here 4 quadrants)
                                                        # these are officially the MAXIMUM radii of this wind speed in each quadrant;
                                                        # value is reduced by 0.85 within the code to estimate the mean radius (see Chavas Knaff Klotzbach 2025 for more info)
Penv_mb = 1008      #[mb]; environmental pressure, to create full pressure profile
## Default values: VmaxNHC_kt=100 kt, R34ktNHCquadmax_nautmi= 145.0 naut mi, lat = 20 --> unadjusted Rmax=38.1 km (sanity check)
############################################################


################################################################
## Calculate wind and pressure profiles and associated data
"""
Full modeling pipeline:
- Estimate Rmax from R34kt: ref Chavas and Knaff 2022 WAF)
- Estimate R0 from R34kt: approximate version of outer model ref Emanuel 2004 / Chavas et al. 2015 JAS / Chavas and Lin 2016 JAS
- Generate wind profile: merge simple inner + outer models, ref Klotzbach et al. 2022 JGR-A / Chavas and Lin 2016 JAS
- Estimate Pmin: ref Chavas Knaff Klotzbach 2025 WAF
- Generate pressure profile that matches Pmin: ref Chavas Knaff Klotzbach 2025 WAF
"""
from tcwindprofile.windprofile_all import run_full_wind_model

tc_wind_and_pressure_profile = run_full_wind_model(
    VmaxNHC_kt=VmaxNHC_kt,
    Vtrans_kt=Vtrans_kt,
    R34kt_quad_max_nautmi=R34ktNHCquadmax_nautmi,
    lat=lat,
    Penv_mb=Penv_mb,
    plot=True
)

print(f"Rmax = {tc_wind_and_pressure_profile['Rmax_km']:.1f} km")
print(f"R0 = {tc_wind_and_pressure_profile['R0_km']:.1f} km")
print(f"Pmin = {tc_wind_and_pressure_profile['Pmin_mb']:.1f} hPa")
################################################################

################################################################
## Plot that data
from tcwindprofile.plot_windprofile import plot_wind_and_pressure

# unpack
rr_km   = tc_wind_and_pressure_profile['rr_km']
vv_ms   = tc_wind_and_pressure_profile['vv_ms']
pp_mb   = tc_wind_and_pressure_profile['pp_mb']
Vmaxmean_ms   = tc_wind_and_pressure_profile['Vmaxmean_ms']
Rmax_km   = tc_wind_and_pressure_profile['Rmax_km']
V34kt_ms   = tc_wind_and_pressure_profile['V34kt_ms']
R34ktmean_km   = tc_wind_and_pressure_profile['R34ktmean_km']
R0_km   = tc_wind_and_pressure_profile['R0_km']
lat   = tc_wind_and_pressure_profile['lat']
Penv_mb   = tc_wind_and_pressure_profile['Penv_mb']
Pmin_mb   = tc_wind_and_pressure_profile['Pmin_mb']


# then:
Renv_km = R0_km
plot_wind_and_pressure(
    rr_km, vv_ms,
    Rmax_km, Vmaxmean_ms,
    R34ktmean_km, V34kt_ms,
    R0_km, lat,
    rr_km, pp_mb,
    Renv_km, Penv_mb, Pmin_mb,
    save_path='tc_wind_pressure_profiles'
)
################################################################