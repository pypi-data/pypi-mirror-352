from pydriftn.Utils import find_which_ccd


ras = [92.253, 91.5417, 90.3174, 88.4417]
decs = [-70.7387, -70.7827, -70.7318, -69.6491]
variables = ['EB', 'Chaotic', 'RR Lyrae', '4140096_shortperiod']
fits_path = 'demo/r_ooi_exp013253.fits'

for ra, dec, v in zip(ras, decs, variables):
    extname = find_which_ccd(fits_path, ra, dec)
    print('{} variable with RA = {} and DEC = {} belongs to {}.'.format(v, ra, dec, extname))