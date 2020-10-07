import matplotlib.pyplot as plt
import astropy.cosmology as apc
cosmo = apc.Planck15
from loaddata_sdss_xr import *

import astropy.coordinates as coords
from astropy.coordinates import SkyCoord
from scipy.interpolate import griddata
from astropy import units as uxmm
#from sklearn import linear_model
import numpy as np

from scipy.ndimage.filters import gaussian_filter


arcsec = 1/3600. #degrees



from demarcations import *
from Gdiffs import *
from Fits_set import *
from setops import *
from matchspec import *
from loaddata_m2 import *
from ast_func import *
from catmatching_xr import *
from ELObj import *
from XMM3_obj import *
from xraysfr_obj import *
from gsw_3xmm_match import *
catfold='catalogs/'
plt.rc('font', family='serif')





#commid, ind1_m2, ind2_m2phot = commonpts1d(m2[0], m2_photcatids)
m2_photrfluxmatched = m1_modelrflux[ind2_m1phot]
posflux = np.where(m2_photrfluxmatched >0 )[0]
#np.savetxt(catfold+'photmatchinginds.txt', ind2_m2phot,fmt='%s')
def get_massfrac(fibmass, totmass):
    '''
    get the mass fraction of the fibers
    '''
    val_masses = np.where((fibmass > 6) & ( fibmass < 13)  &(totmass > 6) &(totmass < 13))[0]
    inval_masses =[(fibmass < 6) | (fibmass > 13) | (totmass < 6) | (totmass > 13)]
    mass_frac = np.ones_like(fibmass)
    mass_frac[val_masses] = 10**(fibmass[val_masses])/(10**(totmass[val_masses]))
    mass_frac[inval_masses] *= -99
    return mass_frac, val_masses
all_sdss_massfrac, val_massinds  = get_massfrac(sdssobj.all_fibmass, sdssobj.all_sdss_avgmasses)

'''
matching the xray catalog to the gswlc
'''

# %% x-ray
print('matching catalogs')
x3 = XMM3(xmm3,xmm3obs)
coordgswm = SkyCoord(allm2[raind]*u.degree, allm2[decind]*u.degree)
#coordchand = SkyCoord(ra95*u.degree, dec95*u.degree)
'''
actmatch_3xmm_gsw2 = catmatch_act(x3.ra,x3.dec,m2Cat_GSW_3xmm.allra,m2Cat_GSW.alldec, m2_photrfluxmatched, x3.fullflux)
#np.array(match_7), np.array(match_7_dists), np.array(matchxflux), np.array(matchedind), np.array(matchrflux), np.array(matchra_diff), np.array(matchdec_diff)
idm2 = actmatch_3xmm_gsw2[0]
goodm2 = actmatch_3xmm_gsw2[3]
d2d2m = actmatch_3xmm_gsw2[1]
radiff = actmatch_3xmm_gsw2[5]
decdiff = actmatch_3xmm_gsw2[6]
'''
idm2 = np.loadtxt(catfold+'xmm3gswmatch1indnew.txt')
goodm2 = np.loadtxt(catfold+'xmm3gswmatch1goodnew.txt')
d2d1m = np.loadtxt(catfold+'xmm3gswmmatchd2d1new.txt')
decdiff = np.loadtxt(catfold+'xmm3gswmatchdeltadecnew.txt')
radiff = np.loadtxt(catfold+'xmm3gswmatchdeltaranew.txt')

x3.idm2 = np.int64(idm2)
x3.good_med = np.int64(goodm2)
x3.medmatchinds, x3.medmatchsetids, x3.medmatchobsinds, x3.medmatchobsids, x3.medexptimes = x3.obsmatching(x3.good_med)
#x3.medmatchindsall, x3.medmatchsetidsall = x3.obsmatching(np.int64(np.ones_like(x3.ra)))

x3.goodobsids = np.array(x3.obsids[np.where(x3.medmatchinds !=0)[0]])
#np.savetxt(catfold+'sampleobstimes.txt', np.array(x3.goodobsids), fmt='%s')
x3.medtimes_all,x3.medtimes_allt, x3.obsids_allt = x3.singtimearr(np.int64(np.ones_like(x3.tpn)))
x3.logmedtimes_all = np.log10(x3.medtimes_all)
x3.medtimes_allfilt = np.where((x3.logmedtimes_all>4.1)&(x3.logmedtimes_all <4.5))
x3.medcovgobs = x3.obsids[x3.medtimes_allfilt]
#np.savetxt(catfold+'goodobsalltimes.txt',np.array(x3.medcovgobs), fmt='%s')

x3.goodra = np.array(x3.ra[x3.good_med])
x3.gooddec = np.array(x3.dec[x3.good_med])
#x3.allxmm3times, x3.allxmm3timesobs = x3.obsmatching(np.int64(np.ones(x3.ra.size)))
x3.medtimes, x3.medtimesobs, x3.obsids_matches = x3.singtimearr(x3.medmatchinds)
#x3.medtimes, x3.medtimesobs, x3.obsids_matches = x3.singtimearr(x3.medmatchindsobsinds)

x3.logmedtimes = np.log10(x3.medexptimes)
x3.logmedtimesobs = np.log10(x3.medtimesobs)
x3.medtimefilt = np.where((x3.logmedtimes > 4.1) & (x3.logmedtimes < 4.5))[0]
x3.medtimeobsfilt = np.where((x3.logmedtimesobs >4.1) & (x3.logmedtimesobs < 4.5))[0]

resolve_eco_filt = np.where( ( (x3.obs_ra > (9*15-1) ) & (x3.obs_ra < (16*15+1) ) & (x3.obs_dec > -1) &(x3.obs_dec < 51)) | #eco
                ( ( (x3.obs_ra > (22*15-1)) | (x3.obs_ra<3*15+1) )  & (x3.obs_dec > -2.25) &(x3.obs_dec < 2.25 )  ) | #resolve spring
                ( (x3.obs_ra> (8.75*15-1 ) ) &(x3.obs_ra<15.75*15 +1)&(x3.obs_dec> -1 ) &(x3.obs_dec<6)) )[0] #resolve fall
resolve_eco_tpn = x3.tpn[resolve_eco_filt]
resolve_eco_tmos1 = x3.tmos1[resolve_eco_filt]
resolve_eco_tmos2 = x3.tmos2[resolve_eco_filt]
resolve_eco_ra = x3.obs_ra[resolve_eco_filt]
resolve_eco_dec = x3.obs_dec[resolve_eco_filt]
resolve_eco_obsids = x3.obsids[resolve_eco_filt]


x3.goodratimefilt = x3.goodra[x3.medtimefilt]
x3.gooddectimefilt = x3.gooddec[x3.medtimefilt]
#np.savetxt(catfold+'goodobstimes.txt',np.array(x3.goodobsids[x3.medtimeobsfilt]), fmt='%s')
#x3.medtimefilt = np.where((x3.logmedtimes > 3.5) & (x3.logmedtimes <3.9))[0] #shorter, s82x-esque exposures
x3.medtimefilt_all = np.where(x3.logmedtimes >0 )[0] #all times

x3.softflux_filt = x3.softflux[x3.good_med][x3.medtimefilt]
x3.hardflux_filt = x3.hardflux[x3.good_med][x3.medtimefilt]
x3.hardflux2_filt = x3.hardflux2[x3.good_med][x3.medtimefilt]
x3.fullflux_filt = x3.fullflux[x3.good_med][x3.medtimefilt]
x3.efullflux_filt = x3.efullflux[x3.good_med][x3.medtimefilt]
x3.qualflag_filt = x3.qualflag[x3.good_med][x3.medtimefilt]
x3.ext_filt = x3.ext[x3.good_med][x3.medtimefilt_all]

x3.softflux_all = x3.softflux[x3.good_med][x3.medtimefilt_all]
x3.hardflux_all = x3.hardflux[x3.good_med][x3.medtimefilt_all]
x3.hardflux2_all = x3.hardflux2[x3.good_med][x3.medtimefilt_all]
x3.fullflux_all = x3.fullflux[x3.good_med][x3.medtimefilt_all]
x3.efullflux_all = x3.efullflux[x3.good_med][x3.medtimefilt_all]
x3.qualflag_all = x3.qualflag[x3.good_med][x3.medtimefilt_all]
x3.ext_all = x3.ext[x3.good_med][x3.medtimefilt_all]

#%% GSW loading

#a1Cat_GSW_3xmm = GSWCatmatch3xmm(x3,x3.ida[x3.good_all][x3.alltimefilt], a1, redshift_a1, alla1)
m2Cat_GSW_qsos = GSWCat( np.arange(len(m2[0])), m2, redshift_m2, allm2, sedflag=1)

m2Cat_GSW = GSWCat( np.arange(len(m2[0])), m2, redshift_m2, allm2)


m2Cat_GSW_3xmm = GSWCatmatch3xmm(x3.idm2[x3.medtimefilt], m2, redshift_m2, allm2, x3.qualflag_filt,
                                 x3.fullflux_filt, x3.efullflux_filt, 
                                 x3.hardflux_filt, x3.hardflux2_filt, x3.softflux_filt, x3.ext_filt)
m2Cat_GSW_3xmm_all = GSWCatmatch3xmm( x3.idm2[x3.medtimefilt_all], m2, 
                                     redshift_m2, allm2, x3.qualflag_all, x3.fullflux_all, 
                                     x3.efullflux_all,x3.hardflux_all, 
                                     x3.hardflux2_all, x3.softflux_all, x3.ext_all)
m2Cat_GSW_3xmm.exptimes = x3.logmedtimes[x3.medtimefilt][m2Cat_GSW_3xmm.sedfilt]
m2Cat_GSW_3xmm_all.exptimes = x3.logmedtimes[x3.medtimefilt_all][m2Cat_GSW_3xmm_all.sedfilt]
m2Cat_GSW_3xmm.matchxrayra = x3.goodra[x3.medtimefilt][m2Cat_GSW_3xmm.sedfilt]
m2Cat_GSW_3xmm.matchxraydec = x3.gooddec[x3.medtimefilt][m2Cat_GSW_3xmm.sedfilt]
#m2Cat_GSW_3xmm.xraysourceids = x3.sourceids[x3.good_med][x3.medtimefilt][m2Cat_GSW_3xmm.sedfilt]
m2Cat_GSW_3xmm.xrayobsids =  x3.obsids_matches[x3.medtimefilt][m2Cat_GSW_3xmm.sedfilt]
m2Cat_GSW_3xmm_all.matchxrayra = x3.goodra[x3.medtimefilt_all][m2Cat_GSW_3xmm_all.sedfilt]
m2Cat_GSW_3xmm_all.matchxraydec = x3.gooddec[x3.medtimefilt_all][m2Cat_GSW_3xmm_all.sedfilt]

'''
np.savetxt(catfold+'xmm3gswamatch1ind.txt',ida1)
np.savetxt(catfold+'xmm3gswamatch1good.txt',gooda1)
np.savetxt(catfold+'xmm3gswamatchd2d1.txt',d2d1a)

np.savetxt(catfold+'xmm3gswmmatch1ind.txt',idm2)
np.savetxt(catfold+'xmm3gswmmatch1good.txt',goodm2)
np.savetxt(catfold+'xmm3gswmmatchd2d1.txt',d2d1m)

np.savetxt(catfold+'xmm3gswdmatch1ind.txt',idd1)
np.savetxt(catfold+'xmm3gswdmatch1good.txt',goodd1)
np.savetxt(catfold+'xmm3gswdmatchd2d1.txt',d2d1d)

'''

#%% mpa matching

mpa_spec_m2_3xmm = MPAJHU_Spec(m2Cat_GSW_3xmm, sdssobj)
mpa_spec_qsos = MPAJHU_Spec(m2Cat_GSW_qsos, sdssobj, sedtyp=1)
mpa_spec_m2_3xmm_all = MPAJHU_Spec(m2Cat_GSW_3xmm_all, sdssobj)
mpa_spec_allm2 = MPAJHU_Spec(m2Cat_GSW, sdssobj, find=False, gsw=True)
#gsw_2matching_info = np.vstack([mpa_spec_allm2.spec_inds_prac, mpa_spec_allm2.spec_plates_prac, mpa_spec_allm2.spec_fibers_prac, mpa_spec_allm2.spec_mass_prac, mpa_spec_allm2.make_prac ])
mpa_spec_allm2.spec_inds_prac, mpa_spec_allm2.spec_plates_prac, mpa_spec_allm2.spec_fibers_prac, mpa_spec_allm2.spec_mass_prac, mpa_spec_allm2.make_prac = np.loadtxt(catfold+'gsw2_dr7_matching_info.txt')

inds_comm, gsw_sedfilt_mpamake,mpamake_gsw_sedfilt=np.intersect1d(m2Cat_GSW.sedfilt, mpa_spec_allm2.make_prac, return_indices=True)
#new way of setting up gsw_3xmm_match filters sed flag beforehand so some of 
#the previous objects are now eing leftout (all QSOs/bad SEDfits so not a problem)
#need to combine inds from m2Cat_GSW.sedfilt ana mpa_spec_allm2.make_prac




#spec_inds_m2_3xmm, spec_plates_m2_3xmm, spec_fibers_m2_3xmm, specmass_m2_3xmm, make_m2_3xmm, miss_m2_3xmm, ids_sp_m2_3xmm  = matchspec_full(m2Cat_GSW_3xmm, sdssobj)
#spec_inds_m2_3xmm, spec_plates_m2_3xmm, spec_fibers_m2_3xmm, specmass_m2_3xmm, make_m2_3xmm, miss_m2_3xmm, ids_sp_m2_3xmm  = matchspec_prac(m2Cat_GSW_3xmm, sdssobj)
#spec_inds_m2_3xmm_all, spec_plates_m2_3xmm_all, spec_fibers_m2_3xmm_all, specmass_m2_3xmm_all, make_m2_3xmm_all, miss_m2_3xmm_all, ids_sp_m2_3xmm_all  = matchspec_prac(m2Cat_GSW_3xmm_all, sdssobj)

#spec_inds_allm2, spec_plates_allm2, spec_fibers_allm2, mass_allm2,make_allm2 = np.loadtxt(catfold+'gsw_dr7_matching_info.txt')
mpa_spec_allm2.spec_inds_prac = np.int64(mpa_spec_allm2.spec_inds_prac).reshape(-1)
mpa_spec_allm2.make_prac = np.int64(mpa_spec_allm2.make_prac).reshape(-1)
mpa_spec_qsos.spec_inds_prac = np.int64(mpa_spec_qsos.spec_inds_prac).reshape(-1)
mpa_spec_qsos.make_prac = np.int64(mpa_spec_qsos.make_prac).reshape(-1)
mpa_spec_m2_3xmm.spec_inds_prac = np.int64(mpa_spec_m2_3xmm.spec_inds_prac ).reshape(-1)
mpa_spec_m2_3xmm_all.spec_inds_prac  = np.int64(mpa_spec_m2_3xmm_all.spec_inds_prac ).reshape(-1)

def latextable(table):
    for row in table:
        out= '%s & '*(len(row)-1) +'%s \\\\'
        print(out % tuple(row))


'''
actual analysis begins below
'''

#%% Emission line objects
EL_qsos = ELObj(mpa_spec_qsos.spec_inds_prac , sdssobj, mpa_spec_qsos.make_prac,m2Cat_GSW_qsos,gsw=True)
EL_m2 = ELObj(mpa_spec_allm2.spec_inds_prac , sdssobj, gsw_sedfilt_mpamake,m2Cat_GSW,gsw=True, dustbinning=True)

EL_3xmm  = ELObj(mpa_spec_m2_3xmm.spec_inds_prac , sdssobj, mpa_spec_m2_3xmm.make_prac,m2Cat_GSW_3xmm, xr=True)
EL_3xmm_all = ELObj(mpa_spec_m2_3xmm_all.spec_inds_prac , sdssobj, mpa_spec_m2_3xmm_all.make_prac, m2Cat_GSW_3xmm_all, xr=True)


#%% X-ray lum sfr filtering
'''
XRAY LUM -SFR
'''


softxray_xmm = Xraysfr(m2Cat_GSW_3xmm.softlumsrf, m2Cat_GSW_3xmm, 
                       mpa_spec_m2_3xmm.make_prac[EL_3xmm.bpt_sn_filt], 
                       EL_3xmm.bptagn,EL_3xmm.bptsf, 'soft')
hardxray_xmm = Xraysfr(m2Cat_GSW_3xmm.hardlumsrf, m2Cat_GSW_3xmm, 
                       mpa_spec_m2_3xmm.make_prac[EL_3xmm.bpt_sn_filt], 
                       EL_3xmm.bptagn,EL_3xmm.bptsf,'hard')
fullxray_xmm = Xraysfr(m2Cat_GSW_3xmm.fulllumsrf, m2Cat_GSW_3xmm,
                       mpa_spec_m2_3xmm.make_prac[EL_3xmm.bpt_sn_filt], 
                       EL_3xmm.bptagn, EL_3xmm.bptsf, 'full')
fullxray_xmm_bptplus = Xraysfr(m2Cat_GSW_3xmm.fulllumsrf, m2Cat_GSW_3xmm,
                       mpa_spec_m2_3xmm.make_prac[EL_3xmm.bpt_sn_filt], 
                       EL_3xmm.bptplsagn, EL_3xmm.bptplssf, 'full')


fullxray_xmm_dr7 = Xraysfr(m2Cat_GSW_3xmm.fulllumsrf, m2Cat_GSW_3xmm, mpa_spec_m2_3xmm.make_prac,  EL_3xmm.bptagn, EL_3xmm.bptsf, 'full')

softxray_xmm_all = Xraysfr(m2Cat_GSW_3xmm_all.softlumsrf, m2Cat_GSW_3xmm_all, 
                           mpa_spec_m2_3xmm_all.make_prac[EL_3xmm_all.bpt_sn_filt], 
                           EL_3xmm_all.bptagn,EL_3xmm_all.bptsf, 'soft')
hardxray_xmm_all = Xraysfr(m2Cat_GSW_3xmm_all.hardlumsrf, m2Cat_GSW_3xmm_all,
                           mpa_spec_m2_3xmm_all.make_prac[EL_3xmm_all.bpt_sn_filt],
                           EL_3xmm_all.bptagn,EL_3xmm_all.bptsf, 'hard')
fullxray_xmm_all = Xraysfr(m2Cat_GSW_3xmm_all.fulllumsrf, m2Cat_GSW_3xmm_all, 
                           mpa_spec_m2_3xmm_all.make_prac[EL_3xmm_all.bpt_sn_filt],
                           EL_3xmm_all.bptagn, EL_3xmm_all.bptsf, 'full')

fullxray_xmm_all_bptplus = Xraysfr(m2Cat_GSW_3xmm_all.fulllumsrf, m2Cat_GSW_3xmm_all, 
                                   mpa_spec_m2_3xmm_all.make_prac[EL_3xmm_all.bpt_sn_filt], 
                                   EL_3xmm_all.bptplsagn, EL_3xmm_all.bptplssf, 'full')


softxray_xmm_no = Xraysfr(m2Cat_GSW_3xmm.softlumsrf, m2Cat_GSW_3xmm, mpa_spec_m2_3xmm.make_prac[EL_3xmm.not_bpt_sn_filt_bool], [], [], 'soft')
hardxray_xmm_no = Xraysfr(m2Cat_GSW_3xmm.hardlumsrf, m2Cat_GSW_3xmm, mpa_spec_m2_3xmm.make_prac[EL_3xmm.not_bpt_sn_filt_bool], [], [], 'hard')
fullxray_xmm_no = Xraysfr(m2Cat_GSW_3xmm.fulllumsrf, m2Cat_GSW_3xmm, mpa_spec_m2_3xmm.make_prac[EL_3xmm.not_bpt_sn_filt_bool], [], [], 'full')
fullxray_xmm_all_no = Xraysfr(m2Cat_GSW_3xmm_all.fulllumsrf, m2Cat_GSW_3xmm_all, mpa_spec_m2_3xmm_all.make_prac[EL_3xmm_all.not_bpt_sn_filt_bool], [], [], 'full')


#%% refiltering emission line objects by x-ray properties
xmm3eldiagmed_xrfilt = ELObj(mpa_spec_m2_3xmm.spec_inds_prac[EL_3xmm.bpt_sn_filt][fullxray_xmm.valid][fullxray_xmm.likelyagn_xr], 
                             sdssobj,
                             mpa_spec_m2_3xmm.make_prac[EL_3xmm.bpt_sn_filt][fullxray_xmm.valid][fullxray_xmm.likelyagn_xr], 
                             m2Cat_GSW_3xmm,xr=True)

xmm3eldiagmed_xrfiltbptplus = ELObj(mpa_spec_m2_3xmm.spec_inds_prac[EL_3xmm.bpt_sn_filt][fullxray_xmm_bptplus.valid][fullxray_xmm_bptplus.likelyagn_xr], sdssobj,
                             mpa_spec_m2_3xmm.make_prac[EL_3xmm.bpt_sn_filt][fullxray_xmm_bptplus.valid][fullxray_xmm_bptplus.likelyagn_xr], m2Cat_GSW_3xmm,xr=True)

xmm3eldiagmed_xrsffilt = ELObj(mpa_spec_m2_3xmm.spec_inds_prac[EL_3xmm.bpt_sn_filt][fullxray_xmm.valid][fullxray_xmm.likelysf], sdssobj,
                             mpa_spec_m2_3xmm.make_prac[EL_3xmm.bpt_sn_filt][fullxray_xmm.valid][fullxray_xmm.likelysf], m2Cat_GSW_3xmm,xr=True)

xmm3eldiagmed_xrfilt_all =  ELObj(mpa_spec_m2_3xmm_all.spec_inds_prac[EL_3xmm_all.bpt_sn_filt][fullxray_xmm_all.valid][fullxray_xmm_all.likelyagn_xr], sdssobj,
                                  mpa_spec_m2_3xmm_all.make_prac[EL_3xmm_all.bpt_sn_filt][fullxray_xmm_all.valid][fullxray_xmm_all.likelyagn_xr], m2Cat_GSW_3xmm_all, xr=True)
xmm3eldiagmed_xrfiltbptplus_all =  ELObj(mpa_spec_m2_3xmm_all.spec_inds_prac[EL_3xmm_all.bpt_sn_filt][fullxray_xmm_all_bptplus.valid][fullxray_xmm_all_bptplus.likelyagn_xr], 
                                         sdssobj,
                                  mpa_spec_m2_3xmm_all.make_prac[EL_3xmm_all.bpt_sn_filt][fullxray_xmm_all_bptplus.valid][fullxray_xmm_all_bptplus.likelyagn_xr], 
                                  m2Cat_GSW_3xmm_all, xr=True)





#groups1_3xmmm, nonagn_3xmmm_xrfilt, agn_3xmmm_xrfilt = xmm3eldiagmed_xrfilt.get_bpt1_groups()
#groups1_3xmmmplus, nonagn_3xmmm_xrfilt_bptplus, agn_3xmmm_xrfilt_bptplus = xmm3eldiagmed_xrfilt.get_bptplus_groups()
#groups1_3xmmmplus, nonagn_3xmmm_xrfilt_bptplus, agn_3xmmm_xrfilt_bptplus = xmm3eldiagmed_xrfiltbptplus.get_bptplus_groups()#

#groups1_3xmmmplusnii, nonagn_3xmmm_xrfilt_bptplusnii, agn_3xmmm_xrfilt_bptplusnii = xmm3eldiagmed_xrfilt.get_bptplus_niigroups()
#groups1_3xmmmtbt, nonagn_3xmmm_xrfilttbt, agn_3xmmm_xrfilttbt = xmm3eldiagmed_xrfilt.get_bpt1_groups(filt=xmm3eldiagmed_xrfilt.bpt_sn_filt[xmm3eldiagmed_xrfilt.tbt_filt])
#groups1_3xmmmvo87_1, nonagn_3xmmm_xrfiltvo87_1, agn_3xmmm_xrfiltvo87_1 = xmm3eldiagmed_xrfilt.get_bpt1_groups(filt=xmm3eldiagmed_xrfilt.bpt_sn_filt[xmm3eldiagmed_xrfilt.vo87_1_filt])
#groups1_3xmmmvo87_2, nonagn_3xmmm_xrfiltvo87_2, agn_3xmmm_xrfiltvo87_2 = xmm3eldiagmed_xrfilt.get_bpt1_groups(filt=xmm3eldiagmed_xrfilt.bpt_sn_filt[xmm3eldiagmed_xrfilt.vo87_2_filt])

#groups1_3xmmmtbtonly, nonagn_3xmmm_xrfilttbtonly, agn_3xmmm_xrfilttbtonly = xmm3eldiagmed_xrfilt.get_bpt1_groups(filt=xmm3eldiagmed_xrfilt.tbt_filtall)

#lowestmassgals = np.where(xmm3eldiagmed_xrfilt.mass[nonagn_3xmmm_xrfilt] <9.2)
#lowssfr = np.where(xmm3eldiagmed_xrfilt.ssfr[nonagn_3xmmm_xrfilt] < -11)[0]
#highssfrbptagn = np.where(xmm3eldiagmed_xrfilt.ssfr[agn_3xmmm_xrfilt]>-10)[0]


#groups1_3xmmm_all, nonagn_3xmmm_all_xrfilt, agn_3xmmm_all_xrfilt = xmm3eldiagmed_xrfilt_all.get_bpt1_groups()
#groups1_3xmmm_alltbt, nonagn_3xmmm_all_xrfilttbt, agn_3xmmm_all_xrfilttbt = xmm3eldiagmed_xrfilt_all.get_bpt1_groups(filt=xmm3eldiagmed_xrfilt_all.bpt_sn_filt[xmm3eldiagmed_xrfilt_all.tbt_filt])
#groups1_3xmmm_xrsffilt, nonagn_3xmmm_xrsffilt, agn_3xmmm_xrsffilt = xmm3eldiagmed_xrsffilt.get_bpt1_groups()

#groups1_3xmmmbptplus_all, nonagn_3xmmmbptplus_all_xrfilt, agn_3xmmmbptplus_all_xrfilt = xmm3eldiagmed_xrfiltbptplus_all.get_bpt1_groups()
#groups1_3xmmmbptplus_all_bptplus, nonagn_3xmmmbptplus_all_xrfilt_bptplus, agn_3xmmmbptplus_all_xrfilt_bptplus = xmm3eldiagmed_xrfiltbptplus_all.get_bptplus_groups()


#obs_gals_inds = [1,2,4,5,6,8,9,10,12,13,14,16,21,52,60,76,78,81,82,83,84,85,86,87]


#unclass = mpa_spec_m2_3xmm_all.make_prac[EL_3xmm_all.not_bpt_sn_filt][fullxray_xmm_all_no.likelyagn_xr]
#unclass_EL_3xmm_all_xragn = EL_3xmm_all.not_bpt_sn_filt[fullxray_xmm_all_no.likelyagn_xr]
#muse_samp_inds = [3,6, 28, 57] #7,27, 46
#unclass_muse_samp_inds = [22,23,57,104,210]

#het_samp_inds = [11, 13, 16,  21, 22,  79, 82, 85, 87] #9,10, 14, 20, 77
#unclass_het_samp_inds = [68, 87, 91, 102, 110, 483, 487, 497, 510, 523, 525, 526, 534]


#%% Gdiffs

'''
Gdiffs
'''
xmm3inds = m2Cat_GSW_3xmm.inds[m2Cat_GSW_3xmm.sedfilt][mpa_spec_m2_3xmm.make_prac][EL_3xmm.bpt_sn_filt][fullxray_xmm.valid][fullxray_xmm.likelyagn_xr]
xmm3ids = m2Cat_GSW_3xmm.ids[mpa_spec_m2_3xmm.make_prac][EL_3xmm.bpt_sn_filt][fullxray_xmm.valid][fullxray_xmm.likelyagn_xr]
gswids = m2[0][mpa_spec_allm2.make_prac][EL_m2.bpt_sn_filt]
covered_gsw = np.int64(np.loadtxt('catalogs/matched_gals_s82_fields.txt'))
covered_gsw_x3 = np.int64(np.loadtxt('catalogs/xraycov/matched_gals_gsw2xmm3_xrcovg_fields_set.txt'))

xmm3gdiff = Gdiffs(xmm3ids, gswids, xmm3eldiagmed_xrfilt, EL_m2)
xmm3gdiff.get_filt(covered_gsw_x3)
commdiffidsxmm3, xmm3diffcomm, xmm3gswdiffcomm = commonpts1d(xmm3ids, gswids[covered_gsw_x3])
xmm3gdiff.nearbyx(xmm3gswdiffcomm)
xmm3gdiff.getdist_by_thresh(3.0)
binnum = 60
contaminations_xmm3 = xmm3gdiff.xrgswfracs[:,binnum]
contaminations_xmm3_2 = xmm3gdiff.xrgswfracs[:, 40]
contaminations_xmm3_25 = xmm3gdiff.xrgswfracs[:, 50]
contaminations_xmm3_3 = xmm3gdiff.xrgswfracs[:, 60]
contaminations_xmm3_35 = xmm3gdiff.xrgswfracs[:, 70]
contaminations_xmm3_4 = xmm3gdiff.xrgswfracs[:, 80]
xmm3gdiff.interpdistgrid(11,11,50,method='linear')

#%% sfrm
'''
match sfr
'''
kmnclust = np.loadtxt('catalogs/samir_kmeans_comb3.dat', unpack=True)
kmnclust1 =  kmnclust[0]
val1 = np.where(kmnclust1 != 0 )[0]
sy2_1 = np.where(kmnclust1==1)[0]
liner2_1 = np.where(kmnclust1==2)[0]
sf_1 = np.where(kmnclust1==3)[0]


kmnclust2 =  kmnclust[1]
'''
val2 = np.where(kmnclust2 != 0 )[0]
sy2_1 = np.where(kmnclust2==1)[0]
liner2_1 = np.where(kmnclust2==2)[0]
sf_1 = np.where(kmnclust2==3)[0]
'''
from sfrmatch import SFRMatch

sfrm_gsw2 = SFRMatch(EL_m2,EL_m2.bpt_EL_gsw_df,
                     EL_m2.plus_EL_gsw_df, EL_m2.neither_EL_gsw_df)

sfrm_gsw2.get_highsn_match_only(EL_m2.bptplsagn, EL_m2.bptplssf, 
                                EL_m2.bptplsnii_sf, EL_m2.bptplsnii_agn, 
                                load=True,  sncut=2, with_av=True)#, fname='_second_')
sfrm_gsw2.subtract_elflux(sncut=2,  halphbeta_sncut=2)


sfrm_gsw2_sec = SFRMatch(EL_m2,EL_m2.bpt_EL_gsw_df,
                     EL_m2.plus_EL_gsw_df, EL_m2.neither_EL_gsw_df)

sfrm_gsw2_sec.get_highsn_match_only(EL_m2.bptplsagn, EL_m2.bptplssf, 
                                EL_m2.bptplsnii_sf, EL_m2.bptplsnii_agn, 
                                load=True,  sncut=2, with_av=True, fname='_second_')
sfrm_gsw2_sec.subtract_elflux(sncut=2,  halphbeta_sncut=2)


val2_sii_doub= np.where((kmnclust1 != 0) &(sfrm_gsw2.allagn_df.sii6717flux_sub_sn>2) &(sfrm_gsw2.allagn_df.sii6731flux_sub_sn>2))[0]
sy2_1_sii_doub = np.where((kmnclust1==1) &(sfrm_gsw2.allagn_df.sii6717flux_sub_sn>2) &(sfrm_gsw2.allagn_df.sii6731flux_sub_sn>2))[0]
sf_1_sii_doub = np.where((kmnclust1==3) &(sfrm_gsw2.allagn_df.sii6717flux_sub_sn>2) &(sfrm_gsw2.allagn_df.sii6731flux_sub_sn>2))[0]
liner2_1_sii_doub = np.where((kmnclust1==2) &(sfrm_gsw2.allagn_df.sii6717flux_sub_sn>2) &(sfrm_gsw2.allagn_df.sii6731flux_sub_sn>2))[0]


val2_oi_3 =  np.where((kmnclust1 != 0) &(sfrm_gsw2.allagn_df.oiflux_sub_sn>3) )[0]
sy2_1_oi_3 = np.where((kmnclust1==1) &(sfrm_gsw2.allagn_df.oiflux_sub_sn>3) )[0]
sf_1_oi_3 = np.where((kmnclust1==3) &(sfrm_gsw2.allagn_df.oiflux_sub_sn>3) )[0]
liner2_1_oi_3 = np.where((kmnclust1==2) &(sfrm_gsw2.allagn_df.oiflux_sub_sn>3))[0]



sncut=2
combo_sncut=2, 
delta_ssfr_cut=-0.7
minmass=10.2
maxmass=10.4, 
d4000_cut=1.6


upperoiiilum=40.14
loweroiiilum=40.06

upperU_cut=-0.2
lowerU_cut=-0.3,


filts = {'delta_ssfr': {'cut':[delta_ssfr_cut]},
             #'mass':{'cut': [minmass,maxmass]},
             #'d4000':{'cut':[d4000_cut]},
             #'oiiilum': {'cut':[loweroiiilum,upperoiiilum]},
             #'oiiilum_sub_dered': {'cut':[loweroiiilum,upperoiiilum]},
             #'U_sub': {'cut':[lowerU_cut,upperU_cut]},
             #'U': {'cut':[lowerU_cut,upperU_cut]},
             #'qc_sub':{'cut':[lowerqc_cut, upperqc_cut]},
             #'q_sub':{'cut':[lowerq_cut, upperq_cut]}
             'sy2_liner_bool':{'cut':[0.5]}
              }
gen_filts = {}
match_filts = {'delta_ssfr': {'cut':[delta_ssfr_cut]},
             #'mass':{'cut': [minmass,maxmass]},
             #'d4000':{'cut':[d4000_cut]},
             #'oiiilum': {'cut':[loweroiiilum,upperoiiilum]},
             #'oiiilum_sub_dered': {'cut':[loweroiiilum,upperoiiilum]},
             #'U_sub': {'cut':[lowerU_cut,upperU_cut]},
             #'U': {'cut':[lowerU_cut,upperU_cut]},
             'sy2_liner_bool':{'cut':[0.5]}
             
             #'qc_sub':{'cut':[lowerq_cut, upperq_cut]},
             #'q_sub':{'cut':[lowerq_cut, upperq_cut]}

              }
line_filts = [['oiflux',sncut],
              ['oiiflux',sncut],
              ['siiflux',sncut],
              ['oiflux_sub',sncut],
              ['oiiflux_sub',sncut],
              ['siiflux_sub',sncut]                      
              ]
line_filts_comb = {'sii_oii_sub':[['siiflux_sub', 'oiiflux_sub'],combo_sncut],
                   'sii_oi_sub':[['siiflux_sub','oiflux_sub'],3],
                   'oi_oii_sub':[['oiflux_sub', 'oiiflux_sub'],combo_sncut],
                   'sii_oii_oi_sub':[['siiflux_sub', 'oiiflux_sub', 'oiflux_sub'], combo_sncut],
                   'sii_oii_ha_hb_sub':[['siiflux_sub','oiiflux_sub','halpflux_sub','hbetaflux_sub'],combo_sncut],
                   #'o32_sub':[['oiii4959flux_sub','oiiflux_sub'], combo_sncut],
                   'siidoub_sub':[['sii6717flux_sub', 'sii6731flux_sub'],combo_sncut ],
                   
                   #'sii_oii':[['siiflux', 'oiiflux'],combo_sncut],
                   #'sii_oi':[['siiflux','oiflux'],combo_sncut],
                   #'oi_oii':[['oiflux', 'oiiflux'],combo_sncut],
                   #'sii_oii_ha_hb':[['siiflux','oiiflux','halpflux','hbetaflux'],combo_sncut],
                   #'siidoub':[['sii6717flux', 'sii6731flux'],combo_sncut ]
                   
                   }
sfrm_gsw2.get_filt_dfs(filts, gen_filts, match_filts, line_filts, line_filts_comb, loweroiiilum=40.0, upperoiiilum=40.2)
#get_filt_dfs(self, sncut=2, combo_sncut=2, 
#                     delta_ssfr_cut=-0.7, 
#                     minmass=10.2, maxmass=10.4, 
#                     d4000_cut=1.6, 
#                     loweroiiilum=40.2, upperoiiilum=40.3, 
#                     upperU_cut=-0.2, lowerU_cut=-0.3,):
sfrm_gsw2.bin_by_bpt(binsize=0.1)



'''
from sfrmatch import SFRMatch

sfrm_gsw2 = SFRMatch(EL_m2.EL_gsw_df,EL_m2.bpt_EL_gsw_df,
                     EL_m2.plus_EL_gsw_df, EL_m2.neither_EL_gsw_df)

sfrm_gsw2.get_highsn_match_only(EL_m2.bptplsagn[:100], EL_m2.bptplssf, 
                                EL_m2.bptplsnii_sf, EL_m2.bptplsnii_agn,
                                load=False, sncut=2, with_av=True, fname='pdtest', balmdecmin=-99)
sfrm_gsw2.subtract_elflux(sncut=2,  halphbeta_sncut=2)
sfrm_gsw2.bin_by_bpt(binsize=0.1)

'''


'''
d4000m_gsw2 = SFRMatch(EL_m2,EL_m2.bpt_EL_gsw_df,
                     EL_m2.plus_EL_gsw_df, EL_m2.neither_EL_gsw_df)

d4000m_gsw2.get_highsn_match_only_d4000(EL_m2.bptplsagn, EL_m2.bptplssf, 
                                EL_m2.bptplsnii_sf, EL_m2.bptplsnii_agn, 
                                load=True, sncut=2, with_av=True)
d4000m_gsw2.subtract_elflux(sncut=2,  halphbeta_sncut=10)
d4000m_gsw2.bin_by_bpt(binsize=0.1)
'''

#%% 
def match_xrgal_to_sfrm_obj(xrids, sfrmids):
    matching_ind_bpt = []
    xrind_bpt = []
    matching_ind_plus = []
    xrind_plus = []
    matching_ind_neither = []
    xrind_neither = []
    for i, xrid in enumerate(xrids):
        match = np.int64(np.where(sfrmids == xrid)[0][0])
        if match <sfrm_gsw2.agns.size:
            matching_ind_bpt.append(match)
            xrind_bpt.append(i)
        elif match <sfrm_gsw2.agns.size+sfrm_gsw2.agns_plus.size:
            matching_ind_plus.append(match-sfrm_gsw2.agns.size)
            xrind_plus.append(i)
        else:
            matching_ind_neither.append(match-sfrm_gsw2.agns.size+sfrm_gsw2.agns_plus.size)
            xrind_neither.append(i)
    return np.array(matching_ind_bpt), np.array(xrind_bpt), np.array(matching_ind_plus), np.array(xrind_plus), np.array(matching_ind_neither), np.array(xrind_neither)

#xmm3all_xr_to_sfrm_bpt, xmm3all_xrind_bpt, xmm3all_xr_to_sfrm_plus,xmm3all_xrind_plus, xmm3all_xr_to_sfrm_neither, xmm3all_xrind_neither = match_xrgal_to_sfrm_obj(xmm3eldiagmed_xrfilt_all.ids[agn_3xmmmbptplus_all_xrfilt_bptplus], sfrm_gsw2.sdssids_sing)
#xmm3_xr_to_sfrm_bpt,xmm3_xrind_bpt, xmm3_xr_to_sfrm_plus,xmm3_xrind_plus, xmm3_xr_to_sfrm_neither, xmm3_xrind_neither = match_xrgal_to_sfrm_obj(xmm3eldiagmed_xrfiltbptplus.ids[agn_3xmmm_xrfilt_bptplus], sfrm_gsw2.sdssids_sing)

#sfrm_gsw2.bin_by_bpt(binsize=0.1)

'''
sfrm_gsw2_100 = SFRMatch(EL_m2)

sfrm_gsw2_100.get_highsn_match_only(agn_gsw_bptplus[:100], nonagn_gsw_bptplus, 
                                nonagn_gsw_bptplusnii, agn_gsw_bptplusnii, 
                                load=True, fname='first100',sncut=2, with_av=True)
sfrm_gsw2_100.subtract_elflux(sncut=2)

sfrm_gsw2_500 = SFRMatch(EL_m2)

sfrm_gsw2_500.get_highsn_match_only(agn_gsw_bptplus[:500], nonagn_gsw_bptplus, 
                                nonagn_gsw_bptplusnii, agn_gsw_bptplusnii, 
                                load=True, fname='first500',sncut=2, with_av=True)
sfrm_gsw2_500.subtract_elflux(sncut=2)
sfrm_gsw2_500.bin_by_bpt(binsize=0.1)
'''

'''
sfrm_gsw2_1000 = SFRMatch(EL_m2)

sfrm_gsw2_1000.get_highsn_match_only(agn_gsw_bptplus[:1000], nonagn_gsw_bptplus, 
                                nonagn_gsw_bptplusnii, agn_gsw_bptplusnii, 
                                load=False, fname='first1000',sncut=2, with_av=True)
sfrm_gsw2_1000.subtract_elflux(sncut=2)
sfrm_gsw2_1000.bin_by_bpt(binsize=0.1)


sfrm_gsw2_2000 = SFRMatch(EL_m2)

sfrm_gsw2_2000.get_highsn_match_only(agn_gsw_bptplus[:2000], nonagn_gsw_bptplus, 
                                nonagn_gsw_bptplusnii, agn_gsw_bptplusnii, 
                                load=False, fname='first2000',sncut=2, with_av=True)
sfrm_gsw2_2000.subtract_elflux(sncut=2)
sfrm_gsw2_2000.bin_by_bpt(binsize=0.1)

'''
#sfrm_3xmm = SFRMatch(EL_3xmm)
#sfrm_3xmm.get_highsn_match_only(agn_3xmmm_plus, nonagn_3xmmm_plus, nonagn_3xmmm_plusnii,
#                                agn_3xmmm_plusnii, load=False, fname='3xmm', sncut=2, with_av =True)
'''
sfrm_gsw2.getmatch_lindist(agn_gsw_bptplus, nonagn_gsw_bptplus, nonagn_gsw_bptplusnii, agn_gsw_bptplusnii, load=True)
sfrm_gsw2.subtract_elflux(sncut=0)
'''

'''
sfrm_gsw2.getsfrmatch_avg(agn_gsw_bptplus, nonagn_gsw_bptplus, nonagn_gsw_bptplusnii, agn_gsw_bptplusnii, load=False, n_avg=1)
sfrm_gsw2.getsfrmatch_avg(agn_gsw_bptplus, nonagn_gsw_bptplus, nonagn_gsw_bptplusnii, agn_gsw_bptplusnii, load=False, n_avg=3)
sfrm_gsw2.getsfrmatch_avg(agn_gsw_bptplus, nonagn_gsw_bptplus, nonagn_gsw_bptplusnii, agn_gsw_bptplusnii, load=False, n_avg=5)
sfrm_gsw2.getsfrmatch_avg(agn_gsw_bptplus, nonagn_gsw_bptplus, nonagn_gsw_bptplusnii, agn_gsw_bptplusnii, load=False, n_avg=10)
sfrm_gsw2.getsfrmatch_avg(agn_gsw_bptplus, nonagn_gsw_bptplus, nonagn_gsw_bptplusnii, agn_gsw_bptplusnii, load=False, n_avg=20)
sfrm_gsw2.getsfrmatch_avg(agn_gsw_bptplus, nonagn_gsw_bptplus, nonagn_gsw_bptplusnii, agn_gsw_bptplusnii, load=False, n_avg=50)
sfrm_gsw2.getsfrmatch_avg(agn_gsw_bptplus, nonagn_gsw_bptplus, nonagn_gsw_bptplusnii, agn_gsw_bptplusnii, load=False, n_avg=100)
'''

#
#sfrm_gsw2.getmatch_avg(agn_gsw_bptplus, nonagn_gsw_bptplus, nonagn_gsw_bptplusnii, agn_gsw_bptplusnii, load=True, n_avg=5)
#sfrm_gsw2.subtract_elflux_avg(nonagn_gsw_bptplus, nonagn_gsw_bptplusnii,sncut=2)
#sfrm_gsw2.getsfrmatch_avg(agn_gsw_bptplus, nonagn_gsw_bptplus, nonagn_gsw_bptplusnii, agn_gsw_bptplusnii, load=True, n_avg=10)
#sfrm_gsw2.getsfrmatch_avg(agn_gsw_bptplus, nonagn_gsw_bptplus, nonagn_gsw_bptplusnii, agn_gsw_bptplusnii, load=True, n_avg=20)
#sfrm_gsw2.getsfrmatch_avg(agn_gsw_bptplus, nonagn_gsw_bptplus, nonagn_gsw_bptplusnii, agn_gsw_bptplusnii, load=True, n_avg=50)
#sfrm_gsw2.getsfrmatch_avg(agn_gsw_bptplus, nonagn_gsw_bptplus, nonagn_gsw_bptplusnii, agn_gsw_bptplusnii, load=True, n_avg=100)

'''
for creating target files
'''
def write_to_fil_obs(filnam):
    f = open(filnam,'w+')
    #f.write("#Name, OBJID, RA, DEC, BPT CAT\n")
    f.write("#Name, OBJID, RA, DEC, Exp time, SN Min, SN Min Line, SN Max, SN Max Line, z\n")

    sn =  np.vstack([xmm3eldiagmed_xrfilt.halp_sn,xmm3eldiagmed_xrfilt.nii_sn,                   xmm3eldiagmed_xrfilt.oiii_sn,xmm3eldiagmed_xrfilt.hbeta_sn])
    snmin = np.min(sn, axis= 0)
    snmax = np.max(sn, axis= 0)
    sncodemin = matchcode(sn, snmin)
    sncodemax = matchcode(sn, snmax)

    filtxmm = mpa_spec_m2_3xmm.make_prac[EL_3xmm.bpt_sn_filt][fullxray_xmm.valid][fullxray_xmm.likelyagn_xr][nonagn_3xmmm_xrfilt]

    for i in range(len(filtxmm)):
        f.write(str(m2Cat_GSW_3xmm.matchra[filtxmm][i])+','+str(m2Cat_GSW_3xmm.matchdec[filtxmm][i])+','+str(m2Cat_GSW_3xmm.matchmjd[filtxmm][i])+ ','+str(m2Cat_GSW_3xmm.matchfiber[filtxmm][i])+','+str(m2Cat_GSW_3xmm.matchplate[filtxmm][i])+'\n')
        #f.write('3XMMHII'+'-'+str(i)+','+str(m2Cat_GSW_3xmm.ids[filtxmm][i])+','+                    str(m2Cat_GSW_3xmm.matchra[filtxmm][i])+','+str(m2Cat_GSW_3xmm.matchdec[filtxmm][i])+
        #                      ','+str(m2Cat_GSW_3xmm.exptimes[filtxmm][i])+',' +               str(snmin[nonagn_3xmmm_xrfilt][i])+','+sncodemin[nonagn_3xmmm_xrfilt][i]+','+str(snmax[nonagn_3xmmm_xrfilt][i])+','+ sncodemax[nonagn_3xmmm_xrfilt][i]+','+str(xmm3eldiagmed_xrfilt.z[nonagn_3xmmm_xrfilt][i])+'\n')

    f.close()
#write_to_fil_obs('sdssquerytable.txt')

codes = {0:'halp', 1:'nii', 2:'oiii', 3:'hbeta'}
def matchcode(sn,sndes):
    code = []
    for i in range(len(sndes)):
        whermin = np.where(sn[:,i] == sndes[i])[0]
        code.append(codes[whermin[0]])
    return np.array(code)

def write_to_fil_obs_supp(filnam):
    f = open(filnam,'w+')
    f.write("#Name, OBJID, RA, DEC, Exp time, SN Min, SN Min Line, SN Max, SN Max Line, z, ssfr \n")
    filtxmm = mpa_spec_m2_3xmm_all.make_prac[EL_3xmm_all.bpt_sn_filt][fullxray_xmm_all.valid][fullxray_xmm_all.likelyagn_xr][nonagn_3xmmm_all_xrfilt]
    sn =  np.vstack([xmm3eldiagmed_xrfilt_all.halp_sn,xmm3eldiagmed_xrfilt_all.nii_sn,xmm3eldiagmed_xrfilt_all.oiii_sn,xmm3eldiagmed_xrfilt_all.hbeta_sn])
    snmin = np.min(sn, axis= 0)
    snmax = np.max(sn, axis= 0)
    sncodemin = matchcode(sn, snmin)
    sncodemax = matchcode(sn, snmax)

    for i in range(len(filtxmm)):
        print(m2Cat_GSW_3xmm_all.matchra[filtxmm][i])
        f.write('3XMMHII'+'-'+str(i)+','+str(m2Cat_GSW_3xmm_all.ids[filtxmm][i])+','+str(m2Cat_GSW_3xmm_all.matchra[filtxmm][i])+','+str(m2Cat_GSW_3xmm_all.matchdec[filtxmm][i])+
                ','+str(m2Cat_GSW_3xmm_all.exptimes[filtxmm][i])+','+str(snmin[nonagn_3xmmm_all_xrfilt][i])+','+
                sncodemin[nonagn_3xmmm_all_xrfilt][i]+','+str(snmax[nonagn_3xmmm_all_xrfilt][i])+','+
                sncodemax[nonagn_3xmmm_all_xrfilt][i]+','+str(xmm3eldiagmed_xrfilt_all.z[nonagn_3xmmm_all_xrfilt][i])+
                ','+str(xmm3eldiagmed_xrfilt_all.ssfr[nonagn_3xmmm_all_xrfilt][i])+'\n')

    f.close()
#write_to_fil_obs_supp('observing_sample_supp_SP19.txt')
