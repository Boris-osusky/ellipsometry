# vlozenie kniznic
import io
import math        # only real numbers
import cmath       # only complex numbers
import numpy as np # used for numpy 'fast lists'
from matplotlib.figure import Figure
import base64

from . import formulas
from . import scale
from . import file_parser



def get_simulation_image_b64(materials, uangle, ustart, uend, uinc, unit, functions):
    values = simulate(materials, uangle, ustart, uend, uinc, unit)
    data = {}
    for key in functions:
        data[key] = values[key]

    content = plot(values['ulst'], data)
    return base64.b64encode(content.getbuffer()).decode()


def plot(list, data):
    fig = Figure(figsize=(10, 5))

    ax1 = fig.add_subplot(111)
    ax1.set_ylabel('Ψ (°)', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Δ (°)', color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    if 'rs' in data:
        ax1.plot(list, data['rs'], label='Rs', color='lightblue')

    if 'rp' in data:
        ax1.plot(list, data['rp'], label='Rp', color='lightgray')

    if 'psi' in data:
        ax1.plot(list, data['psi'], label='Psi', color='tab:blue')

    if 'delta' in data:
        ax2.plot(list, data['delta'], label='Delta', color='tab:red')

    fig.legend()
    ax1.set_xlabel('Wave length (nm)')
    bytes_image = io.BytesIO()
    fig.tight_layout()
    fig.savefig(bytes_image, format='png', dpi=150)
    bytes_image.seek(0)

    return bytes_image

def kVector(wl, *args):
    if not args:
        return (2*math.pi/wl)
    elif len(args) == 1:
        eps = args[0]
        return (2*math.pi/wl)*cmath.sqrt(eps)
    else:
        raise ValueError("Invalid num of args.")        

def kxVector(lbd, theta, eps):
    return ((2*math.pi)/lbd)*cmath.sqrt(eps)*math.sin(math.radians(theta))

def kzVector(k, kx, *args):
    if not args:
        return cmath.sqrt(k**2 - kx**2)
    elif len(args) == 1:
        eps = args[0]
        return cmath.sqrt(k**2*eps - kx**2)
    else:
        raise ValueError("Invalid num of args.")
    
def chiCalc(kz1, kz2, *args):
    if not args:
        return kz1 / kz2
    elif len(args) == 2:
        eps1, eps2 = args
        return (kz1 / kz2) * (eps2 / eps1)
    else:
        raise ValueError("Invalid num of args.")

def rTECalc(Ms, Mp):
    return ((-Ms[1,0]) / Ms[1,1])

def rTMCalc(Ms, Mp):
    return ((-Mp[1,0]) / Mp[1,1])

def rho(rs, rp):
    return rp / rs

def deltaCalc(rho):
    return (360 - np.angle(rho, deg=True)) % 360

def psiCalc(rho):
    return np.degrees(np.arctan(np.absolute(rho)))

def RsCalc(rs):
    return ((rs.conjugate() * rs).real)

def RpCalc(rp):
    return ((rp.conjugate() * rp).real)

def MatrixTE(kx, eps1, eps2, wl):
    k = kVector(wl)
    kz1 = kzVector(k, kx, eps1)
    kz2 = kzVector(k, kx, eps2)
    chi = chiCalc(kz1, kz2)
    return 0.5 * np.array([[1 + chi, 1 - chi], [1 - chi, 1 + chi]])

def MatrixTM(kx, eps1, eps2, wl):
    k = kVector(wl)
    kz1 = kzVector(k, kx, eps1)
    kz2 = kzVector(k, kx, eps2)
    chi = chiCalc(kz1, kz2, eps1, eps2)
    return 0.5 * np.array([[1 + chi, 1 - chi], [1 - chi, 1 + chi]])

def MatrixHP(kx, eps, thick, wl):
    k = kVector(wl, eps)
    kz = kzVector(k, kx)
    return np.array([[cmath.exp(1j * kz * thick), 0], [0, cmath.exp(-1j * kz * thick)]])

def MatrixTEmodel(eps, thicks, lbd, theta):
    kx = kxVector(lbd, theta, eps[-1])
    Msfinal = MatrixTE(kx, eps[1], eps[0], lbd)
    for j in range(1, len(eps) - 1):
        Ms = MatrixTE(kx, eps[j + 1], eps[j], lbd)
        Mh = MatrixHP(kx, eps[j], thicks[j], lbd)
        Msfinal = Msfinal @ Mh @ Ms
    return Msfinal

def MatrixTMmodel(eps, thicks, lbd, theta):
    kx = kxVector(lbd, theta, eps[-1])
    Mpfinal = MatrixTM(kx, eps[1], eps[0], lbd)
    for j in range(1, len(eps) - 1):
        Mp = MatrixTM(kx, eps[j + 1], eps[j], lbd)
        Mh = MatrixHP(kx, eps[j], thicks[j], lbd)
        Mpfinal = Mpfinal @ Mh @ Mp
    return Mpfinal


def simulate(materials, uangle, ustart=430, uend=820, uinc=2, unit='nm'):
    # TODO - separate elipsometric code (upper) from processing code (lower)
    # TODO - user can enter another graph after print one (while / dowhile if user will not enter exit)
    #      - he will enter graph by modifying some param in 'materials' in userInput.py

    # user range to view
    upts = math.floor((uend - ustart) / uinc + 1)
    ulst = np.linspace(ustart, uend, upts)

    thicks = []
    # ([perm of first layer (substrate)], [perms of second layer], ..., [pemr of last layer (superstrate)])
    eps = []

    # init elipsometrical parameters
    Rs, Rp, Delta, Psi = np.empty_like(ulst), np.empty_like(ulst), np.empty_like(ulst), np.empty_like(ulst)

    # first and last material - must have infinite thick (because its substrate / superstrate)
    materials[0]['thick'] = math.inf
    materials[-1]['thick'] = math.inf

    # remove materials with 0 thick
    materials = list((i for i in materials if i['thick'] != 0))

    for mat in materials:
        thicks.append(mat['thick'])

    # all data -> permitivity (epsilon (eps))
    for material in materials:
        mlst = []
        if material['type'] == 'cauchy':
            # TODO - slow, instead of using for loop, func in formulas.py should return np array with ulst directly
            for lbd in ulst:
                mlst.append(formulas.cauchy(lbd, material['A'], material['B'], material['C']))
        elif material['type'] == 'sellmeier':
            for lbd in ulst:
                mlst.append(formulas.sellmeier(lbd))
        elif material['type'] == 'constant':
            for lbd in ulst:
                mlst.append(formulas.constantIndex(material['n'], material['k']))
        elif material['type'] == 'raw':
            for lbd in ulst:
                mlst.append(material['eps'])
        elif material['type'] == 'file':
            file = file_parser.get_filedata(material['path'])
            if file['file_type'] in ['ref1', 'ref2', 'ref3', 'ref4']:
                mlst = scale.interp(materials, uangle, ustart, uend, upts, unit, file)
            elif file['file_type'] == 'dsp':
                    if file['formula_id'] == 9:
                        for lbd in ulst:
                            mlst.append(formulas.constant( file['parameters']['param_value0'], file['parameters']['param_value1']))	
                    elif file['formula_id'] == 5:
                        for lbd in ulst:
                            mlst.append(formulas.cauchy(lbd, file['parameters']['param_value0'], file['parameters']['param_value1'], file['parameters']['param_value2']))
        else:
            continue
        eps.append(mlst)

    #  intensity reflectances
    # TODO looping is slow and code inside is not atomised yet - SEPARate code
    for i in range(upts):
        # TODO - numpy / faster way to process sublist (next 3 lines)
        ep = []
        for sublist in eps:
            ep.append(sublist[i])

        # core (elipsometric model)
        Ms = MatrixTEmodel(ep, thicks, ulst[i], uangle) # M_TE
        Mp = MatrixTMmodel(ep, thicks, ulst[i], uangle) # M_TM

        rs = rTECalc(Ms, Mp)
        rp = rTMCalc(Ms, Mp)

        rho = rp / rs
        Delta[i] = deltaCalc(rho)
        Psi[i] = psiCalc(rho)

        Rs[i] = RsCalc(rs)
        Rp[i] = RpCalc(rp)

    # Print (ulst / [Delta, Psi, Rs, Rp])
    # plot(ulst, Psi)
    # plot2(ulst, Delta, Psi)

    return {'ulst': ulst, 'delta': Delta, 'psi': Psi, 'rs': Rs, 'rp': Rp}
