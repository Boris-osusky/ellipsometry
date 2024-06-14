# nm -> eV / eV -> nm
def eVnm(x):
    h = 6.62607015e-34 #Planck constant
    e = 1.60217663e-19 #elementary charge
    c = 299792458 #speed of light (m/s)
    return ((h*c/e)/x)*1e9

def constantIndex(n, k):
    return ((n + 1j * k)**2)

def cauchy(lbd, A, B, C):
    n = A + B/(lbd**2) + C/(lbd**4)
    return (n**2)

def sellmeier(lbd):
    tmp1 = (1.03961212 * (lbd**2))
    tmp2 = (lbd**2) - 0.0600069867
    tmp3 = (0.231792344 * (lbd**2))
    tmp4 = (lbd**2) - 0.0200179144
    tmp5 = (1.01046945 * (lbd**2))
    tmp6 = (lbd**2) - 103.560653
    n = (tmp1 / tmp2) + (tmp3 / tmp4) + (tmp5 / tmp6) + 1
    return (n**2)
