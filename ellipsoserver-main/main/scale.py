import numpy as np
import scipy as sc
import math

from . import formulas

# TODO duplicate function in another file, needs to be removed later
def genList(start, end, points):
    list = np.linspace(start, end, points)
    return list

def interp(materials, uangle, ustart, uend, upts, unit, file):
    
    wl = genList(ustart, uend, upts)
    
    # i need only refX files for interpolation;
    # before interpolate file data, match every file type with correct column and make x,y
    if (file['file_type'] == 'ref1'):
        # in ref1 eV is not even presented
        y = np.array(file['epsRe']) + 1j * np.array(file['epsIm'])
        x = genList(file['first_point_value'], file['last_point_value'], len(y))
    if (file['file_type'] == 'ref2'):
        y = (np.array(file['n']) + 1j * np.array(file['k'])) ** 2
        x = np.array(file['eV'])
    if (file['file_type'] == 'ref3'):
        y = (np.array(file['epsRe']) + 1j * np.array(file['epsIm'])) ** 2
        x = np.array(file['eV'])
    if (file['file_type'] == 'ref4'):
        y = (np.array(file['n']) + 1j * np.array(file['k'])) ** 2
        x = np.array(file['nm'])

    # user wants eV but file material has nm / user wants nm but file material has eV
    # so eV -> nm / nm -> eV ( i don't use another unit) 
    if ( (unit == 'eV' and file['unit_value'] == 'nm') or (unit == 'nm' and file['unit_value'] == 'eV') ):
        wl = formulas.eVnm(wl)

    # linear interpolation of material data (y) accorting to user data (x)
    fPoly = sc.interpolate.interp1d(x, y)
    new_perm = fPoly(wl)
    
    return new_perm
