"""
precession
"""

import numpy as np
import scipy, scipy.special, scipy.integrate
import sys, os, time
import warnings
import itertools
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)


#### Utilities ####

def flen(x):
    #https://stackoverflow.com/a/26533085
    return getattr(x, '__len__', lambda:1)()


def toarray(*args):
    return np.squeeze(np.array([*args]))


def normalize_nested(x):
    return np.squeeze(x/np.atleast_1d(np.linalg.norm(x, axis=-1))[:,None])


def dot_nested(x,y):
    return np.squeeze(np.diag(np.atleast_1d(np.inner(x,y))))


def sample_unitsphere(N=1):
    vec = np.random.randn(3, N)
    vec /= np.linalg.norm(vec, axis=0)
    return vec.T


def wraproots(coefficientfunction, *args,**kwargs):
    """
    Find roots of a polynomial given coefficients. Wrapper of numpy.roots.

    Parameters
    ----------
    coefficientfunction: callable
        Function returnin the polynomial coefficients ordered from highest to lowest degree.
    *args, **kwargs:
        Parameters of `coefficientfunction`.

    Returns
    -------
    sols: array
        Roots of the polynomial, ordered according to their real part. Complex roots are masked with nans.
    """

    coeffs= coefficientfunction(*args,**kwargs)

    if np.ndim(coeffs)==1:
        sols = np.sort_complex(np.roots(coeffs))
    else:
        sols = np.array([np.sort_complex(np.roots(x)) for x in coeffs.T]).T
    sols = np.real(np.where(np.isreal(sols),sols,np.nan))

    return sols

#### Definitions ####

# TODO: change name to eval_m1?
def mass1(q):
    """
    Mass of the heavier black hole in units of the total mass.

    Call
    ----
    m1 = mass1(q)

    Parameters
    ----------
    q: float
    	Mass ratio: 0<=q<=1.

    Returns
    -------
    m1: float
    	Mass of the primary (heavier) black hole.
    """

    q = toarray(q)
    m1 = 1/(1+q)

    return m1

# TODO: change name to eval_m2?
def mass2(q):
    """
    Mass of the lighter black hole in units of the total mass.

    Call
    ----
    m2 = mass2(q)

    Parameters
    ----------
    q: float
    	Mass ratio: 0<=q<=1.

    Returns
    -------
    m2: float
    	Mass of the secondary (lighter) black hole.
    """

    q = toarray(q)
    m2 = q/(1+q)

    return m2


def masses(q):
    """
    Masses of the two black holes in units of the total mass.

    Call
    ----
    m1,m2 = masses(q)

    Parameters
    ----------
    q: float
    	Mass ratio: 0<=q<=1.

    Returns
    -------
    m1: float
    	Mass of the primary (heavier) black hole.
    m2: float
    	Mass of the secondary (lighter) black hole.
    """


    m1 = mass1(q)
    m2 = mass2(q)

    return toarray(m1, m2)

# TODO: change name to eval_q?
def massratio(m1, m2):
    """
    Mass ratio, 0 < q = m2/m1 < 1.

    Call
    ----
    q = massratio(m1,m2)

    Parameters
    ----------
    m1: float
    	Mass of the primary (heavier) black hole.
    m2: float
    	Mass of the secondary (lighter) black hole.

    Returns
    -------
    q: float
    	Mass ratio: 0<=q<=1.
    """

    m1 = toarray(m1)
    m2 = toarray(m2)
    q = m2 / m1

    return q

# TODO: change name to eval_eta?
def symmetricmassratio(q):
    """
    Symmetric mass ratio eta = m1*m2/(m1+m2)^2 = q/(1+q)^2.

    Call
    ----
    eta = symmetricmassratio(q)

    Parameters
    ----------
    q: float
    	Mass ratio: 0<=q<=1.

    Returns
    -------
    eta: float
    	Symmetric mass ratio 0<=eta<=1/4.
    """

    q = toarray(q)
    eta = q/(1+q)**2

    return eta

# TODO: change name to eval_S1?
def spin1(q,chi1):
    """
    Spin angular momentum of the heavier black hole.

    Call
    ----
    S1 = spin1(q,chi1)

    Parameters
    ----------
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.

    Returns
    -------
    S1: float
    	Magnitude of the primary spin.
    """

    chi1 = toarray(chi1)
    S1 = chi1*(mass1(q))**2

    return S1

# TODO: change name to eval_S2?
def spin2(q,chi2):
    """
    Spin angular momentum of the lighter black hole.

    Call
    ----
    S2 = spin2(q,chi2)

    Parameters
    ----------
    q: float
    	Mass ratio: 0<=q<=1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    S2: float
    	Magnitude of the secondary spin.
    """

    chi2 = toarray(chi2)
    S2 = chi2*(mass2(q))**2

    return S2


def spinmags(q,chi1,chi2):
    """
    Spins of the black holes in units of the total mass.

    Call
    ----
    S1,S2 = spinmags(q,chi1,chi2)

    Parameters
    ----------
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    S1: float
    	Magnitude of the primary spin.
    S2: float
    	Magnitude of the secondary spin.
    """

    S1 = spin1(q,chi1)
    S2 = spin2(q,chi2)

    return toarray(S1,S2)

# TODO: change name to eval_L?
def angularmomentum(r,q):
    """
    Newtonian angular momentum of the binary.

    Call
    ----
    L = angularmomentum(r,q)

    Parameters
    ----------
    r: float
    	Binary separation.
    q: float
    	Mass ratio: 0<=q<=1.

    Returns
    -------
    L: float
    	Magnitude of the Newtonian orbital angular momentum.
    """

    r = toarray(r)
    L = mass1(q)*mass2(q)*r**0.5

    return L

# TODO: change name to eval_v?
def orbitalvelocity(r):
    """
    Newtonian orbital velocity of the binary.

    Call
    ----
    v = orbitalvelocity(r)

    Parameters
    ----------
    r: float
    	Binary separation.

    Returns
    -------
    v: float
    	Newtonian orbital velocity.
    """

    r = toarray(r)
    v= 1/r**0.5

    return v

# TODO: This needs to be merged with eval_r
def orbitalseparation(L, q):
    """
    Orbital separation of the binary.

    Call
    ----
    r = orbitalseparation(L,q)

    Parameters
    ----------
    L: float
    	Magnitude of the Newtonian orbital angular momentum.
    q: float
    	Mass ratio: 0<=q<=1.

    Returns
    -------
    r: float
    	Binary separation.
    """

    L = toarray(L)
    m1, m2 = masses(q)
    r = (L / (m1 * m2))**2

    return r


#### Limits ####

def Jlimits_LS1S2(r,q,chi1,chi2):
    """
    Limits on the magnitude of the total angular momentum due to the vector relation J=L+S1+S2.

    Call
    ----
    Jmin,Jmax = Jlimits_LS1S2(r,q,chi1,chi2)

    Parameters
    ----------
    r: float
    	Binary separation.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    Jmin: float
    	Minimum value of the total angular momentum J.
    Jmax: float
    	Maximum value of the total angular momentum J.
    """

    S1,S2 = spinmags(q,chi1,chi2)
    L = angularmomentum(r,q)
    Jmin = np.maximum.reduce([np.zeros(flen(L)), L-S1-S2, np.abs(S1-S2)-L])
    Jmax = L+S1+S2

    return toarray(Jmin,Jmax)


def kappadiscriminant_coefficients(u,xi,q,chi1,chi2):
    """
    Coefficients of the quintic equation in kappa that defines the spin-orbit resonances.

    Call
    ----
    coeff5,coeff4,coeff3,coeff2,coeff1,coeff0 = kappadiscriminant_coefficients(u,xi,q,chi1,chi2)

    Parameters
    ----------
    u: float
    	Compactified separation 1/(2L).
    xi: float
    	Effective spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    coeff5: float
    	Coefficient to the x^5 term in polynomial.
    coeff4: float
    	Coefficient to the x^4 term in polynomial.
    coeff3: float
    	Coefficient to the x^3 term in polynomial.
    coeff2: float
    	Coefficient to the x^2 term in polynomial.
    coeff1: float
    	Coefficient to the x^1 term in polynomial.
    coeff0: float
    	Coefficient to the x^0 term in polynomial.
    """


    u,q,xi=toarray(u,q,xi)
    S1,S2= spinmags(q,chi1,chi2)

    coeff0 = \
    ( 16 * ( ( -1 + ( q )**( 2 ) ) )**( 2 ) * ( ( ( -1 + ( q )**( 2 ) ) \
    )**( 2 ) * ( S1 )**( 2 ) + -1 * ( q )**( 2 ) * ( xi )**( 2 ) ) * ( ( \
    ( -1 + ( q )**( 2 ) ) )**( 2 ) * ( S2 )**( 2 ) + -1 * ( q )**( 2 ) * \
    ( xi )**( 2 ) ) + ( -32 * q * ( ( 1 + q ) )**( 2 ) * u * xi * ( -5 * \
    ( S1 )**( 2 ) * ( S2 )**( 2 ) + ( ( S2 )**( 4 ) + ( ( q )**( 8 ) * ( \
    ( S1 )**( 4 ) + -5 * ( S1 )**( 2 ) * ( S2 )**( 2 ) ) + ( q * ( ( S1 \
    )**( 4 ) + -1 * ( S2 )**( 4 ) ) + ( ( q )**( 7 ) * ( -1 * ( S1 )**( 4 \
    ) + ( S2 )**( 4 ) ) + ( -1 * ( q )**( 3 ) * ( ( S1 )**( 2 ) + -1 * ( \
    S2 )**( 2 ) ) * ( 3 * ( S1 )**( 2 ) + ( 3 * ( S2 )**( 2 ) + 2 * ( xi \
    )**( 2 ) ) ) + ( ( q )**( 5 ) * ( ( S1 )**( 2 ) + -1 * ( S2 )**( 2 ) \
    ) * ( 3 * ( S1 )**( 2 ) + ( 3 * ( S2 )**( 2 ) + 2 * ( xi )**( 2 ) ) ) \
    + ( ( q )**( 2 ) * ( -1 * ( S1 )**( 4 ) + ( -3 * ( S2 )**( 4 ) + ( 3 \
    * ( S2 )**( 2 ) * ( xi )**( 2 ) + 5 * ( S1 )**( 2 ) * ( 4 * ( S2 )**( \
    2 ) + ( xi )**( 2 ) ) ) ) ) + ( ( q )**( 6 ) * ( -3 * ( S1 )**( 4 ) + \
    ( -1 * ( S2 )**( 4 ) + ( 5 * ( S2 )**( 2 ) * ( xi )**( 2 ) + ( S1 \
    )**( 2 ) * ( 20 * ( S2 )**( 2 ) + 3 * ( xi )**( 2 ) ) ) ) ) + ( q \
    )**( 4 ) * ( 3 * ( S1 )**( 4 ) + ( 3 * ( S2 )**( 4 ) + ( -8 * ( S2 \
    )**( 2 ) * ( xi )**( 2 ) + ( -4 * ( xi )**( 4 ) + -2 * ( S1 )**( 2 ) \
    * ( 15 * ( S2 )**( 2 ) + 4 * ( xi )**( 2 ) ) ) ) ) ) ) ) ) ) ) ) ) ) \
    ) + ( ( u )**( 2 ) * ( -32 * q * ( 1 + q ) * u * xi * ( 4 * ( q )**( \
    9 ) * ( S1 )**( 2 ) * ( 3 * ( S1 )**( 4 ) + ( -8 * ( S1 )**( 2 ) * ( \
    S2 )**( 2 ) + ( S2 )**( 4 ) ) ) + ( 4 * ( S2 )**( 2 ) * ( ( S1 )**( 4 \
    ) + ( -8 * ( S1 )**( 2 ) * ( S2 )**( 2 ) + 3 * ( S2 )**( 4 ) ) ) + ( \
    -1 * q * ( ( S1 )**( 6 ) + ( 21 * ( S1 )**( 4 ) * ( S2 )**( 2 ) + ( \
    43 * ( S1 )**( 2 ) * ( S2 )**( 4 ) + -49 * ( S2 )**( 6 ) ) ) ) + ( ( \
    q )**( 8 ) * ( 49 * ( S1 )**( 6 ) + ( -43 * ( S1 )**( 4 ) * ( S2 )**( \
    2 ) + ( -21 * ( S1 )**( 2 ) * ( S2 )**( 4 ) + -1 * ( S2 )**( 6 ) ) ) \
    ) + ( ( q )**( 7 ) * ( 37 * ( S1 )**( 6 ) + ( 23 * ( S2 )**( 6 ) + ( \
    -4 * ( S2 )**( 4 ) * ( xi )**( 2 ) + ( 5 * ( S1 )**( 4 ) * ( 9 * ( S2 \
    )**( 2 ) + 4 * ( xi )**( 2 ) ) + ( S1 )**( 2 ) * ( -41 * ( S2 )**( 4 \
    ) + 16 * ( S2 )**( 2 ) * ( xi )**( 2 ) ) ) ) ) ) + ( ( q )**( 2 ) * ( \
    23 * ( S1 )**( 6 ) + ( 37 * ( S2 )**( 6 ) + ( 20 * ( S2 )**( 4 ) * ( \
    xi )**( 2 ) + ( -1 * ( S1 )**( 4 ) * ( 41 * ( S2 )**( 2 ) + 4 * ( xi \
    )**( 2 ) ) + ( S1 )**( 2 ) * ( 45 * ( S2 )**( 4 ) + 16 * ( S2 )**( 2 \
    ) * ( xi )**( 2 ) ) ) ) ) ) + ( ( q )**( 6 ) * ( -75 * ( S1 )**( 6 ) \
    + ( 63 * ( S2 )**( 6 ) + ( 48 * ( S2 )**( 4 ) * ( xi )**( 2 ) + ( ( \
    S1 )**( 4 ) * ( 53 * ( S2 )**( 2 ) + -40 * ( xi )**( 2 ) ) + ( S1 \
    )**( 2 ) * ( 23 * ( S2 )**( 4 ) + 24 * ( S2 )**( 2 ) * ( xi )**( 2 ) \
    ) ) ) ) ) + ( ( q )**( 3 ) * ( 63 * ( S1 )**( 6 ) + ( -5 * ( S2 )**( \
    4 ) * ( 15 * ( S2 )**( 2 ) + 8 * ( xi )**( 2 ) ) + ( ( S1 )**( 4 ) * \
    ( 23 * ( S2 )**( 2 ) + 48 * ( xi )**( 2 ) ) + ( S1 )**( 2 ) * ( 53 * \
    ( S2 )**( 4 ) + 24 * ( S2 )**( 2 ) * ( xi )**( 2 ) ) ) ) ) + ( ( q \
    )**( 5 ) * ( -111 * ( S1 )**( 6 ) + ( 3 * ( S2 )**( 6 ) + ( 28 * ( S2 \
    )**( 4 ) * ( xi )**( 2 ) + ( 16 * ( S2 )**( 2 ) * ( xi )**( 4 ) + ( \
    -3 * ( S1 )**( 4 ) * ( 5 * ( S2 )**( 2 ) + 28 * ( xi )**( 2 ) ) + ( \
    S1 )**( 2 ) * ( 27 * ( S2 )**( 4 ) + ( -8 * ( S2 )**( 2 ) * ( xi )**( \
    2 ) + -32 * ( xi )**( 4 ) ) ) ) ) ) ) ) + ( q )**( 4 ) * ( 3 * ( S1 \
    )**( 6 ) + ( ( S1 )**( 4 ) * ( 27 * ( S2 )**( 2 ) + 28 * ( xi )**( 2 \
    ) ) + ( ( S1 )**( 2 ) * ( -15 * ( S2 )**( 4 ) + ( -8 * ( S2 )**( 2 ) \
    * ( xi )**( 2 ) + 16 * ( xi )**( 4 ) ) ) + -1 * ( S2 )**( 2 ) * ( 111 \
    * ( S2 )**( 4 ) + ( 84 * ( S2 )**( 2 ) * ( xi )**( 2 ) + 32 * ( xi \
    )**( 4 ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) + -16 * ( ( q )**( 12 ) * ( S1 \
    )**( 2 ) * ( ( S1 )**( 4 ) + ( -10 * ( S1 )**( 2 ) * ( S2 )**( 2 ) + \
    ( S2 )**( 4 ) ) ) + ( ( S2 )**( 2 ) * ( ( S1 )**( 4 ) + ( -10 * ( S1 \
    )**( 2 ) * ( S2 )**( 2 ) + ( S2 )**( 4 ) ) ) + ( 2 * ( q )**( 11 ) * \
    ( ( S1 )**( 6 ) + ( -22 * ( S1 )**( 4 ) * ( S2 )**( 2 ) + -11 * ( S1 \
    )**( 2 ) * ( S2 )**( 4 ) ) ) + ( q * ( -22 * ( S1 )**( 4 ) * ( S2 \
    )**( 2 ) + ( -44 * ( S1 )**( 2 ) * ( S2 )**( 4 ) + 2 * ( S2 )**( 6 ) \
    ) ) + ( 2 * ( q )**( 9 ) * ( -4 * ( S1 )**( 6 ) + ( ( S2 )**( 6 ) + ( \
    19 * ( S2 )**( 4 ) * ( xi )**( 2 ) + ( 2 * ( S1 )**( 2 ) * ( S2 )**( \
    2 ) * ( 11 * ( S2 )**( 2 ) + ( xi )**( 2 ) ) + ( S1 )**( 4 ) * ( 77 * \
    ( S2 )**( 2 ) + 43 * ( xi )**( 2 ) ) ) ) ) ) + ( 2 * ( q )**( 3 ) * ( \
    ( S1 )**( 6 ) + ( -4 * ( S2 )**( 6 ) + ( 43 * ( S2 )**( 4 ) * ( xi \
    )**( 2 ) + ( ( S1 )**( 4 ) * ( 22 * ( S2 )**( 2 ) + 19 * ( xi )**( 2 \
    ) ) + ( S1 )**( 2 ) * ( 77 * ( S2 )**( 4 ) + 2 * ( S2 )**( 2 ) * ( xi \
    )**( 2 ) ) ) ) ) ) + ( ( q )**( 2 ) * ( ( S1 )**( 6 ) + ( -3 * ( S2 \
    )**( 6 ) + ( 23 * ( S2 )**( 4 ) * ( xi )**( 2 ) + ( -1 * ( S1 )**( 4 \
    ) * ( 61 * ( S2 )**( 2 ) + ( xi )**( 2 ) ) + -1 * ( S1 )**( 2 ) * ( \
    17 * ( S2 )**( 4 ) + 22 * ( S2 )**( 2 ) * ( xi )**( 2 ) ) ) ) ) ) + ( \
    -1 * ( q )**( 10 ) * ( 3 * ( S1 )**( 6 ) + ( -1 * ( S2 )**( 6 ) + ( ( \
    S2 )**( 4 ) * ( xi )**( 2 ) + ( ( S1 )**( 4 ) * ( 17 * ( S2 )**( 2 ) \
    + -23 * ( xi )**( 2 ) ) + ( S1 )**( 2 ) * ( 61 * ( S2 )**( 4 ) + 22 * \
    ( S2 )**( 2 ) * ( xi )**( 2 ) ) ) ) ) ) + ( 2 * ( q )**( 7 ) * ( 6 * \
    ( S1 )**( 6 ) + ( -4 * ( S2 )**( 6 ) + ( 5 * ( S2 )**( 4 ) * ( xi \
    )**( 2 ) + ( 4 * ( S2 )**( 2 ) * ( xi )**( 4 ) + ( -1 * ( S1 )**( 4 ) \
    * ( 88 * ( S2 )**( 2 ) + 67 * ( xi )**( 2 ) ) + ( S1 )**( 2 ) * ( 22 \
    * ( S2 )**( 4 ) + ( -2 * ( S2 )**( 2 ) * ( xi )**( 2 ) + -36 * ( xi \
    )**( 4 ) ) ) ) ) ) ) ) + ( -2 * ( q )**( 5 ) * ( 4 * ( S1 )**( 6 ) + \
    ( -6 * ( S2 )**( 6 ) + ( 67 * ( S2 )**( 4 ) * ( xi )**( 2 ) + ( 36 * \
    ( S2 )**( 2 ) * ( xi )**( 4 ) + ( -1 * ( S1 )**( 4 ) * ( 22 * ( S2 \
    )**( 2 ) + 5 * ( xi )**( 2 ) ) + 2 * ( S1 )**( 2 ) * ( 44 * ( S2 )**( \
    4 ) + ( ( S2 )**( 2 ) * ( xi )**( 2 ) + -2 * ( xi )**( 4 ) ) ) ) ) ) \
    ) ) + ( ( q )**( 8 ) * ( 2 * ( S1 )**( 6 ) + ( -3 * ( S2 )**( 6 ) + ( \
    104 * ( S2 )**( 4 ) * ( xi )**( 2 ) + ( 32 * ( S2 )**( 2 ) * ( xi \
    )**( 4 ) + ( ( S1 )**( 4 ) * ( 169 * ( S2 )**( 2 ) + 56 * ( xi )**( 2 \
    ) ) + 8 * ( S1 )**( 2 ) * ( 28 * ( S2 )**( 4 ) + ( 12 * ( S2 )**( 2 ) \
    * ( xi )**( 2 ) + -1 * ( xi )**( 4 ) ) ) ) ) ) ) ) + ( ( q )**( 4 ) * \
    ( -3 * ( S1 )**( 6 ) + ( 8 * ( S1 )**( 4 ) * ( 28 * ( S2 )**( 2 ) + \
    13 * ( xi )**( 2 ) ) + ( 2 * ( S2 )**( 2 ) * ( ( S2 )**( 4 ) + ( 28 * \
    ( S2 )**( 2 ) * ( xi )**( 2 ) + -4 * ( xi )**( 4 ) ) ) + ( S1 )**( 2 \
    ) * ( 169 * ( S2 )**( 4 ) + ( 96 * ( S2 )**( 2 ) * ( xi )**( 2 ) + 32 \
    * ( xi )**( 4 ) ) ) ) ) ) + 2 * ( q )**( 6 ) * ( ( S1 )**( 6 ) + ( ( \
    S2 )**( 6 ) + ( -91 * ( S2 )**( 4 ) * ( xi )**( 2 ) + ( -44 * ( S2 \
    )**( 2 ) * ( xi )**( 4 ) + ( -8 * ( xi )**( 6 ) + ( -1 * ( S1 )**( 4 \
    ) * ( 153 * ( S2 )**( 2 ) + 91 * ( xi )**( 2 ) ) + -1 * ( S1 )**( 2 ) \
    * ( 153 * ( S2 )**( 4 ) + ( 74 * ( S2 )**( 2 ) * ( xi )**( 2 ) + 44 * \
    ( xi )**( 4 ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) + ( u )**( 4 \
    ) * ( -256 * ( ( 1 + q ) )**( 2 ) * ( ( -1 + ( q )**( 2 ) ) )**( 2 ) \
    * ( ( ( S1 )**( 2 ) + -1 * ( S2 )**( 2 ) ) )**( 2 ) * ( ( -1 * q * ( \
    S1 )**( 2 ) + ( S2 )**( 2 ) ) )**( 2 ) * ( u )**( 2 ) * ( ( q )**( 4 \
    ) * ( S1 )**( 2 ) + ( ( S2 )**( 2 ) + ( ( q )**( 3 ) * ( ( S1 )**( 2 \
    ) + -1 * ( S2 )**( 2 ) ) + ( q * ( -1 * ( S1 )**( 2 ) + ( S2 )**( 2 ) \
    ) + -1 * ( q )**( 2 ) * ( ( S1 )**( 2 ) + ( ( S2 )**( 2 ) + ( xi )**( \
    2 ) ) ) ) ) ) ) + ( -128 * ( -1 + q ) * q * ( ( 1 + q ) )**( 3 ) * ( \
    ( S1 )**( 2 ) + -1 * ( S2 )**( 2 ) ) * u * xi * ( -4 * ( S1 )**( 2 ) \
    * ( S2 )**( 4 ) + ( 8 * ( S2 )**( 6 ) + ( ( q )**( 6 ) * ( 8 * ( S1 \
    )**( 6 ) + -4 * ( S1 )**( 4 ) * ( S2 )**( 2 ) ) + ( -1 * q * ( S2 \
    )**( 2 ) * ( ( S1 )**( 4 ) + ( 10 * ( S1 )**( 2 ) * ( S2 )**( 2 ) + \
    -3 * ( S2 )**( 4 ) ) ) + ( ( q )**( 5 ) * ( 3 * ( S1 )**( 6 ) + ( -10 \
    * ( S1 )**( 4 ) * ( S2 )**( 2 ) + -1 * ( S1 )**( 2 ) * ( S2 )**( 4 ) \
    ) ) + ( ( q )**( 3 ) * ( -3 * ( S1 )**( 6 ) + ( 11 * ( S1 )**( 2 ) * \
    ( S2 )**( 4 ) + ( -3 * ( S2 )**( 6 ) + ( 4 * ( S2 )**( 4 ) * ( xi \
    )**( 2 ) + ( S1 )**( 4 ) * ( 11 * ( S2 )**( 2 ) + 4 * ( xi )**( 2 ) ) \
    ) ) ) ) + ( ( q )**( 2 ) * ( 5 * ( S1 )**( 6 ) + ( 5 * ( S1 )**( 4 ) \
    * ( S2 )**( 2 ) + ( -13 * ( S2 )**( 6 ) + ( -8 * ( S2 )**( 4 ) * ( xi \
    )**( 2 ) + -1 * ( S1 )**( 2 ) * ( ( S2 )**( 4 ) + -4 * ( S2 )**( 2 ) \
    * ( xi )**( 2 ) ) ) ) ) ) + ( q )**( 4 ) * ( -13 * ( S1 )**( 6 ) + ( \
    5 * ( S2 )**( 6 ) + ( -1 * ( S1 )**( 4 ) * ( ( S2 )**( 2 ) + 8 * ( xi \
    )**( 2 ) ) + ( S1 )**( 2 ) * ( 5 * ( S2 )**( 4 ) + 4 * ( S2 )**( 2 ) \
    * ( xi )**( 2 ) ) ) ) ) ) ) ) ) ) ) ) + -16 * ( ( 1 + q ) )**( 2 ) * \
    ( 8 * ( q )**( 10 ) * ( S1 )**( 4 ) * ( ( S1 )**( 4 ) + ( -4 * ( S1 \
    )**( 2 ) * ( S2 )**( 2 ) + ( S2 )**( 4 ) ) ) + ( 8 * ( S2 )**( 4 ) * \
    ( ( S1 )**( 4 ) + ( -4 * ( S1 )**( 2 ) * ( S2 )**( 2 ) + ( S2 )**( 4 \
    ) ) ) + ( 4 * ( q )**( 9 ) * ( 9 * ( S1 )**( 8 ) + ( -13 * ( S1 )**( \
    6 ) * ( S2 )**( 2 ) + ( 7 * ( S1 )**( 4 ) * ( S2 )**( 4 ) + 5 * ( S1 \
    )**( 2 ) * ( S2 )**( 6 ) ) ) ) + ( 4 * q * ( 5 * ( S1 )**( 6 ) * ( S2 \
    )**( 2 ) + ( 7 * ( S1 )**( 4 ) * ( S2 )**( 4 ) + ( -13 * ( S1 )**( 2 \
    ) * ( S2 )**( 6 ) + 9 * ( S2 )**( 8 ) ) ) ) + ( 2 * ( q )**( 3 ) * ( \
    9 * ( S1 )**( 8 ) + ( -27 * ( S2 )**( 8 ) + ( -28 * ( S2 )**( 6 ) * ( \
    xi )**( 2 ) + ( -16 * ( S1 )**( 6 ) * ( 7 * ( S2 )**( 2 ) + ( xi )**( \
    2 ) ) + ( 2 * ( S1 )**( 4 ) * ( 53 * ( S2 )**( 4 ) + -6 * ( S2 )**( 2 \
    ) * ( xi )**( 2 ) ) + -8 * ( S1 )**( 2 ) * ( 5 * ( S2 )**( 6 ) + -3 * \
    ( S2 )**( 4 ) * ( xi )**( 2 ) ) ) ) ) ) ) + ( -2 * ( q )**( 7 ) * ( \
    27 * ( S1 )**( 8 ) + ( -9 * ( S2 )**( 8 ) + ( 16 * ( S2 )**( 6 ) * ( \
    xi )**( 2 ) + ( 4 * ( S1 )**( 6 ) * ( 10 * ( S2 )**( 2 ) + 7 * ( xi \
    )**( 2 ) ) + ( -2 * ( S1 )**( 4 ) * ( 53 * ( S2 )**( 4 ) + 12 * ( S2 \
    )**( 2 ) * ( xi )**( 2 ) ) + 4 * ( S1 )**( 2 ) * ( 28 * ( S2 )**( 6 ) \
    + 3 * ( S2 )**( 4 ) * ( xi )**( 2 ) ) ) ) ) ) ) + ( ( q )**( 8 ) * ( \
    31 * ( S1 )**( 8 ) + ( -1 * ( S2 )**( 8 ) + ( ( S1 )**( 6 ) * ( -52 * \
    ( S2 )**( 2 ) + 88 * ( xi )**( 2 ) ) + ( 2 * ( S1 )**( 4 ) * ( 69 * ( \
    S2 )**( 4 ) + -32 * ( S2 )**( 2 ) * ( xi )**( 2 ) ) + ( S1 )**( 2 ) * \
    ( -68 * ( S2 )**( 6 ) + 8 * ( S2 )**( 4 ) * ( xi )**( 2 ) ) ) ) ) ) + \
    ( -1 * ( q )**( 2 ) * ( ( S1 )**( 8 ) + ( 68 * ( S1 )**( 6 ) * ( S2 \
    )**( 2 ) + ( -31 * ( S2 )**( 8 ) + ( -88 * ( S2 )**( 6 ) * ( xi )**( \
    2 ) + ( -2 * ( S1 )**( 4 ) * ( 69 * ( S2 )**( 4 ) + 4 * ( S2 )**( 2 ) \
    * ( xi )**( 2 ) ) + ( S1 )**( 2 ) * ( 52 * ( S2 )**( 6 ) + 64 * ( S2 \
    )**( 4 ) * ( xi )**( 2 ) ) ) ) ) ) ) + ( 8 * ( q )**( 5 ) * ( 11 * ( \
    S2 )**( 6 ) * ( xi )**( 2 ) + ( 12 * ( S2 )**( 4 ) * ( xi )**( 4 ) + \
    ( ( S1 )**( 6 ) * ( 42 * ( S2 )**( 2 ) + 11 * ( xi )**( 2 ) ) + ( -3 \
    * ( S1 )**( 4 ) * ( 20 * ( S2 )**( 4 ) + ( ( S2 )**( 2 ) * ( xi )**( \
    2 ) + -4 * ( xi )**( 4 ) ) ) + ( S1 )**( 2 ) * ( 42 * ( S2 )**( 6 ) + \
    ( -3 * ( S2 )**( 4 ) * ( xi )**( 2 ) + -20 * ( S2 )**( 2 ) * ( xi \
    )**( 4 ) ) ) ) ) ) ) + ( ( q )**( 6 ) * ( -87 * ( S1 )**( 8 ) + ( 49 \
    * ( S2 )**( 8 ) + ( 112 * ( S2 )**( 6 ) * ( xi )**( 2 ) + ( -16 * ( \
    S2 )**( 4 ) * ( xi )**( 4 ) + ( 4 * ( S1 )**( 6 ) * ( 33 * ( S2 )**( \
    2 ) + -50 * ( xi )**( 2 ) ) + ( -2 * ( S1 )**( 4 ) * ( 73 * ( S2 )**( \
    4 ) + ( -104 * ( S2 )**( 2 ) * ( xi )**( 2 ) + 48 * ( xi )**( 4 ) ) ) \
    + 4 * ( S1 )**( 2 ) * ( 5 * ( S2 )**( 6 ) + ( -38 * ( S2 )**( 4 ) * ( \
    xi )**( 2 ) + 24 * ( S2 )**( 2 ) * ( xi )**( 4 ) ) ) ) ) ) ) ) ) + ( \
    q )**( 4 ) * ( 49 * ( S1 )**( 8 ) + ( 4 * ( S1 )**( 6 ) * ( 5 * ( S2 \
    )**( 2 ) + 28 * ( xi )**( 2 ) ) + ( -2 * ( S1 )**( 4 ) * ( 73 * ( S2 \
    )**( 4 ) + ( 76 * ( S2 )**( 2 ) * ( xi )**( 2 ) + 8 * ( xi )**( 4 ) ) \
    ) + ( -1 * ( S2 )**( 4 ) * ( 87 * ( S2 )**( 4 ) + ( 200 * ( S2 )**( 2 \
    ) * ( xi )**( 2 ) + 96 * ( xi )**( 4 ) ) ) + 4 * ( S1 )**( 2 ) * ( 33 \
    * ( S2 )**( 6 ) + ( 52 * ( S2 )**( 4 ) * ( xi )**( 2 ) + 24 * ( S2 \
    )**( 2 ) * ( xi )**( 4 ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) )

    coeff1 = \
    ( 32 * ( ( -1 + q ) )**( 2 ) * q * ( ( 1 + q ) )**( 4 ) * xi * ( ( q \
    )**( 4 ) * ( S1 )**( 2 ) + ( ( S2 )**( 2 ) + ( q * ( ( S1 )**( 2 ) + \
    -1 * ( S2 )**( 2 ) ) + ( ( q )**( 3 ) * ( -1 * ( S1 )**( 2 ) + ( S2 \
    )**( 2 ) ) + -1 * ( q )**( 2 ) * ( ( S1 )**( 2 ) + ( ( S2 )**( 2 ) + \
    ( xi )**( 2 ) ) ) ) ) ) ) + ( 32 * ( ( 1 + q ) )**( 2 ) * u * ( -12 * \
    q * ( S1 )**( 2 ) * ( S2 )**( 2 ) + ( -12 * ( q )**( 9 ) * ( S1 )**( \
    2 ) * ( S2 )**( 2 ) + ( ( q )**( 10 ) * ( S1 )**( 2 ) * ( ( S1 )**( 2 \
    ) + ( S2 )**( 2 ) ) + ( ( S2 )**( 2 ) * ( ( S1 )**( 2 ) + ( S2 )**( 2 \
    ) ) + ( ( q )**( 6 ) * ( 6 * ( S1 )**( 4 ) + ( -4 * ( S2 )**( 4 ) + ( \
    9 * ( S2 )**( 2 ) * ( xi )**( 2 ) + ( -8 * ( xi )**( 4 ) + ( S1 )**( \
    2 ) * ( 2 * ( S2 )**( 2 ) + -15 * ( xi )**( 2 ) ) ) ) ) ) + ( -12 * ( \
    q )**( 5 ) * ( 3 * ( S2 )**( 2 ) * ( xi )**( 2 ) + ( 2 * ( xi )**( 4 \
    ) + 3 * ( S1 )**( 2 ) * ( 2 * ( S2 )**( 2 ) + ( xi )**( 2 ) ) ) ) + ( \
    ( q )**( 2 ) * ( ( S1 )**( 4 ) + ( -4 * ( S2 )**( 4 ) + ( 7 * ( S2 \
    )**( 2 ) * ( xi )**( 2 ) + -1 * ( S1 )**( 2 ) * ( 3 * ( S2 )**( 2 ) + \
    ( xi )**( 2 ) ) ) ) ) + ( 6 * ( q )**( 3 ) * ( 3 * ( S2 )**( 2 ) * ( \
    xi )**( 2 ) + ( S1 )**( 2 ) * ( 8 * ( S2 )**( 2 ) + 3 * ( xi )**( 2 ) \
    ) ) + ( 6 * ( q )**( 7 ) * ( 3 * ( S2 )**( 2 ) * ( xi )**( 2 ) + ( S1 \
    )**( 2 ) * ( 8 * ( S2 )**( 2 ) + 3 * ( xi )**( 2 ) ) ) + ( ( q )**( 8 \
    ) * ( -4 * ( S1 )**( 4 ) + ( ( S2 )**( 4 ) + ( -1 * ( S2 )**( 2 ) * ( \
    xi )**( 2 ) + ( S1 )**( 2 ) * ( -3 * ( S2 )**( 2 ) + 7 * ( xi )**( 2 \
    ) ) ) ) ) + ( q )**( 4 ) * ( -4 * ( S1 )**( 4 ) + ( 6 * ( S2 )**( 4 ) \
    + ( -15 * ( S2 )**( 2 ) * ( xi )**( 2 ) + ( -8 * ( xi )**( 4 ) + ( S1 \
    )**( 2 ) * ( 2 * ( S2 )**( 2 ) + 9 * ( xi )**( 2 ) ) ) ) ) ) ) ) ) ) \
    ) ) ) ) ) ) + ( ( u )**( 4 ) * ( 256 * ( -1 + q ) * ( ( 1 + q ) )**( \
    4 ) * ( q * ( S1 )**( 2 ) + -1 * ( S2 )**( 2 ) ) * u * ( 2 * ( q )**( \
    6 ) * ( S1 )**( 4 ) * ( ( S1 )**( 2 ) + ( S2 )**( 2 ) ) + ( 2 * ( S2 \
    )**( 4 ) * ( ( S1 )**( 2 ) + ( S2 )**( 2 ) ) + ( ( q )**( 5 ) * ( -3 \
    * ( S1 )**( 6 ) + ( 2 * ( S1 )**( 4 ) * ( S2 )**( 2 ) + -7 * ( S1 \
    )**( 2 ) * ( S2 )**( 4 ) ) ) + ( q * ( -7 * ( S1 )**( 4 ) * ( S2 )**( \
    2 ) + ( 2 * ( S1 )**( 2 ) * ( S2 )**( 4 ) + -3 * ( S2 )**( 6 ) ) ) + \
    ( ( q )**( 3 ) * ( 3 * ( S1 )**( 6 ) + ( 5 * ( S1 )**( 2 ) * ( S2 \
    )**( 4 ) + ( 3 * ( S2 )**( 6 ) + ( 4 * ( S2 )**( 4 ) * ( xi )**( 2 ) \
    + ( S1 )**( 4 ) * ( 5 * ( S2 )**( 2 ) + 4 * ( xi )**( 2 ) ) ) ) ) ) + \
    ( ( q )**( 2 ) * ( 5 * ( S1 )**( 6 ) + ( -7 * ( S1 )**( 4 ) * ( S2 \
    )**( 2 ) + ( -7 * ( S2 )**( 6 ) + ( -2 * ( S2 )**( 4 ) * ( xi )**( 2 \
    ) + ( S1 )**( 2 ) * ( 5 * ( S2 )**( 4 ) + -2 * ( S2 )**( 2 ) * ( xi \
    )**( 2 ) ) ) ) ) ) + -1 * ( q )**( 4 ) * ( 7 * ( S1 )**( 6 ) + ( -5 * \
    ( S2 )**( 6 ) + ( ( S1 )**( 4 ) * ( -5 * ( S2 )**( 2 ) + 2 * ( xi \
    )**( 2 ) ) + ( S1 )**( 2 ) * ( 7 * ( S2 )**( 4 ) + 2 * ( S2 )**( 2 ) \
    * ( xi )**( 2 ) ) ) ) ) ) ) ) ) ) ) + 128 * q * ( ( 1 + q ) )**( 3 ) \
    * xi * ( 8 * ( S1 )**( 2 ) * ( S2 )**( 4 ) + ( 12 * ( S2 )**( 6 ) + ( \
    4 * ( q )**( 7 ) * ( 3 * ( S1 )**( 6 ) + 2 * ( S1 )**( 4 ) * ( S2 \
    )**( 2 ) ) + ( ( q )**( 6 ) * ( -17 * ( S1 )**( 6 ) + ( -6 * ( S1 \
    )**( 4 ) * ( S2 )**( 2 ) + 3 * ( S1 )**( 2 ) * ( S2 )**( 4 ) ) ) + ( \
    q * ( 3 * ( S1 )**( 4 ) * ( S2 )**( 2 ) + ( -6 * ( S1 )**( 2 ) * ( S2 \
    )**( 4 ) + -17 * ( S2 )**( 6 ) ) ) + ( ( q )**( 3 ) * ( 9 * ( S1 )**( \
    6 ) + ( 37 * ( S2 )**( 6 ) + ( 20 * ( S2 )**( 4 ) * ( xi )**( 2 ) + ( \
    ( S1 )**( 4 ) * ( 11 * ( S2 )**( 2 ) + -12 * ( xi )**( 2 ) ) + 3 * ( \
    S1 )**( 2 ) * ( ( S2 )**( 4 ) + 4 * ( S2 )**( 2 ) * ( xi )**( 2 ) ) ) \
    ) ) ) + ( -1 * ( q )**( 5 ) * ( 21 * ( S1 )**( 6 ) + ( 20 * ( S2 )**( \
    6 ) + ( 2 * ( S1 )**( 4 ) * ( 11 * ( S2 )**( 2 ) + 6 * ( xi )**( 2 ) \
    ) + ( S1 )**( 2 ) * ( -3 * ( S2 )**( 4 ) + 8 * ( S2 )**( 2 ) * ( xi \
    )**( 2 ) ) ) ) ) + ( -1 * ( q )**( 2 ) * ( 20 * ( S1 )**( 6 ) + ( -3 \
    * ( S1 )**( 4 ) * ( S2 )**( 2 ) + ( 3 * ( S2 )**( 4 ) * ( 7 * ( S2 \
    )**( 2 ) + 4 * ( xi )**( 2 ) ) + ( S1 )**( 2 ) * ( 22 * ( S2 )**( 4 ) \
    + 8 * ( S2 )**( 2 ) * ( xi )**( 2 ) ) ) ) ) + ( q )**( 4 ) * ( 37 * ( \
    S1 )**( 6 ) + ( 9 * ( S2 )**( 6 ) + ( -12 * ( S2 )**( 4 ) * ( xi )**( \
    2 ) + ( ( S1 )**( 4 ) * ( 3 * ( S2 )**( 2 ) + 20 * ( xi )**( 2 ) ) + \
    ( S1 )**( 2 ) * ( 11 * ( S2 )**( 4 ) + 12 * ( S2 )**( 2 ) * ( xi )**( \
    2 ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) + ( u )**( 2 ) * ( 32 * q * ( ( 1 + q \
    ) )**( 2 ) * xi * ( 8 * ( q )**( 8 ) * ( S1 )**( 2 ) * ( 2 * ( S1 \
    )**( 2 ) + ( S2 )**( 2 ) ) + ( 8 * ( S2 )**( 2 ) * ( ( S1 )**( 2 ) + \
    2 * ( S2 )**( 2 ) ) + ( ( q )**( 7 ) * ( 65 * ( S1 )**( 4 ) + ( 2 * ( \
    S1 )**( 2 ) * ( S2 )**( 2 ) + -3 * ( S2 )**( 4 ) ) ) + ( q * ( -3 * ( \
    S1 )**( 4 ) + ( 2 * ( S1 )**( 2 ) * ( S2 )**( 2 ) + 65 * ( S2 )**( 4 \
    ) ) ) + ( 2 * ( q )**( 6 ) * ( 7 * ( S1 )**( 4 ) + ( -14 * ( S1 )**( \
    2 ) * ( S2 )**( 2 ) + ( 23 * ( S2 )**( 4 ) + -4 * ( S2 )**( 2 ) * ( \
    xi )**( 2 ) ) ) ) + ( -4 * ( q )**( 4 ) * ( 19 * ( S1 )**( 4 ) + ( 19 \
    * ( S2 )**( 4 ) + ( 14 * ( S2 )**( 2 ) * ( xi )**( 2 ) + ( 4 * ( xi \
    )**( 4 ) + -2 * ( S1 )**( 2 ) * ( 5 * ( S2 )**( 2 ) + -7 * ( xi )**( \
    2 ) ) ) ) ) ) + ( 2 * ( q )**( 2 ) * ( 23 * ( S1 )**( 4 ) + ( 7 * ( \
    S2 )**( 4 ) + -2 * ( S1 )**( 2 ) * ( 7 * ( S2 )**( 2 ) + 2 * ( xi \
    )**( 2 ) ) ) ) + ( ( q )**( 5 ) * ( -133 * ( S1 )**( 4 ) + ( 71 * ( \
    S2 )**( 4 ) + ( 12 * ( S2 )**( 2 ) * ( xi )**( 2 ) + -2 * ( S1 )**( 2 \
    ) * ( ( S2 )**( 2 ) + 38 * ( xi )**( 2 ) ) ) ) ) + ( q )**( 3 ) * ( \
    71 * ( S1 )**( 4 ) + ( -2 * ( S1 )**( 2 ) * ( ( S2 )**( 2 ) + -6 * ( \
    xi )**( 2 ) ) + -19 * ( 7 * ( S2 )**( 4 ) + 4 * ( S2 )**( 2 ) * ( xi \
    )**( 2 ) ) ) ) ) ) ) ) ) ) ) ) + 64 * ( ( 1 + q ) )**( 2 ) * u * ( 4 \
    * ( q )**( 10 ) * ( S1 )**( 4 ) * ( ( S1 )**( 2 ) + ( S2 )**( 2 ) ) + \
    ( 4 * ( S2 )**( 4 ) * ( ( S1 )**( 2 ) + ( S2 )**( 2 ) ) + ( ( q )**( \
    9 ) * ( 23 * ( S1 )**( 6 ) + ( 26 * ( S1 )**( 4 ) * ( S2 )**( 2 ) + \
    15 * ( S1 )**( 2 ) * ( S2 )**( 4 ) ) ) + ( q * ( 15 * ( S1 )**( 4 ) * \
    ( S2 )**( 2 ) + ( 26 * ( S1 )**( 2 ) * ( S2 )**( 4 ) + 23 * ( S2 )**( \
    6 ) ) ) + ( ( q )**( 8 ) * ( 25 * ( S1 )**( 6 ) + ( -1 * ( S2 )**( 6 \
    ) + ( ( S1 )**( 4 ) * ( -23 * ( S2 )**( 2 ) + 20 * ( xi )**( 2 ) ) + \
    ( S1 )**( 2 ) * ( -25 * ( S2 )**( 4 ) + 4 * ( S2 )**( 2 ) * ( xi )**( \
    2 ) ) ) ) ) + ( ( q )**( 3 ) * ( 13 * ( S1 )**( 6 ) + ( -33 * ( S2 \
    )**( 6 ) + ( -32 * ( S2 )**( 4 ) * ( xi )**( 2 ) + ( -1 * ( S1 )**( 4 \
    ) * ( 107 * ( S2 )**( 2 ) + 24 * ( xi )**( 2 ) ) + -3 * ( S1 )**( 2 ) \
    * ( 43 * ( S2 )**( 4 ) + 8 * ( S2 )**( 2 ) * ( xi )**( 2 ) ) ) ) ) ) \
    + ( -1 * ( q )**( 7 ) * ( 33 * ( S1 )**( 6 ) + ( -13 * ( S2 )**( 6 ) \
    + ( 24 * ( S2 )**( 4 ) * ( xi )**( 2 ) + ( ( S1 )**( 4 ) * ( 129 * ( \
    S2 )**( 2 ) + 32 * ( xi )**( 2 ) ) + ( S1 )**( 2 ) * ( 107 * ( S2 \
    )**( 4 ) + 24 * ( S2 )**( 2 ) * ( xi )**( 2 ) ) ) ) ) ) + ( -1 * ( q \
    )**( 2 ) * ( ( S1 )**( 6 ) + ( 25 * ( S1 )**( 4 ) * ( S2 )**( 2 ) + ( \
    ( S1 )**( 2 ) * ( 23 * ( S2 )**( 4 ) + -4 * ( S2 )**( 2 ) * ( xi )**( \
    2 ) ) + -5 * ( 5 * ( S2 )**( 6 ) + 4 * ( S2 )**( 4 ) * ( xi )**( 2 ) \
    ) ) ) ) + ( ( q )**( 6 ) * ( -63 * ( S1 )**( 6 ) + ( 35 * ( S2 )**( 6 \
    ) + ( 16 * ( S2 )**( 4 ) * ( xi )**( 2 ) + ( -8 * ( S2 )**( 2 ) * ( \
    xi )**( 4 ) + ( ( S1 )**( 4 ) * ( 9 * ( S2 )**( 2 ) + -60 * ( xi )**( \
    2 ) ) + ( S1 )**( 2 ) * ( 35 * ( S2 )**( 4 ) + ( 20 * ( S2 )**( 2 ) * \
    ( xi )**( 2 ) + -24 * ( xi )**( 4 ) ) ) ) ) ) ) ) + ( ( q )**( 5 ) * \
    ( -3 * ( S1 )**( 6 ) + ( -3 * ( S2 )**( 6 ) + ( 32 * ( S2 )**( 4 ) * \
    ( xi )**( 2 ) + ( 8 * ( S2 )**( 2 ) * ( xi )**( 4 ) + ( ( S1 )**( 4 ) \
    * ( 195 * ( S2 )**( 2 ) + 32 * ( xi )**( 2 ) ) + ( S1 )**( 2 ) * ( \
    195 * ( S2 )**( 4 ) + ( 96 * ( S2 )**( 2 ) * ( xi )**( 2 ) + 8 * ( xi \
    )**( 4 ) ) ) ) ) ) ) ) + ( q )**( 4 ) * ( 35 * ( S1 )**( 6 ) + ( ( S1 \
    )**( 4 ) * ( 35 * ( S2 )**( 2 ) + 16 * ( xi )**( 2 ) ) + ( ( S1 )**( \
    2 ) * ( 9 * ( S2 )**( 4 ) + ( 20 * ( S2 )**( 2 ) * ( xi )**( 2 ) + -8 \
    * ( xi )**( 4 ) ) ) + -3 * ( 21 * ( S2 )**( 6 ) + ( 20 * ( S2 )**( 4 \
    ) * ( xi )**( 2 ) + 8 * ( S2 )**( 2 ) * ( xi )**( 4 ) ) ) ) ) ) ) ) ) \
    ) ) ) ) ) ) ) ) ) ) )

    coeff2 = \
    ( -16 * ( ( -1 + q ) )**( 2 ) * ( ( 1 + q ) )**( 4 ) * ( ( q )**( 6 \
    ) * ( S1 )**( 2 ) + ( ( S2 )**( 2 ) + ( -4 * ( q )**( 3 ) * ( xi )**( \
    2 ) + ( ( q )**( 2 ) * ( ( S1 )**( 2 ) + ( -2 * ( S2 )**( 2 ) + -1 * \
    ( xi )**( 2 ) ) ) + ( q )**( 4 ) * ( -2 * ( S1 )**( 2 ) + ( ( S2 )**( \
    2 ) + -1 * ( xi )**( 2 ) ) ) ) ) ) ) + ( -32 * q * ( ( 1 + q ) )**( 4 \
    ) * u * xi * ( 4 * ( q )**( 6 ) * ( S1 )**( 2 ) + ( 4 * ( S2 )**( 2 ) \
    + ( ( q )**( 5 ) * ( 19 * ( S1 )**( 2 ) + -3 * ( S2 )**( 2 ) ) + ( q \
    * ( -3 * ( S1 )**( 2 ) + 19 * ( S2 )**( 2 ) ) + ( ( q )**( 2 ) * ( 26 \
    * ( S1 )**( 2 ) + ( -30 * ( S2 )**( 2 ) + -4 * ( xi )**( 2 ) ) ) + ( \
    ( q )**( 4 ) * ( -30 * ( S1 )**( 2 ) + ( 26 * ( S2 )**( 2 ) + -4 * ( \
    xi )**( 2 ) ) ) + -16 * ( q )**( 3 ) * ( ( S1 )**( 2 ) + ( ( S2 )**( \
    2 ) + 2 * ( xi )**( 2 ) ) ) ) ) ) ) ) ) + ( -256 * ( ( 1 + q ) )**( 4 \
    ) * ( u )**( 4 ) * ( ( q )**( 8 ) * ( S1 )**( 6 ) + ( ( S2 )**( 6 ) + \
    ( -1 * ( q )**( 7 ) * ( 7 * ( S1 )**( 6 ) + 9 * ( S1 )**( 4 ) * ( S2 \
    )**( 2 ) ) + ( -1 * q * ( 9 * ( S1 )**( 2 ) * ( S2 )**( 4 ) + 7 * ( \
    S2 )**( 6 ) ) + ( ( q )**( 2 ) * ( 18 * ( S1 )**( 4 ) * ( S2 )**( 2 ) \
    + ( 9 * ( S1 )**( 2 ) * ( S2 )**( 4 ) + ( ( S2 )**( 6 ) + -1 * ( S2 \
    )**( 4 ) * ( xi )**( 2 ) ) ) ) + ( ( q )**( 6 ) * ( ( S1 )**( 6 ) + ( \
    18 * ( S1 )**( 2 ) * ( S2 )**( 4 ) + ( S1 )**( 4 ) * ( 9 * ( S2 )**( \
    2 ) + -1 * ( xi )**( 2 ) ) ) ) + ( ( q )**( 5 ) * ( 17 * ( S1 )**( 6 \
    ) + ( -10 * ( S2 )**( 6 ) + ( 6 * ( S1 )**( 2 ) * ( S2 )**( 2 ) * ( \
    xi )**( 2 ) + ( S1 )**( 4 ) * ( 9 * ( S2 )**( 2 ) + 6 * ( xi )**( 2 ) \
    ) ) ) ) + ( ( q )**( 3 ) * ( -10 * ( S1 )**( 6 ) + ( 17 * ( S2 )**( 6 \
    ) + ( 6 * ( S2 )**( 4 ) * ( xi )**( 2 ) + ( S1 )**( 2 ) * ( 9 * ( S2 \
    )**( 4 ) + 6 * ( S2 )**( 2 ) * ( xi )**( 2 ) ) ) ) ) + -1 * ( q )**( \
    4 ) * ( 2 * ( S1 )**( 6 ) + ( 3 * ( S1 )**( 4 ) * ( 9 * ( S2 )**( 2 ) \
    + 2 * ( xi )**( 2 ) ) + ( 2 * ( S2 )**( 4 ) * ( ( S2 )**( 2 ) + 3 * ( \
    xi )**( 2 ) ) + ( S1 )**( 2 ) * ( 27 * ( S2 )**( 4 ) + 10 * ( S2 )**( \
    2 ) * ( xi )**( 2 ) ) ) ) ) ) ) ) ) ) ) ) ) + ( u )**( 2 ) * ( -32 * \
    ( ( 1 + q ) )**( 2 ) * ( 4 * ( q )**( 10 ) * ( S1 )**( 4 ) + ( 4 * ( \
    S2 )**( 4 ) + ( ( q )**( 9 ) * ( 38 * ( S1 )**( 4 ) + 30 * ( S1 )**( \
    2 ) * ( S2 )**( 2 ) ) + ( q * ( 30 * ( S1 )**( 2 ) * ( S2 )**( 2 ) + \
    38 * ( S2 )**( 4 ) ) + ( ( q )**( 2 ) * ( -3 * ( S1 )**( 4 ) + ( 2 * \
    ( S1 )**( 2 ) * ( S2 )**( 2 ) + ( 53 * ( S2 )**( 4 ) + 4 * ( S2 )**( \
    2 ) * ( xi )**( 2 ) ) ) ) + ( ( q )**( 8 ) * ( 53 * ( S1 )**( 4 ) + ( \
    -3 * ( S2 )**( 4 ) + 2 * ( S1 )**( 2 ) * ( ( S2 )**( 2 ) + 2 * ( xi \
    )**( 2 ) ) ) ) + ( -4 * ( q )**( 7 ) * ( 13 * ( S1 )**( 4 ) + ( -6 * \
    ( S2 )**( 2 ) * ( ( S2 )**( 2 ) + -2 * ( xi )**( 2 ) ) + ( S1 )**( 2 \
    ) * ( 29 * ( S2 )**( 2 ) + 9 * ( xi )**( 2 ) ) ) ) + ( 4 * ( q )**( 3 \
    ) * ( 6 * ( S1 )**( 4 ) + ( -13 * ( S2 )**( 4 ) + ( -9 * ( S2 )**( 2 \
    ) * ( xi )**( 2 ) + -1 * ( S1 )**( 2 ) * ( 29 * ( S2 )**( 2 ) + 12 * \
    ( xi )**( 2 ) ) ) ) ) + ( -1 * ( q )**( 6 ) * ( 121 * ( S1 )**( 4 ) + \
    ( -67 * ( S2 )**( 4 ) + ( 104 * ( S2 )**( 2 ) * ( xi )**( 2 ) + ( 8 * \
    ( xi )**( 4 ) + 2 * ( S1 )**( 2 ) * ( ( S2 )**( 2 ) + 46 * ( xi )**( \
    2 ) ) ) ) ) ) + ( ( q )**( 4 ) * ( 67 * ( S1 )**( 4 ) + ( -121 * ( S2 \
    )**( 4 ) + ( -92 * ( S2 )**( 2 ) * ( xi )**( 2 ) + ( -8 * ( xi )**( 4 \
    ) + -2 * ( S1 )**( 2 ) * ( ( S2 )**( 2 ) + 52 * ( xi )**( 2 ) ) ) ) ) \
    ) + -2 * ( q )**( 5 ) * ( 5 * ( S1 )**( 4 ) + ( 5 * ( S2 )**( 4 ) + ( \
    54 * ( S2 )**( 2 ) * ( xi )**( 2 ) + ( 16 * ( xi )**( 4 ) + ( S1 )**( \
    2 ) * ( -86 * ( S2 )**( 2 ) + 54 * ( xi )**( 2 ) ) ) ) ) ) ) ) ) ) ) \
    ) ) ) ) ) + -128 * q * ( ( 1 + q ) )**( 3 ) * u * xi * ( 4 * ( q )**( \
    7 ) * ( S1 )**( 4 ) + ( 4 * ( S2 )**( 4 ) + ( ( q )**( 6 ) * ( -11 * \
    ( S1 )**( 4 ) + 3 * ( S1 )**( 2 ) * ( S2 )**( 2 ) ) + ( q * ( 3 * ( \
    S1 )**( 2 ) * ( S2 )**( 2 ) + -11 * ( S2 )**( 4 ) ) + ( ( q )**( 2 ) \
    * ( -30 * ( S1 )**( 4 ) + ( 9 * ( S1 )**( 2 ) * ( S2 )**( 2 ) + ( 5 * \
    ( S2 )**( 4 ) + -4 * ( S2 )**( 2 ) * ( xi )**( 2 ) ) ) ) + ( ( q )**( \
    5 ) * ( 5 * ( S1 )**( 4 ) + ( -30 * ( S2 )**( 4 ) + ( S1 )**( 2 ) * ( \
    9 * ( S2 )**( 2 ) + -4 * ( xi )**( 2 ) ) ) ) + ( ( q )**( 3 ) * ( -21 \
    * ( S1 )**( 4 ) + ( 29 * ( S2 )**( 4 ) + ( 4 * ( S2 )**( 2 ) * ( xi \
    )**( 2 ) + 12 * ( S1 )**( 2 ) * ( ( S2 )**( 2 ) + -1 * ( xi )**( 2 ) \
    ) ) ) ) + ( q )**( 4 ) * ( 29 * ( S1 )**( 4 ) + ( 4 * ( S1 )**( 2 ) * \
    ( 3 * ( S2 )**( 2 ) + ( xi )**( 2 ) ) + -3 * ( 7 * ( S2 )**( 4 ) + 4 \
    * ( S2 )**( 2 ) * ( xi )**( 2 ) ) ) ) ) ) ) ) ) ) ) ) ) ) )

    coeff3 = \
    ( -32 * ( ( -1 + q ) )**( 2 ) * ( q )**( 2 ) * ( ( 1 + q ) )**( 6 ) * \
    xi + ( 64 * q * ( ( 1 + q ) )**( 4 ) * u * ( 5 * ( q )**( 6 ) * ( S1 \
    )**( 2 ) + ( 5 * ( S2 )**( 2 ) + ( -1 * q * ( ( S1 )**( 2 ) + ( S2 \
    )**( 2 ) ) + ( -1 * ( q )**( 5 ) * ( ( S1 )**( 2 ) + ( S2 )**( 2 ) ) \
    + ( 2 * ( q )**( 3 ) * ( ( S1 )**( 2 ) + ( ( S2 )**( 2 ) + -12 * ( xi \
    )**( 2 ) ) ) + ( ( q )**( 2 ) * ( 5 * ( S1 )**( 2 ) + ( -10 * ( S2 \
    )**( 2 ) + -8 * ( xi )**( 2 ) ) ) + ( q )**( 4 ) * ( -10 * ( S1 )**( \
    2 ) + ( 5 * ( S2 )**( 2 ) + -8 * ( xi )**( 2 ) ) ) ) ) ) ) ) ) + ( u \
    )**( 2 ) * ( 128 * ( q )**( 2 ) * ( ( 1 + q ) )**( 4 ) * xi * ( ( q \
    )**( 4 ) * ( S1 )**( 2 ) + ( ( S2 )**( 2 ) + ( 4 * ( q )**( 3 ) * ( ( \
    S1 )**( 2 ) + -5 * ( S2 )**( 2 ) ) + ( 4 * q * ( -5 * ( S1 )**( 2 ) + \
    ( S2 )**( 2 ) ) + -1 * ( q )**( 2 ) * ( 17 * ( S1 )**( 2 ) + ( 17 * ( \
    S2 )**( 2 ) + 4 * ( xi )**( 2 ) ) ) ) ) ) ) + -256 * q * ( ( 1 + q ) \
    )**( 4 ) * u * ( 3 * ( q )**( 6 ) * ( S1 )**( 4 ) + ( 3 * ( S2 )**( 4 \
    ) + ( -6 * ( q )**( 5 ) * ( ( S1 )**( 4 ) + 2 * ( S1 )**( 2 ) * ( S2 \
    )**( 2 ) ) + ( -6 * q * ( 2 * ( S1 )**( 2 ) * ( S2 )**( 2 ) + ( S2 \
    )**( 4 ) ) + ( ( q )**( 2 ) * ( 10 * ( S1 )**( 4 ) + ( -2 * ( S1 )**( \
    2 ) * ( S2 )**( 2 ) + ( -11 * ( S2 )**( 4 ) + -2 * ( S2 )**( 2 ) * ( \
    xi )**( 2 ) ) ) ) + ( -1 * ( q )**( 4 ) * ( 11 * ( S1 )**( 4 ) + ( \
    -10 * ( S2 )**( 4 ) + 2 * ( S1 )**( 2 ) * ( ( S2 )**( 2 ) + ( xi )**( \
    2 ) ) ) ) + 4 * ( q )**( 3 ) * ( 2 * ( S1 )**( 4 ) + ( ( S2 )**( 2 ) \
    * ( 2 * ( S2 )**( 2 ) + ( xi )**( 2 ) ) + ( S1 )**( 2 ) * ( 5 * ( S2 \
    )**( 2 ) + ( xi )**( 2 ) ) ) ) ) ) ) ) ) ) ) ) )

    coeff4 = \
    ( 16 * ( ( -1 + q ) )**( 2 ) * ( q )**( 2 ) * ( ( 1 + q ) )**( 6 ) + \
    ( 640 * ( q )**( 3 ) * ( ( 1 + q ) )**( 6 ) * u * xi + -256 * ( q \
    )**( 2 ) * ( ( 1 + q ) )**( 4 ) * ( u )**( 2 ) * ( 3 * ( q )**( 4 ) * \
    ( S1 )**( 2 ) + ( 3 * ( S2 )**( 2 ) + ( ( q )**( 3 ) * ( ( S1 )**( 2 \
    ) + -5 * ( S2 )**( 2 ) ) + ( q * ( -5 * ( S1 )**( 2 ) + ( S2 )**( 2 ) \
    ) + -1 * ( q )**( 2 ) * ( 7 * ( S1 )**( 2 ) + ( 7 * ( S2 )**( 2 ) + ( \
    xi )**( 2 ) ) ) ) ) ) ) ) )
    coeff5 = \
    -256 * ( q )**( 3 ) * ( ( 1 + q ) )**( 6 ) * u

    return toarray(coeff5, coeff4, coeff3, coeff2, coeff1, coeff0)


def Jresonances(r,xi,q,chi1,chi2):
    """
    Total angular momentum of the two spin-orbit resonances. The resonances minimizes and maximizes J for a given value of xi. The minimum corresponds to DeltaPhi=pi and the maximum corresponds to DeltaPhi=0.

    Call
    ----
    Jmin,Jmax = Jresonances(r,xi,q,chi1,chi2)

    Parameters
    ----------
    r: float
    	Binary separation.
    xi: float
    	Effective spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    Jmin: float
    	Minimum value of the total angular momentum J.
    Jmax: float
    	Maximum value of the total angular momentum J.
    """

    # There are in principle five solutions, but only two are physical.

    u = eval_u(r, q)

    kapparoots = wraproots(kappadiscriminant_coefficients,u,xi,q,chi1,chi2)
    kapparoots = kapparoots[np.isfinite(kapparoots)]

    def _compute(kapparoots,r,xi,q,chi1,chi2):
        with np.errstate(invalid='ignore'):
            Jroots = np.array([eval_J(kappa=x,r=r,q=q) for x in kapparoots])
            Sroots = np.array([Satresonance(x,r,xi,q,chi1,chi2) for x in Jroots])
            Smin,Smax = np.array([Slimits_LJS1S2(x,r,q,chi1,chi2) for x in Jroots]).T
            Jres = Jroots[np.logical_and(Sroots>Smin,Sroots<Smax)]

            return Jres

    if np.ndim(kapparoots)==1:
        Jmin,Jmax =_compute(kapparoots,r,xi,q,chi1,chi2)
    else:
        Jmin,Jmax =np.array(list(map(_compute, kapparoots,r,xi,q,chi1,chi2))).T

    return toarray(Jmin,Jmax)


def Jlimits(r=None,xi=None,q=None,chi1=None,chi2=None):
    """
    Limits on the magnitude of the total angular momentum. The contraints considered depend on the inputs provided.
    - If r, q, chi1, and chi2 are provided, enforce J=L+S1+S2.
    - If r, xi, q, chi1, and chi2 are provided, the limits are given by the two spin-orbit resonances.

    Call
    ----
    Jmin,Jmax = Jlimits(r = None,xi = None,q = None,chi1 = None,chi2 = None)

    Parameters
    ----------
    r: float, optional (default: None)
    	Binary separation.
    xi: float, optional (default: None)
    	Effective spin.
    q: float, optional (default: None)
    	Mass ratio: 0<=q<=1.
    chi1: float, optional (default: None)
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float, optional (default: None)
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    Jmin: float
    	Minimum value of the total angular momentum J.
    Jmax: float
    	Maximum value of the total angular momentum J.
    """

    if r is not None and xi is None and q is not None and chi1 is not None and chi2 is not None:
        Jmin,Jmax = Jlimits_LS1S2(r,q,chi1,chi2)

    elif r is not None and xi is not None and q is not None and chi1 is not None and chi2 is not None:
        #TODO: Assert that the xi values are compatible with q,chi1,chi2 (either explicitely or with a generic 'limits_check' function)
        Jmin,Jmax = Jresonances(r,xi,q,chi1,chi2)

    else:
        raise TypeError

    return toarray(Jmin,Jmax)


def xilimits_definition(q,chi1,chi2):
    """
    Limits on the effective spin based only on the definition xi = (1+q)S1.L + (1+1/q)S2.L.

    Call
    ----
    ximin,ximax = xilimits_definition(q,chi1,chi2)

    Parameters
    ----------
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    ximin: float
    	Minimum value of the effective spin xi.
    ximax: float
    	Maximum value of the effective spin xi.
    """

    q=toarray(q)
    S1,S2 = spinmags(q,chi1,chi2)
    xilim = (1+q)*S1 + (1+1/q)*S2

    return toarray(-xilim,xilim)


def xidiscriminant_coefficients(kappa,u,q,chi1,chi2):
    """
    Coefficients of the sixth-degree equation in xi that defines the spin-orbit resonances.

    Call
    ----
    coeff6,coeff5,coeff4,coeff3,coeff2,coeff1,coeff0 = xidiscriminant_coefficients(kappa,u,q,chi1,chi2)

    Parameters
    ----------
    kappa: float
    	Regularized angular momentum (J^2-L^2)/(2L).
    u: float
    	Compactified separation 1/(2L).
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    coeff6: float
    	Coefficient to the x^6 term in polynomial.
    coeff5: float
    	Coefficient to the x^5 term in polynomial.
    coeff4: float
    	Coefficient to the x^4 term in polynomial.
    coeff3: float
    	Coefficient to the x^3 term in polynomial.
    coeff2: float
    	Coefficient to the x^2 term in polynomial.
    coeff1: float
    	Coefficient to the x^1 term in polynomial.
    coeff0: float
    	Coefficient to the x^0 term in polynomial.
    """

    kappa,u,q=toarray(kappa,u,q)
    S1,S2= spinmags(q,chi1,chi2)


    coeff0 = \
    ( 16 * ( ( -1 + q ) )**( 2 ) * ( ( 1 + q ) )**( 6 ) * ( ( ( -1 + q ) \
    )**( 2 ) * ( S1 )**( 2 ) + -1 * ( kappa )**( 2 ) ) * ( ( ( -1 + q ) \
    )**( 2 ) * ( S2 )**( 2 ) + -1 * ( q )**( 2 ) * ( kappa )**( 2 ) ) + ( \
    32 * ( ( 1 + q ) )**( 6 ) * u * kappa * ( ( q )**( 6 ) * ( S1 )**( 2 \
    ) * ( ( S1 )**( 2 ) + ( S2 )**( 2 ) ) + ( ( S2 )**( 2 ) * ( ( S1 )**( \
    2 ) + ( S2 )**( 2 ) ) + ( -2 * q * ( S2 )**( 2 ) * ( 8 * ( S1 )**( 2 \
    ) + ( 2 * ( S2 )**( 2 ) + -5 * ( kappa )**( 2 ) ) ) + ( -2 * ( q )**( \
    5 ) * ( S1 )**( 2 ) * ( 2 * ( S1 )**( 2 ) + ( 8 * ( S2 )**( 2 ) + -5 \
    * ( kappa )**( 2 ) ) ) + ( -2 * ( q )**( 3 ) * ( 2 * ( S1 )**( 4 ) + \
    ( 2 * ( S2 )**( 4 ) + ( -7 * ( S2 )**( 2 ) * ( kappa )**( 2 ) + ( 4 * \
    ( kappa )**( 4 ) + ( S1 )**( 2 ) * ( 40 * ( S2 )**( 2 ) + -7 * ( \
    kappa )**( 2 ) ) ) ) ) ) + ( ( q )**( 4 ) * ( 6 * ( S1 )**( 4 ) + ( ( \
    S2 )**( 4 ) + ( -2 * ( S2 )**( 2 ) * ( kappa )**( 2 ) + 11 * ( S1 \
    )**( 2 ) * ( 5 * ( S2 )**( 2 ) + -2 * ( kappa )**( 2 ) ) ) ) ) + ( q \
    )**( 2 ) * ( ( S1 )**( 4 ) + ( 6 * ( S2 )**( 4 ) + ( -22 * ( S2 )**( \
    2 ) * ( kappa )**( 2 ) + ( S1 )**( 2 ) * ( 55 * ( S2 )**( 2 ) + -2 * \
    ( kappa )**( 2 ) ) ) ) ) ) ) ) ) ) ) + ( ( u )**( 4 ) * ( -256 * ( ( \
    -1 + q ) )**( 3 ) * ( ( 1 + q ) )**( 6 ) * ( ( ( S1 )**( 2 ) + -1 * ( \
    S2 )**( 2 ) ) )**( 2 ) * ( ( q * ( S1 )**( 2 ) + -1 * ( S2 )**( 2 ) ) \
    )**( 3 ) * ( u )**( 2 ) + ( 256 * ( ( -1 + q ) )**( 2 ) * ( ( 1 + q ) \
    )**( 6 ) * ( ( -1 * q * ( S1 )**( 2 ) + ( S2 )**( 2 ) ) )**( 2 ) * ( \
    2 * ( q )**( 2 ) * ( S1 )**( 2 ) * ( ( S1 )**( 2 ) + ( S2 )**( 2 ) ) \
    + ( 2 * ( S2 )**( 2 ) * ( ( S1 )**( 2 ) + ( S2 )**( 2 ) ) + q * ( -5 \
    * ( S1 )**( 4 ) + ( 2 * ( S1 )**( 2 ) * ( S2 )**( 2 ) + -5 * ( S2 \
    )**( 4 ) ) ) ) ) * u * kappa + -16 * ( -1 + q ) * ( ( 1 + q ) )**( 6 \
    ) * ( -8 * ( S2 )**( 4 ) * ( ( S1 )**( 4 ) + ( -4 * ( S1 )**( 2 ) * ( \
    S2 )**( 2 ) + ( ( S2 )**( 4 ) + 2 * ( S2 )**( 2 ) * ( kappa )**( 2 ) \
    ) ) ) + ( 8 * ( q )**( 5 ) * ( S1 )**( 4 ) * ( ( S1 )**( 4 ) + ( ( S2 \
    )**( 4 ) + ( S1 )**( 2 ) * ( -4 * ( S2 )**( 2 ) + 2 * ( kappa )**( 2 \
    ) ) ) ) + ( 4 * ( q )**( 4 ) * ( 3 * ( S1 )**( 8 ) + ( 5 * ( S1 )**( \
    2 ) * ( S2 )**( 6 ) + ( ( S1 )**( 6 ) * ( 11 * ( S2 )**( 2 ) + -32 * \
    ( kappa )**( 2 ) ) + ( S1 )**( 4 ) * ( ( S2 )**( 4 ) + -36 * ( S2 \
    )**( 2 ) * ( kappa )**( 2 ) ) ) ) ) + ( -4 * q * ( 5 * ( S1 )**( 6 ) \
    * ( S2 )**( 2 ) + ( ( S1 )**( 4 ) * ( S2 )**( 4 ) + ( 3 * ( S2 )**( 8 \
    ) + ( -32 * ( S2 )**( 6 ) * ( kappa )**( 2 ) + ( S1 )**( 2 ) * ( 11 * \
    ( S2 )**( 6 ) + -36 * ( S2 )**( 4 ) * ( kappa )**( 2 ) ) ) ) ) ) + ( \
    ( q )**( 2 ) * ( ( S1 )**( 8 ) + ( 128 * ( S1 )**( 6 ) * ( S2 )**( 2 \
    ) + ( 21 * ( S2 )**( 8 ) + ( -160 * ( S2 )**( 6 ) * ( kappa )**( 2 ) \
    + ( -2 * ( S1 )**( 4 ) * ( 55 * ( S2 )**( 4 ) + 144 * ( S2 )**( 2 ) * \
    ( kappa )**( 2 ) ) + 24 * ( S1 )**( 2 ) * ( 5 * ( S2 )**( 6 ) + -12 * \
    ( S2 )**( 4 ) * ( kappa )**( 2 ) ) ) ) ) ) ) + -1 * ( q )**( 3 ) * ( \
    21 * ( S1 )**( 8 ) + ( ( S2 )**( 8 ) + ( 40 * ( S1 )**( 6 ) * ( 3 * ( \
    S2 )**( 2 ) + -4 * ( kappa )**( 2 ) ) + ( -2 * ( S1 )**( 4 ) * ( 55 * \
    ( S2 )**( 4 ) + 144 * ( S2 )**( 2 ) * ( kappa )**( 2 ) ) + 32 * ( S1 \
    )**( 2 ) * ( 4 * ( S2 )**( 6 ) + -9 * ( S2 )**( 4 ) * ( kappa )**( 2 \
    ) ) ) ) ) ) ) ) ) ) ) ) ) + ( u )**( 2 ) * ( 64 * ( ( 1 + q ) )**( 6 \
    ) * u * kappa * ( 4 * ( q )**( 6 ) * ( S1 )**( 4 ) * ( ( S1 )**( 2 ) \
    + ( S2 )**( 2 ) ) + ( 4 * ( S2 )**( 4 ) * ( ( S1 )**( 2 ) + ( S2 )**( \
    2 ) ) + ( q * ( 15 * ( S1 )**( 4 ) * ( S2 )**( 2 ) + ( 10 * ( S1 )**( \
    2 ) * ( S2 )**( 4 ) + ( 7 * ( S2 )**( 6 ) + -12 * ( S2 )**( 4 ) * ( \
    kappa )**( 2 ) ) ) ) + ( ( q )**( 5 ) * ( 7 * ( S1 )**( 6 ) + ( 15 * \
    ( S1 )**( 2 ) * ( S2 )**( 4 ) + 2 * ( S1 )**( 4 ) * ( 5 * ( S2 )**( 2 \
    ) + -6 * ( kappa )**( 2 ) ) ) ) + ( -1 * ( q )**( 4 ) * ( 27 * ( S1 \
    )**( 6 ) + ( ( S2 )**( 6 ) + ( ( S1 )**( 4 ) * ( 87 * ( S2 )**( 2 ) + \
    -48 * ( kappa )**( 2 ) ) + ( S1 )**( 2 ) * ( 85 * ( S2 )**( 4 ) + -48 \
    * ( S2 )**( 2 ) * ( kappa )**( 2 ) ) ) ) ) + ( -1 * ( q )**( 2 ) * ( \
    ( S1 )**( 6 ) + ( 85 * ( S1 )**( 4 ) * ( S2 )**( 2 ) + ( 27 * ( S2 \
    )**( 6 ) + ( -48 * ( S2 )**( 4 ) * ( kappa )**( 2 ) + ( S1 )**( 2 ) * \
    ( 87 * ( S2 )**( 4 ) + -48 * ( S2 )**( 2 ) * ( kappa )**( 2 ) ) ) ) ) \
    ) + ( q )**( 3 ) * ( 17 * ( S1 )**( 6 ) + ( 17 * ( S2 )**( 6 ) + ( \
    -40 * ( S2 )**( 4 ) * ( kappa )**( 2 ) + ( ( S1 )**( 4 ) * ( 143 * ( \
    S2 )**( 2 ) + -40 * ( kappa )**( 2 ) ) + 11 * ( S1 )**( 2 ) * ( 13 * \
    ( S2 )**( 4 ) + -8 * ( S2 )**( 2 ) * ( kappa )**( 2 ) ) ) ) ) ) ) ) ) \
    ) ) ) + -16 * ( ( 1 + q ) )**( 6 ) * ( ( S2 )**( 2 ) * ( ( S1 )**( 4 \
    ) + ( -10 * ( S1 )**( 2 ) * ( S2 )**( 2 ) + ( ( S2 )**( 4 ) + 8 * ( \
    S2 )**( 2 ) * ( kappa )**( 2 ) ) ) ) + ( ( q )**( 6 ) * ( S1 )**( 2 ) \
    * ( ( S1 )**( 4 ) + ( ( S2 )**( 4 ) + ( S1 )**( 2 ) * ( -10 * ( S2 \
    )**( 2 ) + 8 * ( kappa )**( 2 ) ) ) ) + ( -4 * ( q )**( 5 ) * ( S1 \
    )**( 2 ) * ( ( S1 )**( 4 ) + ( 7 * ( S2 )**( 4 ) + ( -15 * ( S2 )**( \
    2 ) * ( kappa )**( 2 ) + -1 * ( S1 )**( 2 ) * ( 4 * ( S2 )**( 2 ) + \
    11 * ( kappa )**( 2 ) ) ) ) ) + ( -4 * q * ( S2 )**( 2 ) * ( 7 * ( S1 \
    )**( 4 ) + ( ( S2 )**( 4 ) + ( -11 * ( S2 )**( 2 ) * ( kappa )**( 2 ) \
    + -1 * ( S1 )**( 2 ) * ( 4 * ( S2 )**( 2 ) + 15 * ( kappa )**( 2 ) ) \
    ) ) ) + ( ( q )**( 2 ) * ( ( S1 )**( 6 ) + ( 6 * ( S2 )**( 6 ) + ( \
    -118 * ( S2 )**( 4 ) * ( kappa )**( 2 ) + ( 48 * ( S2 )**( 2 ) * ( \
    kappa )**( 4 ) + ( ( S1 )**( 4 ) * ( 92 * ( S2 )**( 2 ) + -6 * ( \
    kappa )**( 2 ) ) + ( S1 )**( 2 ) * ( 37 * ( S2 )**( 4 ) + -236 * ( S2 \
    )**( 2 ) * ( kappa )**( 2 ) ) ) ) ) ) ) + ( ( q )**( 4 ) * ( 6 * ( S1 \
    )**( 6 ) + ( ( S2 )**( 6 ) + ( -6 * ( S2 )**( 4 ) * ( kappa )**( 2 ) \
    + ( ( S1 )**( 4 ) * ( 37 * ( S2 )**( 2 ) + -118 * ( kappa )**( 2 ) ) \
    + 4 * ( S1 )**( 2 ) * ( 23 * ( S2 )**( 4 ) + ( -59 * ( S2 )**( 2 ) * \
    ( kappa )**( 2 ) + 12 * ( kappa )**( 4 ) ) ) ) ) ) ) + -4 * ( q )**( \
    3 ) * ( ( S1 )**( 6 ) + ( ( S2 )**( 6 ) + ( -18 * ( S2 )**( 4 ) * ( \
    kappa )**( 2 ) + ( 20 * ( S2 )**( 2 ) * ( kappa )**( 4 ) + ( 9 * ( S1 \
    )**( 4 ) * ( 3 * ( S2 )**( 2 ) + -2 * ( kappa )**( 2 ) ) + ( S1 )**( \
    2 ) * ( 27 * ( S2 )**( 4 ) + ( -88 * ( S2 )**( 2 ) * ( kappa )**( 2 ) \
    + 20 * ( kappa )**( 4 ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) )


    coeff1 = \
    ( ( u )**( 4 ) * ( -128 * ( ( -1 + q ) )**( 2 ) * q * ( ( 1 + q ) \
    )**( 5 ) * ( ( S1 )**( 2 ) + -1 * ( S2 )**( 2 ) ) * ( 4 * ( S2 )**( 4 \
    ) * ( ( S1 )**( 2 ) + -2 * ( S2 )**( 2 ) ) + ( ( q )**( 3 ) * ( 8 * ( \
    S1 )**( 6 ) + -4 * ( S1 )**( 4 ) * ( S2 )**( 2 ) ) + ( -1 * ( q )**( \
    2 ) * ( S1 )**( 2 ) * ( 5 * ( S1 )**( 4 ) + ( 6 * ( S1 )**( 2 ) * ( \
    S2 )**( 2 ) + ( S2 )**( 4 ) ) ) + q * ( S2 )**( 2 ) * ( ( S1 )**( 4 ) \
    + ( 6 * ( S1 )**( 2 ) * ( S2 )**( 2 ) + 5 * ( S2 )**( 4 ) ) ) ) ) ) * \
    u + 128 * ( -1 + q ) * q * ( ( 1 + q ) )**( 5 ) * ( -4 * ( S2 )**( 4 \
    ) * ( 2 * ( S1 )**( 2 ) + 3 * ( S2 )**( 2 ) ) + ( 4 * ( q )**( 4 ) * \
    ( 3 * ( S1 )**( 6 ) + 2 * ( S1 )**( 4 ) * ( S2 )**( 2 ) ) + ( ( q \
    )**( 3 ) * ( -29 * ( S1 )**( 6 ) + ( -14 * ( S1 )**( 4 ) * ( S2 )**( \
    2 ) + 3 * ( S1 )**( 2 ) * ( S2 )**( 4 ) ) ) + ( 20 * ( q )**( 2 ) * ( \
    ( S1 )**( 6 ) + -1 * ( S2 )**( 6 ) ) + q * ( -3 * ( S1 )**( 4 ) * ( \
    S2 )**( 2 ) + ( 14 * ( S1 )**( 2 ) * ( S2 )**( 4 ) + 29 * ( S2 )**( 6 \
    ) ) ) ) ) ) ) * kappa ) + ( 32 * ( ( -1 + q ) )**( 2 ) * q * ( ( 1 + \
    q ) )**( 5 ) * kappa * ( ( q )**( 3 ) * ( S1 )**( 2 ) + ( ( S2 )**( 2 \
    ) + ( q * ( ( S1 )**( 2 ) + ( -2 * ( S2 )**( 2 ) + -1 * ( kappa )**( \
    2 ) ) ) + ( q )**( 2 ) * ( -2 * ( S1 )**( 2 ) + ( ( S2 )**( 2 ) + -1 \
    * ( kappa )**( 2 ) ) ) ) ) ) + ( -32 * q * ( ( 1 + q ) )**( 5 ) * u * \
    ( ( q )**( 5 ) * ( S1 )**( 2 ) * ( ( S1 )**( 2 ) + ( -5 * ( S2 )**( 2 \
    ) + 4 * ( kappa )**( 2 ) ) ) + ( ( S2 )**( 2 ) * ( -5 * ( S1 )**( 2 ) \
    + ( ( S2 )**( 2 ) + 4 * ( kappa )**( 2 ) ) ) + ( -1 * ( q )**( 2 ) * \
    ( 4 * ( S1 )**( 4 ) + ( -6 * ( S2 )**( 4 ) + ( 45 * ( S2 )**( 2 ) * ( \
    kappa )**( 2 ) + ( 20 * ( kappa )**( 4 ) + ( S1 )**( 2 ) * ( 10 * ( \
    S2 )**( 2 ) + -29 * ( kappa )**( 2 ) ) ) ) ) ) + ( q * ( ( S1 )**( 4 \
    ) + ( -4 * ( S2 )**( 4 ) + ( 15 * ( S2 )**( 2 ) * ( kappa )**( 2 ) + \
    3 * ( S1 )**( 2 ) * ( 5 * ( S2 )**( 2 ) + -1 * ( kappa )**( 2 ) ) ) ) \
    ) + ( ( q )**( 4 ) * ( -4 * ( S1 )**( 4 ) + ( ( S2 )**( 4 ) + ( -3 * \
    ( S2 )**( 2 ) * ( kappa )**( 2 ) + 15 * ( S1 )**( 2 ) * ( ( S2 )**( 2 \
    ) + ( kappa )**( 2 ) ) ) ) ) + ( q )**( 3 ) * ( 6 * ( S1 )**( 4 ) + ( \
    -4 * ( S2 )**( 4 ) + ( 29 * ( S2 )**( 2 ) * ( kappa )**( 2 ) + ( -20 \
    * ( kappa )**( 4 ) + -5 * ( S1 )**( 2 ) * ( 2 * ( S2 )**( 2 ) + 9 * ( \
    kappa )**( 2 ) ) ) ) ) ) ) ) ) ) ) + ( u )**( 2 ) * ( 32 * q * ( ( 1 \
    + q ) )**( 5 ) * kappa * ( 8 * ( q )**( 5 ) * ( S1 )**( 2 ) * ( 2 * ( \
    S1 )**( 2 ) + ( S2 )**( 2 ) ) + ( 8 * ( S2 )**( 2 ) * ( ( S1 )**( 2 ) \
    + 2 * ( S2 )**( 2 ) ) + ( q * ( -3 * ( S1 )**( 4 ) + ( -22 * ( S1 \
    )**( 2 ) * ( S2 )**( 2 ) + ( 17 * ( S2 )**( 4 ) + 4 * ( S2 )**( 2 ) * \
    ( kappa )**( 2 ) ) ) ) + ( ( q )**( 2 ) * ( 55 * ( S1 )**( 4 ) + ( \
    -85 * ( S2 )**( 4 ) + ( 12 * ( S2 )**( 2 ) * ( kappa )**( 2 ) + 2 * ( \
    S1 )**( 2 ) * ( 7 * ( S2 )**( 2 ) + -40 * ( kappa )**( 2 ) ) ) ) ) + \
    ( ( q )**( 4 ) * ( 17 * ( S1 )**( 4 ) + ( -3 * ( S2 )**( 4 ) + ( S1 \
    )**( 2 ) * ( -22 * ( S2 )**( 2 ) + 4 * ( kappa )**( 2 ) ) ) ) + ( q \
    )**( 3 ) * ( -85 * ( S1 )**( 4 ) + ( 55 * ( S2 )**( 4 ) + ( -80 * ( \
    S2 )**( 2 ) * ( kappa )**( 2 ) + 2 * ( S1 )**( 2 ) * ( 7 * ( S2 )**( \
    2 ) + 6 * ( kappa )**( 2 ) ) ) ) ) ) ) ) ) ) + -32 * q * ( ( 1 + q ) \
    )**( 5 ) * u * ( 4 * ( S2 )**( 2 ) * ( ( S1 )**( 4 ) + ( -8 * ( S1 \
    )**( 2 ) * ( S2 )**( 2 ) + ( 3 * ( S2 )**( 4 ) + 4 * ( S2 )**( 2 ) * \
    ( kappa )**( 2 ) ) ) ) + ( 4 * ( q )**( 5 ) * ( S1 )**( 2 ) * ( 3 * ( \
    S1 )**( 4 ) + ( ( S2 )**( 4 ) + ( S1 )**( 2 ) * ( -8 * ( S2 )**( 2 ) \
    + 4 * ( kappa )**( 2 ) ) ) ) + ( ( q )**( 4 ) * ( ( S1 )**( 6 ) + ( \
    -1 * ( S2 )**( 6 ) + ( ( S1 )**( 4 ) * ( 85 * ( S2 )**( 2 ) + -76 * ( \
    kappa )**( 2 ) ) + ( S1 )**( 2 ) * ( -37 * ( S2 )**( 4 ) + 12 * ( S2 \
    )**( 2 ) * ( kappa )**( 2 ) ) ) ) ) + ( ( q )**( 3 ) * ( -39 * ( S1 \
    )**( 6 ) + ( 3 * ( S2 )**( 4 ) * ( 9 * ( S2 )**( 2 ) + -40 * ( kappa \
    )**( 2 ) ) + ( ( S1 )**( 4 ) * ( -103 * ( S2 )**( 2 ) + 156 * ( kappa \
    )**( 2 ) ) + ( S1 )**( 2 ) * ( 83 * ( S2 )**( 4 ) + 12 * ( S2 )**( 2 \
    ) * ( kappa )**( 2 ) ) ) ) ) + ( q * ( -1 * ( S1 )**( 6 ) + ( -37 * ( \
    S1 )**( 4 ) * ( S2 )**( 2 ) + ( ( S2 )**( 6 ) + ( -76 * ( S2 )**( 4 ) \
    * ( kappa )**( 2 ) + ( S1 )**( 2 ) * ( 85 * ( S2 )**( 4 ) + 12 * ( S2 \
    )**( 2 ) * ( kappa )**( 2 ) ) ) ) ) ) + ( q )**( 2 ) * ( 27 * ( S1 \
    )**( 6 ) + ( ( S1 )**( 4 ) * ( 83 * ( S2 )**( 2 ) + -120 * ( kappa \
    )**( 2 ) ) + ( ( S1 )**( 2 ) * ( -103 * ( S2 )**( 4 ) + 12 * ( S2 \
    )**( 2 ) * ( kappa )**( 2 ) ) + -39 * ( ( S2 )**( 6 ) + -4 * ( S2 \
    )**( 4 ) * ( kappa )**( 2 ) ) ) ) ) ) ) ) ) ) ) ) ) )

    coeff2 = \
    ( 32 * ( q )**( 2 ) * ( ( 1 + q ) )**( 4 ) * u * kappa * ( ( ( -1 + \
    q ) )**( 2 ) * ( -1 + ( 18 * q + 7 * ( q )**( 2 ) ) ) * ( S1 )**( 2 ) \
    + ( -1 * ( ( -1 + q ) )**( 2 ) * ( -7 + ( -18 * q + ( q )**( 2 ) ) ) \
    * ( S2 )**( 2 ) + -16 * q * ( 1 + ( 3 * q + ( q )**( 2 ) ) ) * ( \
    kappa )**( 2 ) ) ) + ( -16 * ( ( -1 + q ) )**( 2 ) * ( q )**( 2 ) * ( \
    ( 1 + q ) )**( 4 ) * ( ( ( -1 + q ) )**( 2 ) * ( S1 )**( 2 ) + ( ( ( \
    -1 + q ) )**( 2 ) * ( S2 )**( 2 ) + -1 * ( 1 + ( 4 * q + ( q )**( 2 ) \
    ) ) * ( kappa )**( 2 ) ) ) + ( ( u )**( 2 ) * ( -16 * ( q )**( 2 ) * \
    ( ( 1 + q ) )**( 4 ) * ( ( ( -1 + q ) )**( 2 ) * ( -1 + ( 40 * q + 23 \
    * ( q )**( 2 ) ) ) * ( S1 )**( 4 ) + ( -1 * ( ( -1 + q ) )**( 2 ) * ( \
    -23 + ( -40 * q + ( q )**( 2 ) ) ) * ( S2 )**( 4 ) + ( -8 * ( -1 + ( \
    11 * q + ( 2 * ( q )**( 2 ) + 12 * ( q )**( 3 ) ) ) ) * ( S2 )**( 2 ) \
    * ( kappa )**( 2 ) + ( -16 * ( q )**( 2 ) * ( kappa )**( 4 ) + -2 * ( \
    S1 )**( 2 ) * ( ( ( -1 + q ) )**( 2 ) * ( 11 + ( -24 * q + 11 * ( q \
    )**( 2 ) ) ) * ( S2 )**( 2 ) + 4 * q * ( 12 + ( 2 * q + ( 11 * ( q \
    )**( 2 ) + -1 * ( q )**( 3 ) ) ) ) * ( kappa )**( 2 ) ) ) ) ) ) + 256 \
    * ( q )**( 2 ) * ( ( 1 + q ) )**( 4 ) * u * kappa * ( ( q )**( 4 ) * \
    ( S1 )**( 2 ) * ( 5 * ( S1 )**( 2 ) + ( S2 )**( 2 ) ) + ( ( S2 )**( 2 \
    ) * ( ( S1 )**( 2 ) + 5 * ( S2 )**( 2 ) ) + ( -2 * q * ( 3 * ( S1 \
    )**( 4 ) + ( 4 * ( S1 )**( 2 ) * ( S2 )**( 2 ) + ( 9 * ( S2 )**( 4 ) \
    + -1 * ( S2 )**( 2 ) * ( kappa )**( 2 ) ) ) ) + ( -2 * ( q )**( 3 ) * \
    ( 9 * ( S1 )**( 4 ) + ( 3 * ( S2 )**( 4 ) + ( S1 )**( 2 ) * ( 4 * ( \
    S2 )**( 2 ) + -1 * ( kappa )**( 2 ) ) ) ) + 4 * ( q )**( 2 ) * ( 4 * \
    ( S1 )**( 4 ) + ( 4 * ( S2 )**( 4 ) + ( -1 * ( S2 )**( 2 ) * ( kappa \
    )**( 2 ) + ( S1 )**( 2 ) * ( 5 * ( S2 )**( 2 ) + -1 * ( kappa )**( 2 \
    ) ) ) ) ) ) ) ) ) ) + ( u )**( 4 ) * ( 256 * ( q )**( 2 ) * ( ( 1 + q \
    ) )**( 4 ) * ( ( ( S1 )**( 2 ) + -1 * ( S2 )**( 2 ) ) )**( 2 ) * ( ( \
    ( q )**( 2 ) * ( S1 )**( 2 ) + ( ( S2 )**( 2 ) + -1 * q * ( ( S1 )**( \
    2 ) + ( S2 )**( 2 ) ) ) ) )**( 2 ) * ( u )**( 2 ) + ( -512 * ( -1 + q \
    ) * ( q )**( 2 ) * ( ( 1 + q ) )**( 4 ) * ( ( q )**( 3 ) * ( S1 )**( \
    4 ) * ( ( S1 )**( 2 ) + ( S2 )**( 2 ) ) + ( -1 * ( S2 )**( 4 ) * ( ( \
    S1 )**( 2 ) + ( S2 )**( 2 ) ) + ( -1 * ( q )**( 2 ) * ( 2 * ( S1 )**( \
    6 ) + ( ( S1 )**( 4 ) * ( S2 )**( 2 ) + 3 * ( S1 )**( 2 ) * ( S2 )**( \
    4 ) ) ) + q * ( 3 * ( S1 )**( 4 ) * ( S2 )**( 2 ) + ( ( S1 )**( 2 ) * \
    ( S2 )**( 4 ) + 2 * ( S2 )**( 6 ) ) ) ) ) ) * u * kappa + -128 * ( q \
    )**( 2 ) * ( ( 1 + q ) )**( 4 ) * ( ( S2 )**( 2 ) * ( ( S1 )**( 4 ) + \
    ( -8 * ( S1 )**( 2 ) * ( S2 )**( 2 ) + ( 11 * ( S2 )**( 4 ) + -2 * ( \
    S2 )**( 2 ) * ( kappa )**( 2 ) ) ) ) + ( ( q )**( 4 ) * ( S1 )**( 2 ) \
    * ( 11 * ( S1 )**( 4 ) + ( ( S2 )**( 4 ) + -2 * ( S1 )**( 2 ) * ( 4 * \
    ( S2 )**( 2 ) + ( kappa )**( 2 ) ) ) ) + ( 2 * ( q )**( 2 ) * ( 11 * \
    ( S1 )**( 6 ) + ( 11 * ( S2 )**( 6 ) + ( -6 * ( S2 )**( 4 ) * ( kappa \
    )**( 2 ) + ( -1 * ( S1 )**( 4 ) * ( 5 * ( S2 )**( 2 ) + 6 * ( kappa \
    )**( 2 ) ) + -5 * ( S1 )**( 2 ) * ( ( S2 )**( 4 ) + 2 * ( S2 )**( 2 ) \
    * ( kappa )**( 2 ) ) ) ) ) ) + ( q * ( -4 * ( S1 )**( 6 ) + ( -5 * ( \
    S1 )**( 4 ) * ( S2 )**( 2 ) + ( -29 * ( S2 )**( 6 ) + ( 12 * ( S2 \
    )**( 4 ) * ( kappa )**( 2 ) + 2 * ( S1 )**( 2 ) * ( 11 * ( S2 )**( 4 \
    ) + 6 * ( S2 )**( 2 ) * ( kappa )**( 2 ) ) ) ) ) ) + ( q )**( 3 ) * ( \
    -29 * ( S1 )**( 6 ) + ( -4 * ( S2 )**( 6 ) + ( 2 * ( S1 )**( 4 ) * ( \
    11 * ( S2 )**( 2 ) + 6 * ( kappa )**( 2 ) ) + ( S1 )**( 2 ) * ( -5 * \
    ( S2 )**( 4 ) + 12 * ( S2 )**( 2 ) * ( kappa )**( 2 ) ) ) ) ) ) ) ) ) \
    ) ) ) ) )

    coeff3 = \
    ( -32 * ( ( -1 + q ) )**( 2 ) * ( q )**( 3 ) * ( ( 1 + q ) )**( 4 ) \
    * kappa + ( ( u )**( 4 ) * ( 512 * ( q )**( 3 ) * ( ( 1 + q ) )**( 3 \
    ) * ( ( S1 )**( 2 ) + -1 * ( S2 )**( 2 ) ) * ( ( S2 )**( 2 ) * ( ( S1 \
    )**( 2 ) + -2 * ( S2 )**( 2 ) ) + ( ( q )**( 3 ) * ( 2 * ( S1 )**( 4 \
    ) + -1 * ( S1 )**( 2 ) * ( S2 )**( 2 ) ) + ( -1 * ( q )**( 2 ) * ( 3 \
    * ( S1 )**( 4 ) + ( -1 * ( S1 )**( 2 ) * ( S2 )**( 2 ) + ( S2 )**( 4 \
    ) ) ) + q * ( ( S1 )**( 4 ) + ( -1 * ( S1 )**( 2 ) * ( S2 )**( 2 ) + \
    3 * ( S2 )**( 4 ) ) ) ) ) ) * u + -512 * ( q )**( 3 ) * ( ( 1 + q ) \
    )**( 3 ) * ( 2 * ( S1 )**( 2 ) * ( S2 )**( 2 ) + ( 3 * ( S2 )**( 4 ) \
    + ( ( q )**( 3 ) * ( 3 * ( S1 )**( 4 ) + 2 * ( S1 )**( 2 ) * ( S2 \
    )**( 2 ) ) + ( q * ( 3 * ( S1 )**( 4 ) + ( -3 * ( S1 )**( 2 ) * ( S2 \
    )**( 2 ) + -5 * ( S2 )**( 4 ) ) ) + ( q )**( 2 ) * ( -5 * ( S1 )**( 4 \
    ) + ( -3 * ( S1 )**( 2 ) * ( S2 )**( 2 ) + 3 * ( S2 )**( 4 ) ) ) ) ) \
    ) ) * kappa ) + ( 32 * ( q )**( 3 ) * ( ( 1 + q ) )**( 3 ) * u * ( -1 \
    * ( ( -1 + q ) )**( 2 ) * ( 5 + 3 * q ) * ( S1 )**( 2 ) + ( -1 * ( ( \
    -1 + q ) )**( 2 ) * ( 3 + 5 * q ) * ( S2 )**( 2 ) + 4 * ( 1 + ( 9 * q \
    + ( 9 * ( q )**( 2 ) + ( q )**( 3 ) ) ) ) * ( kappa )**( 2 ) ) ) + ( \
    u )**( 2 ) * ( 128 * ( q )**( 3 ) * ( ( 1 + q ) )**( 3 ) * kappa * ( \
    ( -2 + ( 5 * q + -19 * ( q )**( 2 ) ) ) * ( S1 )**( 2 ) + -1 * q * ( \
    ( 19 + ( -5 * q + 2 * ( q )**( 2 ) ) ) * ( S2 )**( 2 ) + 4 * ( 1 + q \
    ) * ( kappa )**( 2 ) ) ) + 128 * ( q )**( 3 ) * ( ( 1 + q ) )**( 3 ) \
    * u * ( ( 1 + ( -14 * q + ( 20 * ( q )**( 2 ) + -5 * ( q )**( 3 ) ) ) \
    ) * ( S1 )**( 4 ) + ( ( -5 + ( 20 * q + ( -14 * ( q )**( 2 ) + ( q \
    )**( 3 ) ) ) ) * ( S2 )**( 4 ) + ( 4 * ( 1 + ( -1 * q + 3 * ( q )**( \
    2 ) ) ) * ( S2 )**( 2 ) * ( kappa )**( 2 ) + ( S1 )**( 2 ) * ( 2 * ( \
    -2 + ( q + ( ( q )**( 2 ) + -2 * ( q )**( 3 ) ) ) ) * ( S2 )**( 2 ) + \
    4 * q * ( 3 + ( -1 * q + ( q )**( 2 ) ) ) * ( kappa )**( 2 ) ) ) ) ) \
    ) ) ) )

    coeff4 = \
    ( 16 * ( q )**( 4 ) * ( ( -1 + ( q )**( 2 ) ) )**( 2 ) + ( 256 * ( q \
    )**( 4 ) * ( ( 1 + q ) )**( 2 ) * ( ( 1 + ( -6 * q + 6 * ( q )**( 2 ) \
    ) ) * ( S1 )**( 4 ) + ( -2 * ( 3 + ( -5 * q + 3 * ( q )**( 2 ) ) ) * \
    ( S1 )**( 2 ) * ( S2 )**( 2 ) + ( 6 + ( -6 * q + ( q )**( 2 ) ) ) * ( \
    S2 )**( 4 ) ) ) * ( u )**( 4 ) + ( -256 * ( q )**( 4 ) * ( ( 1 + q ) \
    )**( 2 ) * ( 1 + ( 3 * q + ( q )**( 2 ) ) ) * u * kappa + ( u )**( 2 \
    ) * ( -512 * ( q )**( 4 ) * ( ( 1 + q ) )**( 2 ) * ( ( 1 + ( -1 * q + \
    3 * ( q )**( 2 ) ) ) * ( S1 )**( 2 ) + ( 3 + ( -1 * q + ( q )**( 2 ) \
    ) ) * ( S2 )**( 2 ) ) * u * kappa + 128 * ( q )**( 4 ) * ( ( 1 + q ) \
    )**( 2 ) * ( ( -4 + ( 7 * q + ( q )**( 2 ) ) ) * ( S1 )**( 2 ) + ( ( \
    1 + ( 7 * q + -4 * ( q )**( 2 ) ) ) * ( S2 )**( 2 ) + 2 * ( 1 + ( 4 * \
    q + ( q )**( 2 ) ) ) * ( kappa )**( 2 ) ) ) ) ) ) )

    coeff5 = \
    ( 128 * ( q )**( 5 ) * ( ( 1 + q ) )**( 2 ) * u + ( u )**( 2 ) * ( \
    512 * ( q )**( 5 ) * ( 1 + q ) * ( ( -1 + 2 * q ) * ( S1 )**( 2 ) + \
    -1 * ( -2 + q ) * ( S2 )**( 2 ) ) * u + -512 * ( q )**( 5 ) * ( ( 1 + \
    q ) )**( 2 ) * kappa ) )

    coeff6 = \
    256 * ( q )**( 6 ) * ( u )**( 2 )

    return toarray(coeff6, coeff5, coeff4, coeff3, coeff2, coeff1, coeff0)


def xiresonances(J,r,q,chi1,chi2):
    """
    Effective spin of the two spin-orbit resonances. The resonances minimizes and maximizes xi for a given value of J. The minimum corresponds to either DeltaPhi=0 or DeltaPhi=pi, the maximum always corresponds to DeltaPhi=pi.

    Call
    ----
    ximin,ximax = xiresonances(J,r,q,chi1,chi2)

    Parameters
    ----------
    J: float
    	Magnitude of the total angular momentum.
    r: float
    	Binary separation.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    ximin: float
    	Minimum value of the effective spin xi.
    ximax: float
    	Maximum value of the effective spin xi.
    """

    #Altough there are 6 solutions in general, we know that only two can lie between Smin and Smax.
    kappa = eval_kappa(J, r, q)
    u = eval_u(r, q)

    Smin,Smax = Slimits_LJS1S2(J,r,q,chi1,chi2)
    xiroots= wraproots(xidiscriminant_coefficients,kappa,u,q,chi1,chi2)
    xiroots = xiroots[np.isfinite(xiroots)]

    def _compute(Smin,Smax,J,r,xiroots,q,chi1,chi2):

        with np.errstate(invalid='ignore'):
            Sroots = np.array([Satresonance(J,r,x,q,chi1,chi2) for x in xiroots])
            xires = xiroots[np.logical_and(Sroots>Smin, Sroots<Smax)]
        return xires

    if np.ndim(xiroots)==1:
        ximin,ximax =_compute(Smin,Smax,J,r,xiroots,q,chi1,chi2)
    else:
        ximin,ximax =np.array(list(map(_compute, Smin,Smax,J,r,xiroots,q,chi1,chi2))).T

    return toarray(ximin,ximax)


def xilimits(J=None,r=None,q=None,chi1=None,chi2=None):
    """
    Limits on the projected effective spin. The contraints considered depend on the inputs provided.
    - If q, chi1, and chi2 are provided, enforce xi = (1+q)S1.L + (1+1/q)S2.L.
    - If J, r, q, chi1, and chi2 are provided, the limits are given by the two spin-orbit resonances.

    Call
    ----
    ximin,ximax = xilimits(J = None,r = None,q = None,chi1 = None,chi2 = None)

    Parameters
    ----------
    J: float, optional (default: None)
    	Magnitude of the total angular momentum.
    r: float, optional (default: None)
    	Binary separation.
    q: float, optional (default: None)
    	Mass ratio: 0<=q<=1.
    chi1: float, optional (default: None)
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float, optional (default: None)
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    ximin: float
    	Minimum value of the effective spin xi.
    ximax: float
    	Maximum value of the effective spin xi.
    """

    if J is None and r is None and q is not None and chi1 is not None and chi2 is not None:
        ximin,ximax = xilimits_definition(q,chi1,chi2)


    elif J is not None and r is not None and q is not None and chi1 is not None and chi2 is not None:
        #TODO: Assert that the xi values are compatible with q,chi1,chi2 (either explicitely or with a generic 'limits_check' function)
        ximin,ximax = xiresonances(J,r,q,chi1,chi2)

    else:
        raise TypeError

    return toarray(ximin,ximax)


def Slimits_S1S2(q,chi1,chi2):
    """
    Limits on the total spin magnitude due to the vector relation S=S1+S2.

    Call
    ----
    Smin,Smax = Slimits_S1S2(q,chi1,chi2)

    Parameters
    ----------
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    Smin: float
    	Minimum value of the total spin S.
    Smax: float
    	Maximum value of the total spin S.
    """

    S1,S2= spinmags(q,chi1,chi2)
    Smin = np.abs(S1-S2)
    Smax = S1+S2

    return toarray(Smin,Smax)


def Slimits_LJ(J,r,q):
    """
    Limits on the total spin magnitude due to the vector relation S=J-L.

    Call
    ----
    Smin,Smax = Slimits_LJ(J,r,q)

    Parameters
    ----------
    J: float
    	Magnitude of the total angular momentum.
    r: float
    	Binary separation.
    q: float
    	Mass ratio: 0<=q<=1.

    Returns
    -------
    Smin: float
    	Minimum value of the total spin S.
    Smax: float
    	Maximum value of the total spin S.
    """

    L= angularmomentum(r,q)
    Smin = np.abs(J-L)
    Smax = J+L

    return toarray(Smin,Smax)


def Slimits_LJS1S2(J,r,q,chi1,chi2):
    """
    Limits on the total spin magnitude due to the vector relations S=S1+S2 and S=J-L.

    Call
    ----
    Smin,Smax = Slimits_LJS1S2(J,r,q,chi1,chi2)

    Parameters
    ----------
    J: float
    	Magnitude of the total angular momentum.
    r: float
    	Binary separation.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    Smin: float
    	Minimum value of the total spin S.
    Smax: float
    	Maximum value of the total spin S.
    """

    SminS1S2,SmaxS1S2 = Slimits_S1S2(q,chi1,chi2)
    SminLJ, SmaxLJ = Slimits_LJ(J,r,q)
    Smin = np.maximum(SminS1S2,SminLJ)
    Smax = np.minimum(SmaxS1S2,SmaxLJ)

    return toarray(Smin,Smax)


def Scubic_coefficients(kappa,u,xi,q,chi1,chi2):
    """
    Coefficients of the cubic equation in S^2 that identifies the effective potentials.

    Call
    ----
    coeff3,coeff2,coeff1,coeff0 = Scubic_coefficients(kappa,u,xi,q,chi1,chi2)

    Parameters
    ----------
    kappa: float
    	Regularized angular momentum (J^2-L^2)/(2L).
    u: float
    	Compactified separation 1/(2L).
    xi: float
    	Effective spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    coeff3: float
    	Coefficient to the x^3 term in polynomial.
    coeff2: float
    	Coefficient to the x^2 term in polynomial.
    coeff1: float
    	Coefficient to the x^1 term in polynomial.
    coeff0: float
    	Coefficient to the x^0 term in polynomial.
    """

    kappa,u,xi,q = toarray(kappa,u,xi,q)
    S1,S2 = spinmags(q,chi1,chi2)

    coeff3 = \
    q * ( ( 1 + q ) )**( 2 ) * ( u )**( 2 )

    coeff2 = \
    ( 1/4 * ( ( 1 + q ) )**( 2 ) + ( -1/2 * q * ( ( 1 + q ) )**( 2 ) + ( \
    1/4 * ( q )**( 2 ) * ( ( 1 + q ) )**( 2 ) + ( ( -1 * q * ( ( 1 + q ) \
    )**( 2 ) * ( S1 )**( 2 ) + ( ( q )**( 2 ) * ( ( 1 + q ) )**( 2 ) * ( \
    S1 )**( 2 ) + ( ( ( 1 + q ) )**( 2 ) * ( S2 )**( 2 ) + -1 * q * ( ( 1 \
    + q ) )**( 2 ) * ( S2 )**( 2 ) ) ) ) * ( u )**( 2 ) + u * ( q * ( ( 1 \
    + q ) )**( 2 ) * xi + -2 * q * ( ( 1 + q ) )**( 2 ) * kappa ) ) ) ) )

    coeff1 = \
    ( -1/2 * ( 1 + -1 * ( q )**( 2 ) ) * ( S1 )**( 2 ) + ( 1/2 * ( q \
    )**( 2 ) * ( 1 + -1 * ( q )**( 2 ) ) * ( S1 )**( 2 ) + ( -1/2 * ( 1 + \
    -1 * ( q )**( 2 ) ) * ( S2 )**( 2 ) + ( 1/2 * ( q )**( 2 ) * ( 1 + -1 \
    * ( q )**( 2 ) ) * ( S2 )**( 2 ) + ( u * ( -1 * q * ( 1 + -1 * ( q \
    )**( 2 ) ) * ( S1 )**( 2 ) * ( xi + -2 * kappa ) + ( q * ( 1 + -1 * ( \
    q )**( 2 ) ) * ( S2 )**( 2 ) * ( xi + -2 * kappa ) + ( 2 * ( q )**( 2 \
    ) * ( 1 + -1 * ( q )**( 2 ) ) * ( S1 )**( 2 ) * kappa + -2 * ( 1 + -1 \
    * ( q )**( 2 ) ) * ( S2 )**( 2 ) * kappa ) ) ) + q * ( kappa * ( -1 * \
    xi + kappa ) + ( ( q )**( 2 ) * kappa * ( -1 * xi + kappa ) + q * ( ( \
    xi )**( 2 ) + ( -2 * xi * kappa + 2 * ( kappa )**( 2 ) ) ) ) ) ) ) ) \
    ) )

    coeff0 = \
    1/4 * ( -1 + ( q )**( 2 ) ) * ( ( -1 + ( q )**( 2 ) ) * ( S1 )**( 4 \
    ) + ( ( -1 + ( q )**( 2 ) ) * ( S2 )**( 4 ) + ( -4 * ( S2 )**( 2 ) * \
    kappa * ( -1 * q * xi + ( kappa + q * kappa ) ) + ( S1 )**( 2 ) * ( \
    -2 * ( -1 + ( q )**( 2 ) ) * ( S2 )**( 2 ) + 4 * q * kappa * ( -1 * \
    xi + ( kappa + q * kappa ) ) ) ) ) )

    return toarray(coeff3, coeff2, coeff1, coeff0)


# TODO: this is a case where we use 2 for square. Fix docstrings
def S2roots(J,r,xi,q,chi1,chi2):
    """
    Roots of the cubic equation in S^2 that identifies the effective potentials.

    Parameters
    ----------
    kappa: float
        Asymptotic momentum (J^2-L^2)/(2L).
    u: float
        Compactified momentum 1/(2L).
    xi: float
        Effective spin
    q: float
        Mass ratio: 0 <= q <= 1.
    chi1: float
        Dimensionless spin of the primary black hole: 0 <= chi1 <= 1.
    chi2: float
        Dimensionless spin of the secondary black hole: 0 <= chi1 <= 1.

    Returns
    -------
    Sminus2:
        Lowest physical root (or unphysical).
    Splus2:
        Highest physical root (or unphysical).
    S32: float
        Spurious root.
    """

    kappa = eval_kappa(J, r, q)
    u = eval_u(r, q)

    S32, Sminus2, Splus2 = wraproots(Scubic_coefficients,kappa,u,xi,q,chi1,chi2)

    return toarray(Sminus2,Splus2,S32)


def Slimits_plusminus(J,r,xi,q,chi1,chi2):
    """
    Limits on the total spin magnitude compatible with both J and xi.

    Call
    ----
    Smin,Smax = Slimits_plusminus(J,r,xi,q,chi1,chi2)

    Parameters
    ----------
    J: float
    	Magnitude of the total angular momentum.
    r: float
    	Binary separation.
    xi: float
    	Effective spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    Smin: float
    	Minimum value of the total spin S.
    Smax: float
    	Maximum value of the total spin S.
    """

    Sminus2,Splus2,_= S2roots(J,r,xi,q,chi1,chi2)
    with np.errstate(invalid='ignore'):
        Smin=Sminus2**0.5
        Smax=Splus2**0.5

    return toarray(Smin,Smax)


def Satresonance(J,r,xi,q,chi1,chi2):
    """
    Assuming that the inputs correspond to a spin-orbit resonance, find the corresponding value of S. There will be two roots that are conincident if not for numerical errors: for concreteness, return the mean of the real part. This function does not check that the input is a resonance; it is up to the user.

    Call
    ----
    S = Satresonance(J,r,xi,q,chi1,chi2)

    Parameters
    ----------
    J: float
    	Magnitude of the total angular momentum.
    r: float
    	Binary separation.
    xi: float
    	Effective spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    S: float
    	Magnitude of the total spin.
    """

    kappa = eval_kappa(J, r, q)
    u = eval_u(r, q)
    coeffs = Scubic_coefficients(kappa,u,xi,q,chi1,chi2)

    if np.ndim(coeffs)==1:
        Sres = np.mean(np.real(np.roots(coeffs))[1:]**0.5)
    else:
        Sres = np.array([np.mean(np.real(np.roots(x))[1:]**0.5) for x in coeffs.T])

    return Sres


def Slimits(J=None,r=None,xi=None,q=None,chi1=None,chi2=None):
    """
    Limits on the total spin magnitude. The contraints considered depend on the inputs provided.
    - If q, chi1, and chi2 are provided, enforce S=S1+S2.
    - If J, r, and q are provided, enforce S=J-L.
    - If J, r, q, chi1, and chi2 are provided, enforce S=S1+S2 and S=J-L.
    - If J, r, xi, q, chi1, and chi2 are provided, compute solve the cubic equation of the effective potentials (Sminus and Splus).

    Call
    ----
    Smin,Smax = Slimits(J = None,r = None,xi = None,q = None,chi1 = None,chi2 = None)

    Parameters
    ----------
    J: float, optional (default: None)
    	Magnitude of the total angular momentum.
    r: float, optional (default: None)
    	Binary separation.
    xi: float, optional (default: None)
    	Effective spin.
    q: float, optional (default: None)
    	Mass ratio: 0<=q<=1.
    chi1: float, optional (default: None)
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float, optional (default: None)
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    Smin: float
    	Minimum value of the total spin S.
    Smax: float
    	Maximum value of the total spin S.
    """

    if J is None and r is None and xi is None and q is not None and chi1 is not None and chi2 is not None:
        Smin,Smax = Slimits_S1S2(q,chi1,chi2)

    elif J is not None and r is not None and xi is None and q is not None and chi1 is None and chi2 is None:
        Smin,Smax = Slimits_LJ(J,r,q)

    elif J is not None and r is not None and xi is None and q is not None and chi1 is not None and chi2 is not None:
        Smin,Smax = Slimits_LJS1S2(J,r,q,chi1,chi2)

    elif J is not None and r is not None and xi is not None and q is not None and chi1 is not None and chi2 is not None:
        #TODO: Assert that Slimits_LJS1S2 is also respected (either explicitely or with a generic 'limits_check' function)
        Smin,Smax = Slimits_plusminus(J,r,xi,q,chi1,chi2)

    else:
        raise TypeError

    return toarray(Smin,Smax)


# TODO: Check inter-compatibility of Slimits, Jlimits, xilimits
# TODO: check docstrings
# Tags for each limit check that fails?
# Davide: Does this function uses only Jlimits and xilimits or also Slimits? Move later?
def limits_check(S=None, J=None, r=None, xi=None, q=None, chi1=None, chi2=None):
    """
    Check if the inputs are consistent with the geometrical constraints.

    Parameters
    ----------
    S: float
        Magnitude of the total spin.
    J: float, optional
        Magnitude of the total angular momentum.
    r: float, optional
        Binary separation.
    xi: float, optional
        Effective spin
    q: float
        Mass ratio: 0 <= q <= 1.
    chi1: float, optional
        Dimensionless spin of the primary black hole: 0 <= chi1 <= 1.
    chi2: float, optional
        Dimensionless spin of the secondary black hole: 0 <= chi1 <= 1.

    Returns
    -------
    check: bool
        True if the given parameters are compatible with each other, false if not.
    """
    # q, ch1, chi2
    # 0, 1

    # J: r, xi, q, chi1, chi2
    # r, q, chi1, chi2 -> Jlimits_LS1S2
    # r, xi, q, chi1, chi2 -> Jresonances

    # xi: J, r, q, chi1, chi2
    # q, chi1, chi2 -> xilimits_definition
    # J, r, q, chi1, chi2 -> xiresonances

    # S: J, r, xi, q, chi1, chi2
    # q, chi1, chi2 -> Slimits_S1S2
    # J, r, q -> Slimits_LJ
    # J, r, q, chi1, chi2 -> Slimits_LJS1S2
    # J, r, xi, q, chi1, chi2 -> Slimits_plusminus

    def _limits_check(testvalue, interval):
        """Check if a value is within a given interval"""
        return np.logical_and(testvalue>=interval[0], testvalue<=interval[1])

    Slim = Slimits(J, r, xi, q, chi1, chi2)
    Sbool = _limits_check(S, Slim)

    Jlim = Jlimits(r, xi, q, chi1, chi2)
    Jbool = _limits_check(J, Jlim)

    xilim = xilimits(J, r, q, chi1, chi2)
    xibool = _limits_check(xi, xilim)

    check = all((Sbool, Jbool, xibool))

    if r is not None:
        rbool = _limits_check(r, [10.0, np.inf])
        check = all((check, rbool))

    if q is not None:
        qbool = _limits_check(q, [0.0, 1.0])
        check = all((check, qbool))

    if chi1 is not None:
        chi1bool = _limits_check(chi1, [0.0, 1.0])
        check = all((check, chi1bool))

    if chi2 is not None:
        chi2bool = _limits_check(chi2, [0.0, 1.0])
        check = all((check, chi2bool))

    return check


#### Evaluations and conversions ####

# TODO Should this be called eval_xi?
def effectivepotential_Sphi(S,varphi,J,r,q,chi1,chi2):
    """
    Effective spin as a function of total spin magnitude S, nutation angle varphi and total angularm momentum J.

    Call
    ----
    xi = effectivepotential_Sphi(S,varphi,J,r,q,chi1,chi2)

    Parameters
    ----------
    S: float
    	Magnitude of the total spin.
    varphi: float
    	Generalized nutation coordinate (Eq 9 in arxiv:1506.03492).
    J: float
    	Magnitude of the total angular momentum.
    r: float
    	Binary separation.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    xi: float
    	Effective spin.
    """

    S,varphi,J,q=toarray(S,varphi,J,q)
    S1,S2 = spinmags(q,chi1,chi2)
    L = angularmomentum(r,q)

    xi = \
    1/4 * ( L )**( -1 ) * ( q )**( -1 ) * ( S )**( -2 ) * ( ( ( J )**( 2 \
    ) + ( -1 * ( L )**( 2 ) + -1 * ( S )**( 2 ) ) ) * ( ( ( 1 + q ) )**( \
    2 ) * ( S )**( 2 ) + ( -1 + ( q )**( 2 ) ) * ( ( S1 )**( 2 ) + -1 * ( \
    S2 )**( 2 ) ) ) + -1 * ( 1 + -1 * ( q )**( 2 ) ) * ( ( ( J )**( 2 ) + \
    -1 * ( ( L + -1 * S ) )**( 2 ) ) )**( 1/2 ) * ( ( -1 * ( J )**( 2 ) + \
    ( ( L + S ) )**( 2 ) ) )**( 1/2 ) * ( ( ( S )**( 2 ) + -1 * ( ( S1 + \
    -1 * S2 ) )**( 2 ) ) )**( 1/2 ) * ( ( -1 * ( S )**( 2 ) + ( ( S1 + S2 \
    ) )**( 2 ) ) )**( 1/2 ) * np.cos( varphi ) )

    return xi


def effectivepotential_plus(S,J,r,q,chi1,chi2):
    """
    Upper effective potential.

    Call
    ----
    xi = effectivepotential_plus(S,J,r,q,chi1,chi2)

    Parameters
    ----------
    S: float
    	Magnitude of the total spin.
    J: float
    	Magnitude of the total angular momentum.
    r: float
    	Binary separation.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    xi: float
    	Effective spin.
    """

    varphi = np.pi*np.ones(flen(S))
    xi = effectivepotential_Sphi(S,varphi,J,r,q,chi1,chi2)

    return xi


def effectivepotential_minus(S,J,r,q,chi1,chi2):
    """
    Lower effective potential.

    Call
    ----
    xi = effectivepotential_minus(S,J,r,q,chi1,chi2)

    Parameters
    ----------
    S: float
    	Magnitude of the total spin.
    J: float
    	Magnitude of the total angular momentum.
    r: float
    	Binary separation.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    xi: float
    	Effective spin.
    """

    varphi = np.zeros(flen(S))
    xi = effectivepotential_Sphi(S,varphi,J,r,q,chi1,chi2)

    return xi


# TODO: check the behavior of sign here. Array?
def eval_varphi(S, J, r, xi, q, chi1, chi2, sign=1):
    """
    Evaluate the nutation parameter varphi.

    Call
    ----
    varphi = eval_varphi(S,J,r,xi,q,chi1,chi2,sign = 1)

    Parameters
    ----------
    S: float
    	Magnitude of the total spin.
    J: float
    	Magnitude of the total angular momentum.
    r: float
    	Binary separation.
    xi: float
    	Effective spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.
    sign: integer, optional (default: 1)
    	Sign, either +1 or -1.

    Returns
    -------
    varphi: float
    	Generalized nutation coordinate (Eq 9 in arxiv:1506.03492).
    """

    L = angularmomentum(r, q)
    S1, S2 = spinmags(q, chi1, chi2)

    t1 = (1+q) / (4*q * S**2 * L)
    t2 = J**2 - L**2 - S**2
    t3 = S**2 * (1+q) - (S1**2 - S2**2) * (1-q)
    t4 = (1-q) * ((L+S)**2 - J**2)**0.5
    t5 = (J**2 - (L-S)**2)**0.5
    t6 = ((S1+S2)**2 - S**2)**0.5
    t7 = (S**2 - (S1-S2)**2)**0.5

    cosvarphi= ((t2*t3) - (xi/t1)) / (t4*t5*t6*t7)
    varphi = np.arccos(cosvarphi) * sign

    return varphi


def eval_costheta1(S,J,r,xi,q,chi1,chi2):
    """
    Cosine of the angle theta1 between the orbital angular momentum and the spin of the primary black hole.

    Call
    ----
    costheta1 = eval_costheta1(S,J,r,xi,q,chi1,chi2)

    Parameters
    ----------
    S: float
    	Magnitude of the total spin.
    J: float
    	Magnitude of the total angular momentum.
    r: float
    	Binary separation.
    xi: float
    	Effective spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    costheta1: float
    	Cosine of the angle between orbital angular momentum and primary spin.
    """

    S,J,q=toarray(S,J,q)
    S1,S2 = spinmags(q,chi1,chi2)
    L = angularmomentum(r,q)

    costheta1= ( ((J**2-L**2-S**2)/L) - (2.*q*xi)/(1.+q) )/(2.*(1.-q)*S1)

    return costheta1


def eval_theta1(S,J,r,xi,q,chi1,chi2):
    """
    Angle theta1 between the orbital angular momentum and the spin of the primary black hole.

    Call
    ----
    theta1 = eval_theta1(S,J,r,xi,q,chi1,chi2)

    Parameters
    ----------
    S: float
    	Magnitude of the total spin.
    J: float
    	Magnitude of the total angular momentum.
    r: float
    	Binary separation.
    xi: float
    	Effective spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    theta1: float
    	Angle between orbital angular momentum and primary spin.
    """

    costheta1=eval_costheta1(S,J,r,xi,q,chi1,chi2)
    theta1 = np.arccos(costheta1)

    return theta1


def eval_costheta2(S,J,r,xi,q,chi1,chi2):
    """
    Cosine of the angle theta2 between the orbital angular momentum and the spin of the secondary black hole.

    Call
    ----
    costheta2 = eval_costheta2(S,J,r,xi,q,chi1,chi2)

    Parameters
    ----------
    S: float
    	Magnitude of the total spin.
    J: float
    	Magnitude of the total angular momentum.
    r: float
    	Binary separation.
    xi: float
    	Effective spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    costheta2: float
    	Cosine of the angle between orbital angular momentum and secondary spin.
    """

    S,J,q=toarray(S,J,q)
    S1,S2 = spinmags(q,chi1,chi2)
    L = angularmomentum(r,q)

    costheta2= ( ((J**2-L**2-S**2)*(-q/L)) + (2*q*xi)/(1+q) )/(2*(1-q)*S2)

    return costheta2


def eval_theta2(S,J,r,xi,q,chi1,chi2):
    """
    Angle theta2 between the orbital angular momentum and the spin of the secondary black hole.

    Call
    ----
    theta2 = eval_theta2(S,J,r,xi,q,chi1,chi2)

    Parameters
    ----------
    S: float
    	Magnitude of the total spin.
    J: float
    	Magnitude of the total angular momentum.
    r: float
    	Binary separation.
    xi: float
    	Effective spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    theta2: float
    	Angle between orbital angular momentum and secondary spin.
    """

    costheta2=eval_costheta2(S,J,r,xi,q,chi1,chi2)
    theta2 = np.arccos(costheta2)

    return theta2


def eval_costheta12(S,q,chi1,chi2):
    """
    Cosine of the angle theta12 between the two spins.

    Call
    ----
    costheta12 = eval_costheta12(S,q,chi1,chi2)

    Parameters
    ----------
    S: float
    	Magnitude of the total spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    costheta12: float
    	Cosine of the angle between the two spins.
    """

    S=toarray(S)
    S1,S2 = spinmags(q,chi1,chi2)
    costheta12=(S**2-S1**2-S2**2)/(2*S1*S2)

    return costheta12


def eval_theta12(S,q,chi1,chi2):
    """
    Angle theta12 between the two spins.

    Call
    ----
    theta12 = eval_theta12(S,q,chi1,chi2)

    Parameters
    ----------
    S: float
    	Magnitude of the total spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    theta12: float
    	Angle between the two spins.
    """

    costheta12=eval_costheta12(S,q,chi1,chi2)
    theta12 = np.arccos(costheta12)

    return theta12


def eval_cosdeltaphi(S,J,r,xi,q,chi1,chi2):
    """
    Cosine of the angle deltaphi between the projections of the two spins onto the orbital plane.

    Call
    ----
    cosdeltaphi = eval_cosdeltaphi(S,J,r,xi,q,chi1,chi2)

    Parameters
    ----------
    S: float
    	Magnitude of the total spin.
    J: float
    	Magnitude of the total angular momentum.
    r: float
    	Binary separation.
    xi: float
    	Effective spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    cosdeltaphi: float
    	Cosine of the angle between the projections of the two spins onto the orbital plane.
    """

    q=toarray(q)
    S1,S2 = spinmags(q,chi1,chi2)
    costheta1=eval_costheta1(S,J,r,xi,q,chi1,chi2)
    costheta2=eval_costheta2(S,J,r,xi,q,chi1,chi2)
    costheta12=eval_costheta12(S,q,chi1,chi2)
    cosdeltaphi= (costheta12 - costheta1*costheta2)/((1-costheta1**2)*(1-costheta2**2))**0.5

    return cosdeltaphi

# TODO: check the behavior of sign. Array?
def eval_deltaphi(S,J,r,xi,q,chi1,chi2,sign=+1):
    """
    Angle deltaphi between the projections of the two spins onto the orbital plane. By default this is returned in [0,pi]. Setting sign=-1 returns the other half of the  precession cycle [-pi,0].

    Call
    ----
    deltaphi = eval_deltaphi(S,J,r,xi,q,chi1,chi2,sign = +1)

    Parameters
    ----------
    S: float
    	Magnitude of the total spin.
    J: float
    	Magnitude of the total angular momentum.
    r: float
    	Binary separation.
    xi: float
    	Effective spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.
    sign: integer, optional (default: +1)
    	Sign, either +1 or -1.

    Returns
    -------
    deltaphi: float
    	Angle between the projections of the two spins onto the orbital plane.
    """

    cosdeltaphi=eval_cosdeltaphi(S,J,r,xi,q,chi1,chi2)
    deltaphi = np.sign(sign)*np.arccos(cosdeltaphi)

    return deltaphi


def eval_costhetaL(S,J,r,q,chi1,chi2):
    """
    Cosine of the angle thetaL betwen orbital angular momentum and total angular momentum.

    Call
    ----
    costhetaL = eval_costhetaL(S,J,r,q,chi1,chi2)

    Parameters
    ----------
    S: float
    	Magnitude of the total spin.
    J: float
    	Magnitude of the total angular momentum.
    r: float
    	Binary separation.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    costhetaL: float
    	Cosine of the angle betwen orbital angular momentum and total angular momentum.
    """


    S,J=toarray(S,J)
    S1,S2 = spinmags(q,chi1,chi2)
    L = angularmomentum(r,q)
    costhetaL=(J**2+L**2-S**2)/(2*J*L)

    return costhetaL


def eval_thetaL(S,J,r,q,chi1,chi2):
    """
    Angle thetaL betwen orbital angular momentum and total angular momentum.

    Call
    ----
    thetaL = eval_thetaL(S,J,r,q,chi1,chi2)

    Parameters
    ----------
    S: float
    	Magnitude of the total spin.
    J: float
    	Magnitude of the total angular momentum.
    r: float
    	Binary separation.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    thetaL: float
    	Angle betwen orbital angular momentum and total angular momentum.
    """

    costhetaL=eval_costhetaL(S,J,r,q,chi1,chi2)
    thetaL=np.arccos(costhetaL)

    return thetaL

#TODO: there's confusion here with the effective potential, which is also and evaluation of xi
def eval_xi(theta1,theta2,q,chi1,chi2):
    """
    Effective spin from the spin angles.

    Call
    ----
    xi = eval_xi(theta1,theta2,q,chi1,chi2)

    Parameters
    ----------
    theta1: float
    	Angle between orbital angular momentum and primary spin.
    theta2: float
    	Angle between orbital angular momentum and secondary spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    xi: float
    	Effective spin.
    """

    theta1,theta2,q=toarray(theta1,theta2,q)
    S1,S2 = spinmags(q,chi1,chi2)
    xi=(1+q)*(q*S1*np.cos(theta1)+S2*np.cos(theta2))/q

    return xi


#TODO: Docstrings needs to be rewritten
def eval_J(theta1=None,theta2=None,deltaphi=None,kappa=None,r=None,q=None,chi1=None,chi2=None):
    """
    Magnitude of the total angular momentum from the spin angles.

    Parameters
    ----------
    theta1: float
        Angle between orbital angular momentum and primary spin.
    theta1: float
        Angle between orbital angular momentum and primary spin.
    deltaphi: float
        Angle between the projections of the two spins onto the orbital plane.
    r: float
        Binary separation.
    q: float
        Mass ratio: 0 <= q <= 1.
    chi1: float
        Dimensionless spin of the primary black hole: 0 <= chi1 <= 1.
    chi2: float
        Dimensionless spin of the secondary black hole: 0 <= chi1 <= 1.

    Returns
    -------
    J: float
        Magnitude of the total angular momentum.
    """


    if theta1 is not None and theta2 is not None and deltaphi is not None and kappa is None and r is not None and q is not None and chi1 is not None and chi2 is not None:

        theta1,theta2,deltaphi,q=toarray(theta1,theta2,deltaphi,q)
        S1,S2 = spinmags(q,chi1,chi2)
        L = angularmomentum(r,q)
        S=eval_S(theta1,theta2,deltaphi,q,chi1,chi2)
        J=(L**2+S**2+2*L*(S1*np.cos(theta1)+S2*np.cos(theta2)))**0.5

    elif theta1 is None and theta2 is None and deltaphi is None and kappa is not None and r is not None and q is not None and chi1 is None and chi2 is None:

        kappa = toarray(kappa)
        L = angularmomentum(r,q)
        J = ( 2*L*kappa + L**2 )**0.5

    else:
        raise TypeError



    return J


def eval_S(theta1,theta2,deltaphi,q,chi1,chi2):
    """
    Magnitude of the total spin from the spin angles.

    Call
    ----
    S = eval_S(theta1,theta2,deltaphi,q,chi1,chi2)

    Parameters
    ----------
    theta1: float
    	Angle between orbital angular momentum and primary spin.
    theta2: float
    	Angle between orbital angular momentum and secondary spin.
    deltaphi: float
    	Angle between the projections of the two spins onto the orbital plane.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    S: float
    	Magnitude of the total spin.
    """

    theta1,theta2,deltaphi=toarray(theta1,theta2,deltaphi)
    S1,S2 = spinmags(q,chi1,chi2)

    S=(S1**2+S2**2+2*S1*S2*(np.sin(theta1)*np.sin(theta2)*np.cos(deltaphi)+np.cos(theta1)*np.cos(theta2)))**0.5

    return S


def eval_kappa(J, r, q):
    """
    Change of dependent variable to regularize the infinite orbital separation
    limit of the precession-averaged evolution equation.

    Call
    ----
    kappa = eval_kappa(J,r,q)

    Parameters
    ----------
    J: float
    	Magnitude of the total angular momentum.
    r: float
    	Binary separation.
    q: float
    	Mass ratio: 0<=q<=1.

    Returns
    -------
    kappa: float
    	Regularized angular momentum (J^2-L^2)/(2L).
    """

    J = toarray(J)
    L = angularmomentum(r, q)
    kappa = (J**2 - L**2) / (2*L)

    return kappa


def eval_u(r, q):
    """
    Change of independent variable to regularize the infinite orbital separation
    limit of the precession-averaged evolution equation.

    Call
    ----
    u = eval_u(r,q)

    Parameters
    ----------
    r: float
    	Binary separation.
    q: float
    	Mass ratio: 0<=q<=1.

    Returns
    -------
    u: float
    	Compactified separation 1/(2L).
    """

    L = angularmomentum(r, q)
    u = 1 / (2*L)

    return u


# TODO: this needs to be merged with orbital separation
def eval_r(u, q):
    '''TODO docstrings'''

    u = toarray(u)
    r= (2*mass1(q)*mass2(q)*u)**(-2)

    return r


def eval_kappainf(theta1inf, theta2inf, q, chi1, chi2):
    """
    Infinite orbital-separation limit of the regularized momentum kappa.

    Call
    ----
    kappainf = eval_kappainf(theta1inf,theta2inf,q,chi1,chi2)

    Parameters
    ----------
    theta1inf: float
    	Asymptotic value of the angle between orbital angular momentum and primary spin.
    theta2inf: float
    	Asymptotic value of the angle between orbital angular momentum and secondary spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    kappainf: float
    	Asymptotic value of the regularized momentum kappa.
    """

    theta1inf, theta2inf = toarray(theta1inf, theta2inf)
    S1, S2 = spinmags(q, chi1, chi2)
    kappainf = S1*np.cos(theta1inf) + S2*np.cos(theta2inf)

    return kappainf


def eval_costheta1inf(kappainf, xi, q, chi1, chi2):
    """
    Infinite orbital separation limit of the cosine of the angle between the
    orbital angular momentum and the primary spin.

    Call
    ----
    costheta1inf = eval_costheta1inf(kappainf,xi,q,chi1,chi2)

    Parameters
    ----------
    kappainf: float
    	Asymptotic value of the regularized momentum kappa.
    xi: float
    	Effective spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    costheta1inf: float
    	Cosine of the asymptotic angle between orbital angular momentum and primary spin.
    """


    kappainf, xi, q = toarray(kappainf, xi, q)
    S1, S2 = spinmags(q, chi1, chi2)
    costheta1inf = (-xi + kappainf*(1+1/q)) / (S1*(1/q-q))

    return costheta1inf


def eval_theta1inf(kappainf, xi, q, chi1, chi2):
    """
    Infinite orbital separation limit of the angle between the orbital angular
    momentum and the primary spin.

    Call
    ----
    theta1inf = eval_theta1inf(kappainf,xi,q,chi1,chi2)

    Parameters
    ----------
    kappainf: float
    	Asymptotic value of the regularized momentum kappa.
    xi: float
    	Effective spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    theta1inf: float
    	Asymptotic value of the angle between orbital angular momentum and primary spin.
    """


    costheta1inf = eval_costheta1inf(kappainf, xi, q, chi1, chi2)
    theta1inf = np.arccos(costheta1inf)

    return theta1inf


def eval_costheta2inf(kappainf, xi, q, chi1, chi2):
    """
    Infinite orbital separation limit of the cosine of the angle between the
    orbital angular momentum and the secondary spin.

    Call
    ----
    theta1inf = eval_costheta2inf(kappainf,xi,q,chi1,chi2)

    Parameters
    ----------
    kappainf: float
    	Asymptotic value of the regularized momentum kappa.
    xi: float
    	Effective spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    theta1inf: float
    	Asymptotic value of the angle between orbital angular momentum and primary spin.
    """

    kappainf, xi, q = toarray(kappainf, xi, q)
    S1, S2 = spinmags(q, chi1, chi2)
    costheta2inf = (xi - kappainf*(1+q)) / (S2*(1/q-q))

    return costheta2inf


def eval_theta2inf(kappainf, xi, q, chi1, chi2):
    """
    Infinite orbital separation limit of the angle between the orbital angular
    momentum and the secondary spin.

    Call
    ----
    theta2inf = eval_theta2inf(kappainf,xi,q,chi1,chi2)

    Parameters
    ----------
    kappainf: float
    	Asymptotic value of the regularized momentum kappa.
    xi: float
    	Effective spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

    Returns
    -------
    theta2inf: float
    	Asymptotic value of the angle between orbital angular momentum and secondary spin.
    """

    costheta2inf = eval_costheta2inf(kappainf, xi, q, chi1, chi2)
    theta2inf = np.arccos(costheta2inf)

    return theta2inf

#TODO: check simpler flag and arrays
def morphology(J,r,xi,q,chi1,chi2,simpler=False):
    """
    Evaluate the spin morphology and return `L0` for librating about DeltaPhi=0, `Lpi` for librating about DeltaPhi=pi, `C-` for circulating from DeltaPhi=pi to DeltaPhi=0, and `C+` for circulating from DeltaPhi=0 to DeltaPhi=pi. If simpler=True, do not distinguish between the two circulating morphologies and return `C` for both.

    Call
    ----
    morph = morphology(J,r,xi,q,chi1,chi2,simpler = False)

    Parameters
    ----------
    J: float
    	Magnitude of the total angular momentum.
    r: float
    	Binary separation.
    xi: float
    	Effective spin.
    q: float
    	Mass ratio: 0<=q<=1.
    chi1: float
    	Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
    chi2: float
    	Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.
    simpler: boolean, optional (default: False)
    	If True simplifies output.

    Returns
    -------
    morph: string
    	Spin morphology.
    """

    Smin,Smax = Slimits_plusminus(J,r,xi,q,chi1,chi2)
    # Pairs of booleans based on the values of deltaphi at S- and S+
    status = np.array([eval_cosdeltaphi(Smin,J,r,xi,q,chi1,chi2) >0.5 ,eval_cosdeltaphi(Smax,J,r,xi,q,chi1,chi2) >0.5]).T

    # Map to labels
    if simpler:
        dictlabel = {(False,False):"Lpi", (True,True):"L0", (False, True):"C", (True, False):"C"}
    else:
        dictlabel = {(False,False):"Lpi", (True,True):"L0", (False, True):"C-", (True, False):"C+"}

    # Subsitute pairs with labels
    morphs = np.zeros(flen(J))
    for k, v in dictlabel.items():
        morphs=np.where((status == k).all(axis=1),v,morphs)

    return np.squeeze(morphs)

#  TODO: Jan 4. all docstrtings from here need to be checked



# TODO: check behavior of sign and arrays
def conserved_to_angles(S,J,r,xi,q,chi1,chi2,sign=+1):
    """
    Convert conserved quantities (S,J,xi) into angles (theta1,theta2,deltaphi).
    Setting sign=+1 (default) returns deltaphi in [0, pi], setting sign=-1 returns deltaphi in [-pi,0].

    Parameters
    ----------
    S: float
        Magnitude of the total spin.
    J: float
        Magnitude of the total angular momentum.
    r: float
        Binary separation.
    q: float
        Mass ratio: 0 <= q <= 1.
    xi: float
        Effective spin.
    chi1: float
        Dimensionless spin of the primary black hole: 0 <= chi1 <= 1.
    chi2: float
        Dimensionless spin of the secondary black hole: 0 <= chi1 <= 1.
    sign: optional (default: +1)
        If positive returns values in [0,pi], if negative returns values in [-pi,0].

    Returns
    -------
    theta1: float
        Angle between orbital angular momentum and primary spin.
    theta2: float
        Angle between orbital angular momentum and secondary spin.
    deltaphi: float
        Angle between the projections of the two spins onto the orbital plane.
    """

    theta1=eval_theta1(S,J,r,xi,q,chi1,chi2)
    theta2=eval_theta2(S,J,r,xi,q,chi1,chi2)
    deltaphi=eval_deltaphi(S,J,r,xi,q,chi1,chi2,sign=sign)

    return toarray(theta1,theta2,deltaphi)


def angles_to_conserved(theta1,theta2,deltaphi,r,q,chi1,chi2):
    """
    Convert angles (theta1,theta2,deltaphi) into conserved quantities (S,J,xi).

    Parameters
    ----------
    theta1: float
        Angle between orbital angular momentum and primary spin.
    theta1: float
        Angle between orbital angular momentum and primary spin.
    deltaphi: float
        Angle between the projections of the two spins onto the orbital plane.
    r: float
        Binary separation.
    q: float
        Mass ratio: 0 <= q <= 1.
    chi1: float
        Dimensionless spin of the primary black hole: 0 <= chi1 <= 1.
    chi2: float
        Dimensionless spin of the secondary black hole: 0 <= chi1 <= 1.

    Returns
    ----------
    S: float
        Magnitude of the total spin.
    J: float
        Magnitude of the total angular momentum.
    xi: float
        Effective spin.
    """

    S=eval_S(theta1,theta2,deltaphi,q,chi1,chi2)
    J=eval_J(theta1=theta1,theta2=theta2,deltaphi=deltaphi,r=r,q=q,chi1=chi1,chi2=chi2)
    xi=eval_xi(theta1,theta2,q,chi1,chi2)

    return toarray(S,J,xi)


def angles_to_asymptotic(theta1inf, theta2inf, q, chi1, chi2):
    """
    Convert asymptotic angles theta1 theta2 into effective spin and asymptotic kappa.

    Parameters
    ----------
    theta1inf: float
        Asymptotic angle between orbital angular momentum and primary spin.

    theta2inf: float
        Asymptotic angle between orbital angular momentum and primary spin.

    q: float
        Mass ratio: 0 <= q <= 1.

    chi1: float
        Dimensionless spin of the primary black hole: 0 <= chi1 <= 1.

    chi2: float
        Dimensionless spin of the secondary black hole: 0 <= chi1 <= 1.

    Returns
    ----------
    kappainf: float
        Asymptotic momentum (J^2-L^2)/(2L).

    xi: float
        Effective spin.
    """

    S1, S2 = spinmags(q, chi1, chi2)
    kappainf = eval_kappainf(theta1inf, theta2inf, q, chi1, chi2)
    xi = eval_xi(theta1inf, theta2inf, q, chi1, chi2)

    return toarray(kappainf, xi)


def asymptotic_to_angles(kappainf, xi, q, chi1, chi2):
    """
    Convert asymptotic kappa and xi into asymptotic angles theta1, theta2.

    Call
    ----
    theta1inf,theta2inf=asymptotic_to_angles(kappainf,xi,q,chi1,chi2)

	Parameters
	----------
	kappainf: float
		Asymptotic value of the regularized momentum kappa.
	xi: float
		Effective spin.
	q: float
		Mass ratio: 0<=q<=1.
	chi1: float
		Dimensionless spin of the primary (heavier) black hole: 0<=chi1<= 1.
	chi2: float
		Dimensionless spin of the secondary (lighter) black hole: 0<=chi2<=1.

	Returns
	-------
	theta1inf: float
		Asymptotic value of the angle between orbital angular momentum and primary spin.
	theta2inf: float
		Asymptotic value of the angle between orbital angular momentum and secondary spin.
    """

    theta1inf = eval_theta1inf(kappainf, xi, q, chi1, chi2)
    theta2inf = eval_theta2inf(kappainf, xi, q, chi1, chi2)

    return toarray(theta1inf, theta2inf)



#### Precessional timescale dynamics ####

def Speriod_prefactor(r,xi,q):
    """
    Numerical prefactor to the precession period.

    Parameters
    ----------
    r: float
        Binary separation.
    xi: float
        Effective spin.
    q: float
        Mass ratio: 0 <= q <= 1.

    Returns
    -------
    mathcalA: string
        Numerical prefactor to the precession period.
    """

    r,xi=toarray(r,xi)
    eta=symmetricmassratio(q)
    mathcalA = (3/2)*(1/(r**3*eta**0.5))*(1-(xi/r**0.5))

    return mathcalA


def dS2dtsquared(S,J,r,xi,q,chi1,chi2):
    """
    Squared first time derivative of the squared total spin, on the precession timescale.

    Parameters
    ----------
    S: float
        Magnitude of the total spin.

    J: float
        Magnitude of the total angular momentum.

    r: float
        Orbital separation.

    xi: float
        Effective spin

    q: float
        Mass ratio.

    chi1: float
        Dimensionless spin of the primary.

    chi2: float
        Dimensionless spin of the secondary.

    Returns
    -------
    float
        Squared time derivative of the squared total spin.
    """

    mathcalA = Speriod_prefactor(r,xi,q)
    Sminus2,Splus2,S32 = S2roots(J,r,xi,q,chi1,chi2)

    return - mathcalA**2 * (S**2-Splus2) * (S**2-Sminus2) * (S**2-S32)


def dS2dt(S,J,r,xi,q,chi1,chi2):
    """
    Time derivative of the squared total spin, on the precession timescale.

    Parameters
    ----------
    S: float
        Magnitude of the total spin.

    J: float
        Magnitude of the total angular momentum.

    r: float
        Orbital separation.

    xi: float
        Effective spin.

    q: float
        Mass ratio.

    chi1: float
        Dimensionless spin of the primary.

    chi2: float
        Dimensionless spin of the secondary.

    Returns
    -------
    float
        Time derivative of the squared total spin.
    """

    return dS2dtsquared(S,J,r,xi,q,chi1,chi2)**0.5


def dSdt(S,J,r,xi,q,chi1,chi2):
    """
    Time derivative of the total spin, on the precession timescale.

    Parameters
    ----------
    S: float
        Magnitude of the total spin.

    J: float
        Magnitude of the total angular momentum.

    r: float
        Orbital separation.

    xi: float
        Effective spin.

    q: float
        Mass ratio.

    chi1: float
        Dimensionless spin of the primary.

    chi2: float
        Dimensionless spin of the secondary.

    Returns
    -------
    float
        Time derivative of the total spin.
    """

    return dS2dt(S,J,r,xi,q,chi1,chi2) / (2*S)


def elliptic_parameter(Sminus2,Splus2,S32):
    """
    Parameter m entering elliptic functiosn for the evolution of S.

    Parameters
    ----------
    Sminus2, Splus2, S32: floats
        Roots of d(S^2)/dt=0 with S32<=Sminus2<=Splus2.

    Returns
    -------
    m: string
        Parameter of the ellptic functions.
    """

    m = (Splus2-Sminus2)/(Splus2-S32)

    return m


def Speriod(J,r,xi,q,chi1,chi2):
    """
    Period of S as it oscillates from S- to S+ and back to S-.

    Parameters
    ----------
    J: float
        Magnitude of the total angular momentum.
    r: float
        Binary separation.
    xi: float
        Effective spin.
    q: float
        Mass ratio: 0 <= q <= 1.
    chi1: float
        Dimensionless spin of the primary black hole: 0 <= chi1 <= 1.
    chi2: float
        Dimensionless spin of the secondary black hole: 0 <= chi1 <= 1.

    Returns
    -------
    tau: string
        Nutation period.
    """

    mathcalA=Speriod_prefactor(r,xi,q)
    Sminus2,Splus2,S32 = S2roots(J,r,xi,q,chi1,chi2)
    m = elliptic_parameter(Sminus2,Splus2,S32)
    tau = 4*scipy.special.ellipk(m) / (mathcalA* (Splus2-S32)**0.5)

    return tau


def Soft(t,J,r,xi,q,chi1,chi2):
    """
    Evolution of S on the precessional timescale (without radiation reaction).

    Parameters
    ----------
    t: float, array
        Time
    J: float
        Magnitude of the total angular momentum.
    r: float
        Binary separation.
    xi: float
        Effective spin.
    q: float
        Mass ratio: 0 <= q <= 1.
    chi1: float
        Dimensionless spin of the primary black hole: 0 <= chi1 <= 1.
    chi2: float
        Dimensionless spin of the secondary black hole: 0 <= chi1 <= 1.

    Returns
    -------
    S: float
        Magnitude of the total spin.
    """

    t=toarray(t)
    mathcalA=Speriod_prefactor(r,xi,q)
    Sminus2,Splus2,S32 = S2roots(J,r,xi,q,chi1,chi2)
    m = elliptic_parameter(Sminus2,Splus2,S32)
    sn,cn,dn,pn = scipy.special.ellipj(t.T*mathcalA*(Splus2-S32)**0.5/2,m)
    S2 = Sminus2 + (Splus2-Sminus2)*((Sminus2-S32)/(Splus2-S32)) *(sn/dn)**2
    S=S2.T**0.5

    return S


def Ssampling(J,r,xi,q,chi1,chi2,N=1):
    #TODO write docstrings
    # N is number of samples

    tau = Speriod(J,r,xi,q,chi1,chi2)
    t = np.array([np.random.uniform(0,x,y) for x,y in zip(np.atleast_1d(tau),np.atleast_1d(N))])
    S = Soft(t,J,r,xi,q,chi1,chi2)

    return S


def S2av_mfactor(m):
    """
    Factor depending on the elliptic parameter in the precession averaged squared total spin.

    Parameters
    ----------
    m: float
        Elliptic parameter.

    Returns
    -------
    mfactor: float
        Value of the factor for the given m, (1 - E(m)/K(m)) / m.
    """

    m=toarray(m)

    with warnings.catch_warnings(): #Filter out warning for m=0
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        mfactor = (1- scipy.special.ellipe(m)/scipy.special.ellipk(m))/m

    # If m=0 return the limit 1/2
    return np.where(m==0, 1/2, mfactor)


def S2av(J, r, xi, q, chi1, chi2):
    """
    Analytic precession averaged expression for the squared total spin.

    Parameters
    ----------
    J: float
        Magnitude of the total angular momentum.
    r: float
        Binary separation.
    xi: float
        Effective spin.
    q: float
        Mass ratio: 0 <= q <= 1.
    chi1: float
        Dimensionless spin of the primary black hole: 0 <= chi1 <= 1.
    chi2: float
        Dimensionless spin of the secondary black hole: 0 <= chi1 <= 1.

    Returns
    -------
    """

    Sminus2, Splus2, S32 = S2roots(J, r, xi, q, chi1, chi2)
    m = elliptic_parameter(Sminus2, Splus2, S32)
    S2 = Splus2 - (Splus2-Sminus2)*S2av_mfactor(m)

    return S2


def S2rootsinf(theta1inf, theta2inf, q, chi1, chi2):
    """
    Infinite orbital separation limit of the roots of the cubic equation in S^2.

    Parameters
    ----------
    theta1inf: float
        Asymptotic value of the angle between the orbital angular momentum and
        the primary spin.

    theta2inf: float
        Asymptotic value of the angle between the orbital angular momentum and
        the secondary spin.

    q: float
        Mass ratio: 0 <= q <= 1.

    chi1: float
        Dimensionless spin of the primary black hole: 0 <= chi1 <= 1.

    chi2: float
        Dimensionless spin of the secondary black hole: 0 <= chi1 <= 1.

    Returns
    -------
    Sminus2inf: float
        Asymptotic value of the root Sminus2.

    Splus2inf: float
        Asymptotic value of the root Splus2.

    S32inf: float
        Asymptotic value of the root S32, -inf.
    """

    S1, S2 = spinmags(q, chi1, chi2)
    costheta1inf = np.cos(theta1inf)
    costheta2inf = np.cos(theta2inf)
    sintheta1inf = np.sin(theta1inf)
    sintheta2inf = np.sin(theta2inf)
    Sminus2inf = S1**2 + S2**2 + 2*S1*S2*(costheta1inf*costheta2inf - sintheta1inf*sintheta2inf)
    Splus2inf = S1**2 + S2**2 + 2*S1*S2*(costheta1inf*costheta2inf + sintheta1inf*sintheta2inf)
    S32inf = -np.inf

    return toarray(Sminus2inf, Splus2inf, S32inf)


def S2avinf(theta1inf, theta2inf, q, chi1, chi2):
    """
    Infinite orbital separation limit of the precession averaged values of S^2
    from the asymptotic angles theta1, theta2.

    Parameters
    ----------
    theta1inf: float
        Asymptotic value of the angle between the orbital angular momentum and
        the primary spin.

    theta2inf: float
        Asymptotic value of the angle between the orbital angular momentum and
        the secondary spin.

    q: float
        Mass ratio: 0 <= q <= 1.

    chi1: float
        Dimensionless spin of the primary black hole: 0 <= chi1 <= 1.

    chi2: float
        Dimensionless spin of the secondary black hole: 0 <= chi1 <= 1.

    Returns
    -------
    S2avinf: flaot
        Asymptotic value of S2av.
    """

    theta1inf, theta2inf = toarray(theta1inf, theta2inf)
    S1, S2 = spinmags(q, chi1, chi2)
    S2avinf = S1**2 + S2**2 + 2*S1*S2*np.cos(theta1inf)*np.cos(theta2inf)

    return S2avinf


#### Precession-averaged evolution ####

def dkappadu(kappa, u, xi, q, chi1, chi2):
    # TODO: fix docstrings
    # TODO: this function does not work with numpy arrays, but it doesn't have to, I think, because it's the RHS of quad; user should never call this directly

    """
    Analytic precession averaged expression for the squared total spin.

    Parameters
    ----------
    J: float
        Magnitude of the total angular momentum.
    r: float
        Binary separation.
    xi: float
        Effective spin.
    q: float
        Mass ratio: 0 <= q <= 1.
    chi1: float
        Dimensionless spin of the primary black hole: 0 <= chi1 <= 1.
    chi2: float
        Dimensionless spin of the secondary black hole: 0 <= chi1 <= 1.

    Returns
    -------
    """

    if u==0:
        # In this case use analytic result
        theta1inf,theta2inf = asymptotic_to_angles(kappa,xi,q,chi1,chi2)
        S2av = S2avinf(theta1inf, theta2inf, q, chi1, chi2)
    else:

        # This is equivalent to S2av, but we avoid multiple conversions J <--> kappa.
        S32, Sminus2, Splus2 = wraproots(Scubic_coefficients,kappa,u,xi,q,chi1,chi2)
        m = elliptic_parameter(Sminus2, Splus2, S32)
        S2av = Splus2 - (Splus2-Sminus2)*S2av_mfactor(m)

    return S2av


def kappaofu(kappa0, u, xi, q, chi1, chi2):
    """
    TODO: write docstrings. This is the actual precession-averaged integrator
    """

    def _compute(kappa0, u, xi, q, chi1, chi2):

        # h0 controls the first stepsize attempted. If integrating from finite separation, let the solver decide (h0=0). If integrating from infinity, prevent it from being too small.
        # TODO. This breaks down if r is very large but not infinite.
        h0= 1e-3 if u[0]==0 else 0

        #kappa = scipy.integrate.odeint(dkappadu, kappa0, u, args=(xi,q,chi1,chi2), h0=h0, full_output = 1)
        kappa = scipy.integrate.odeint(dkappadu, kappa0, u, args=(xi,q,chi1,chi2), h0=h0)

        return toarray(kappa)

    if flen(kappa0)==1:
        kappa = _compute(kappa0, u, xi, q, chi1, chi2)
    else:
        kappa = np.array(list(map(lambda x: _compute(*x), zip(kappa0, u, xi, q, chi1, chi2))))

    return kappa



def inspiral_precav(theta1=None,theta2=None,deltaphi=None,S=None,J=None,kappa=None,r=None,u=None,xi=None,q=None,chi1=None,chi2=None,outputs=None):
    '''
    TODO: docstrings. Precession average evolution; this is the function the user should call (I think)
    '''

    def _compute(theta1,theta2,deltaphi,S,J,kappa,r,u,xi,q,chi1,chi2):

        if q is None:
            raise TypeError("Please provide q.")
        if chi1 is None:
            raise TypeError("Please provide chi1.")
        if chi2 is None:
            raise TypeError("Please provide chi2.")

        if r is not None and u is None:
            r=toarray(r)
            u = eval_u(r, np.repeat(q,flen(r)) )
        elif r is None and u is not None:
            u=toarray(u)
            r = eval_r(u, np.repeat(q,flen(u)) )
        else:
            raise TypeError("Please provide either r or u. Use np.inf for infinity.")

        assert np.sum(u==0)<=1 and np.sum(u[1:-1]==0)==0, "There can only be one r=np.inf location, either at the beginning or at the end."


        # Start from r=infinity
        if u[0]==0:

            if theta1 is not None and theta2 is not None and S is None and J is None and kappa is None and xi is None:
                kappa, xi = angles_to_asymptotic(theta1,theta2,q,chi1,chi2)
                theta1inf, theta2inf = theta1, theta2

            elif theta1 is None and theta2 is None and deltaphi is None and J is None and kappa is not None and xi is not None:
                theta1inf,theta2inf = asymptotic_to_angles(kappa,xi,q,chi1,chi2)

            else:
                raise TypeError("Integrating from infinite separation. Please provide either (theta1,theta2) or (kappa,xi).")


        # Start from finite separations
        else:

            # User provides theta1,theta2, and deltaphi.
            if theta1 is not None and theta2 is not None and deltaphi is not None and S is None and J is None and kappa is None and xi is None:
                S, J, xi = angles_to_conserved(theta1, theta2, deltaphi, r[0], q, chi1, chi2)
                kappa = eval_kappa(J, r[0], q)

            # User provides J, xi, and maybe S.
            elif theta1 is None and theta2 is None and deltaphi is None and J is not None and kappa is None and xi is not None:
                kappa = eval_kappa(J, r[0], q)

            # User provides kappa, xi, and maybe S.
            elif theta1 is None and theta2 is None and deltaphi is None and J is None and kappa is not None and xi is not None:
                pass

            else:
                TypeError("Integrating from finite separations. Please provide one and not more of the following: (theta1,theta2,deltaphi), (J,xi), (S,J,xi), (kappa,xi), (S,kappa,xi).")

        # Integration
        kappa = kappaofu(kappa, u, xi, q, chi1, chi2)

        # Select finite separations
        rok = r[u!=0]
        kappaok = kappa[u!=0]

        # Resample S and assign random sign to deltaphi
        J = eval_J(kappa=kappaok,r=rok,q=np.repeat(q,flen(rok)))
        S = Ssampling(J, rok, np.repeat(xi,flen(rok)), np.repeat(q,flen(rok)),
        np.repeat(chi1,flen(rok)), np.repeat(chi2,flen(rok)), N=1)
        theta1,theta2,deltaphi = conserved_to_angles(S, J, rok, xi, np.repeat(q,flen(rok)), np.repeat(chi1,flen(rok)), np.repeat(chi2,flen(rok)))
        deltaphi = deltaphi * np.random.choice([-1,1],flen(deltaphi))

        # Integrating from infinite separation.
        if u[0]==0:
            J = np.concatenate(([np.inf],J))
            S = np.concatenate(([np.nan],S))
            theta1 = np.concatenate(([theta1inf],theta1))
            theta2 = np.concatenate(([theta2inf],theta2))
            deltaphi = np.concatenate(([np.nan],deltaphi))
        # Integrating backwards to infinity
        elif u[-1]==0:
            J = np.concatenate((J,[np.inf]))
            S = np.concatenate((S,[np.nan]))
            theta1inf,theta2inf = asymptotic_to_angles(kappa[-1],xi,q,chi1,chi2)
            theta1 = np.concatenate((theta1,[theta1inf]))
            theta2 = np.concatenate((theta2,[theta2inf]))
            deltaphi = np.concatenate((deltaphi,[np.nan]))
        else:
            pass

        return toarray(theta1,theta2,deltaphi,S,J,kappa,r,u,xi,q,chi1,chi2)

    #This array has to match the outputs of _compute (in the right order!)
    alloutputs = np.array(['theta1','theta2','deltaphi','S','J','kappa','r','u','xi','q','chi1','chi2'])

    # allresults is an array of dtype=object because different variables have different shapes
    if flen(q)==1:
        allresults =_compute(theta1,theta2,deltaphi,S,J,kappa,r,u,xi,q,chi1,chi2)
    else:
        inputs = np.array([theta1,theta2,deltaphi,S,J,kappa,r,u,xi,q,chi1,chi2])
        for k,v in enumerate(inputs):
            if v==None:
                inputs[k] = itertools.repeat(None) #TODO: this could be np.repeat(None,flen(q)) if you need to get rid of the itertools dependence

        theta1,theta2,deltaphi,S,J,kappa,r,u,xi,q,chi1,chi2= inputs
        allresults = np.array(list(map(_compute, theta1,theta2,deltaphi,S,J,kappa,r,u,xi,q,chi1,chi2))).T

    # Handle the outputs.
    # Return all
    if outputs is None:
        outputs = alloutputs
    # Return only those requested (in1d return boolean array)
    wantoutputs = np.in1d(alloutputs,outputs)

    # Store into a dictionary
    outcome={}
    for k,v in zip(alloutputs[wantoutputs],allresults[wantoutputs]):
        # np.stack fixed shapes and object types
        outcome[k]=np.stack(np.atleast_1d(v))

    return outcome




#TODO: does this work on arrays?
def precession_average(J, r, xi, q, chi1, chi2, func, *args, **kwargs):
    """
    Average a function over a precession cycle.

    Parameters
    ----------
    J: float
        Magnitude of the total angular momentum.

    r: float
        Binary separation.

    xi: float
        Effective spin.

    q: float
        Mass ratio: 0 <= q <= 1.

    chi1: float
        Dimensionless spin of the primary black hole: 0 <= chi1 <= 1.

    chi2: float
        Dimensionless spin of the secondary black hole: 0 <= chi1 <= 1.

    func: function
        Function to precession-average, with call func(S**2, *args, **kwargs).

    *args: tuple
        Extra arguments to pass to func.

    **kwargs: tuple
        Extra keyword arguments to pass to func.

    Returns
    -------
    func_av: float
        Precession averaged value of func.
    """

    Sminus2, Splus2, S32 = S2roots(J, r, xi, q, chi1, chi2)
    a = Speriod_prefactor(r, xi ,q)

    def _integrand(S2):
        return func(S2, *args, **kwargs) / np.abs(dS2dt(S2, Sminus2, Splus2, S32, a))

    tau = Speriod(J, r, xi, q, chi1, chi2)
    func_av = (2/tau) * scipy.integrate.quad(_integrand, Sminus2, Splus2)[0]

    return func_av


def vectors_to_conserved(Lvec, S1vec, S2vec, q):
    """
    """

    S1vec, S2vec, Lvec = toarray(S1vec, S2vec, Lvec)
    S = np.linalg.norm(S1vec+S2vec, axis=-1)
    J = np.linalg.norm(S1vec+S2vec+Lvec, axis=-1)
    L = np.linalg.norm(Lvec, axis=-1)
    m1, m2 = masses(q)
    xi = dot_nested(S1vec,Lvec)/(m1*L) + dot_nested(S2vec,Lvec)/(m2*L)

    return toarray(S, J, xi)

# TODO: write function to get theta12 from theta1,theta2 and deltaphi

def vectors_to_angles(Lvec, S1vec, S2vec):
    """
    The sign comes from Eq 2d in the multitimescale paper
    """

    S1vec, S2vec, Lvec = toarray(S1vec, S2vec, Lvec)
    S1vec = normalize_nested(S1vec)
    S2vec = normalize_nested(S2vec)
    Lvec = normalize_nested(Lvec)
    theta1 = np.arccos(dot_nested(S1vec,Lvec))
    theta2 = np.arccos(dot_nested(S2vec,Lvec))
    absdeltaphi = np.arccos(dot_nested(normalize_nested(np.cross(S1vec, Lvec)), normalize_nested(np.cross(S2vec, Lvec))))
    signdeltaphi = np.sign(dot_nested(Lvec,np.cross(np.cross(S2vec, Lvec),np.cross(S1vec, Lvec))))
    deltaphi = absdeltaphi*signdeltaphi

    return toarray(theta1, theta2, deltaphi)


def conserved_to_Jframe(S, J, r, xi, q, chi1, chi2):
    """
    Convert the conserved quantities to angular momentum vectors in the frame
    aligned with the total angular momentum.
    TODO: check multitimescale paper for definition of x and y axis

    Parameters
    ----------
    S: float
        Magnitude of the total spin.

    J: float
        Magnitude of the total angular momentum.

    r: float
        Binary separation.

    q: float
        Mass ratio: 0 <= q <= 1.

    xi: float
        Effective spin.

    chi1: float
        Dimensionless spin of the primary black hole: 0 <= chi1 <= 1.

    chi2: float
        Dimensionless spin of the secondary black hole: 0 <= chi1 <= 1.

    Returns
    -------

    """

    S, J, q = toarray(S, J, q)
    L = angularmomentum(r, q)
    S1, S2 = spinmags(q, chi1, chi2)
    varphi = eval_varphi(S, J, r, xi, q, chi1, chi2)
    thetaL = eval_thetaL(S, J, r, q, chi1, chi2)

    # Jx = toarray(np.zeros(flen(J)))
    # Jy = toarray(np.zeros(flen(J)))
    # Jz = J
    # Jvec = np.array([Jx, Jy, Jz]).T
    # Svec = Jvec - Lvec

    Lx = L * np.sin(thetaL)
    Ly = toarray(np.zeros(flen(L)))
    Lz = L * np.cos(thetaL)
    Lvec = np.array([Lx, Ly, Lz]).T

    A1 = (J**2 - (L-S)**2)**0.5
    A2 = ((L+S)**2 - J**2)**0.5
    A3 = (S**2 - (S1-S2)**2)**0.5
    A4 = ((S1+S2)**2 - S**2)**0.5

    S1x = (-(S**2+S1**2-S2**2)*A1*A2 + (J**2-L**2+S**2)*A3*A4*np.cos(varphi)) / (4*J*S**2)
    S1y = A3 * A4 * np.sin(varphi) / (2*S)
    S1z = ((S**2+S1**2-S2**2)*(J**2-L**2+S**2) + A1*A2*A3*A4*np.cos(varphi)) / (4*J*S**2)
    S1vec = np.array([S1x, S1y, S1z]).T

    S2x = -((S**2+S2**2-S1**2)*A1*A2 + (J**2-L**2+S**2)*A3*A4*np.cos(varphi)) / (4*J*S**2)
    S2y = -A3*A4*np.sin(varphi) / (2*S)
    S2z = ((S**2+S2**2-S1**2)*(J**2-L**2+S**2) - A1*A2*A3*A4*np.cos(varphi)) / (4*J*S**2)
    S2vec = np.array([S2x, S2y, S2z]).T

    return toarray(Lvec, S1vec, S2vec)

def angles_to_Jframe(theta1, theta2, deltaphi, r, q, chi1, chi2):
    """
    TODO: write docstrings
    """

    S, J, xi = angles_to_conserved(theta1, theta2, deltaphi, r, q, chi1, chi2)
    Lvec, S1vec, S2vec = conserved_to_Jframe(S, J, r, xi, q, chi1, chi2)
    return toarray(Lvec, S1vec, S2vec)


def angles_to_Lframe(theta1, theta2, deltaphi, r, q, chi1, chi2):
    """
    TODO: write docstrings
    """

    L = angularmomentum(r, q)
    S1, S2 = spinmags(q, chi1, chi2)

    Lx = toarray(np.zeros(flen(L)))
    Ly = toarray(np.zeros(flen(L)))
    Lz = L
    Lvec = np.array([Lx, Ly, Lz]).T

    S1x = S1 * np.sin(theta1)
    S1y = toarray(np.zeros(flen(S1)))
    S1z = S1 * np.cos(theta1)
    S1vec = np.array([S1x, S1y, S1z]).T

    S2x = S2 * np.sin(theta2) * np.cos(deltaphi)
    S2y = S2 * np.sin(theta2) * np.sin(deltaphi)
    S2z = S2 * np.cos(theta2)
    S2vec = np.array([S2x, S2y, S2z]).T

    # Svec = S1vec + S2vec
    # Jvec = Lvec + Svec
    return toarray(Lvec, S1vec, S2vec)


def conserved_to_Lframe(S, J, r, xi, q, chi1, chi2):
    """
    TODO: write docstrings
    """

    theta1, theta2, deltaphi = conserved_to_angles(S, J, r, xi, q, chi1, chi2)
    Lvec, S1vec, S2vec = angles_to_Lframe(theta1, theta2, deltaphi, r, q, chi1, chi2)
    return toarray(Lvec, S1vec, S2vec)


def r_updown(q, chi1, chi2):
    """
    The critical separations r_ud+/- marking the region of the up-down precessional instability.

    Parameters
    ----------
    q: float
        Mass ratio m2/m1, 0 <= q <= 1.

    chi1:
        Dimensionless spin of the primary black hole, 0 <= chi1 <= 1.

    chi2:
        Dimensionless spin of the secondary black hole, 0 <= chi2 <= 1.

    Returns
    -------
    r_udp: float
        Outer critical separation marking the instability onset.

    r_udm: float
        Inner critical separation marking the end of the unstable region.

    """

    q, chi1, chi2 = toarray(q, chi1, chi2)
    r_plus = (chi1**.5+(q*chi2)**.5)**4./(1.-q)**2.
    r_minus = (chi1**.5-(q*chi2)**.5)**4./(1.-q)**2.

    return toarray(r_plus, r_minus)


def omega2_aligned(r, q, chi1, chi2, which):
    """
    TODO: fix docstrings, new which paramters, alphas removed
    Squared oscillation frequency of a given perturbed aligned-spin binary.

    Parameters
    ----------
    r: float
        Orbital separation.

    q: float
        Mass ratio m2/m1, 0 <= q <= 1.

    chi1: float
        Dimensionless spin of the primary black hole, 0 <= chi1 <= 1.

    chi2: float
        Dimensionless spin of the secondary black hole, 0 <= chi2 <= 1.

    alpha1: int
        Alignment of the primary black hole, +1 for up or -1 for down.

    alpha2: int
        Alignment of the secondary black hole, +1 for up or -1 for down.

    Returns
    -------
    omega2: float
        Squared oscillation frequency of the given aligned binary.
    """

    # These are all the valid input flags
    uulabels=np.array(['uu','up-up','upup','++'])
    udlabels=np.array(['ud','up-down','updown','+-'])
    dulabels=np.array(['du','down-up','downup','-+'])
    ddlabels=np.array(['dd','down-down','downdown','--'])

    assert np.isin(which,np.concatenate([uulabels,udlabels,dulabels,ddlabels])).all(), "Set `which` flag to either uu, ud, du, or dd."

    #+1 if primary is co-aligned, -1 if primary is counter-aligned
    alpha1 = np.where(np.isin(which,np.concatenate([uulabels,udlabels])), 1,-1)
    #+1 if secondary is co-aligned, -1 if secondary is counter-aligned
    alpha2 = np.where(np.isin(which,np.concatenate([uulabels,dulabels])), 1,-1)

    q = toarray(q)
    L = angularmomentum(r, q)
    S1, S2 = spinmags(q, chi1, chi2)
    # Slightly rewritten from Eq. 18 in arXiv:2003.02281, regularized for q=1
    a = (3*q**5/(2*(1+q)**11*L**7))**2
    b = L**2*(1-q)**2 - 2*L*(q*alpha1*S1-alpha2*S2)*(1-q) + (q*alpha1*S1+alpha2*S2)**2
    c = (L - (q*alpha1*S1+alpha2*S2)/(1+q))**2
    omega2 = a*b*c

    return omega2


# TODO: nutation
def r_wide(q, chi1, chi2):
    """
    The critical separation r_wide below which the binary component with
    smaller dimensionless spin may undergo wide nutations.

    Parameters
    ----------
    q: float
        Mass ratio m2/m1, 0 <= q <= 1.

    chi1:
        Dimensionless spin of the primary black hole, 0 <= chi1 <= 1.

    chi2:
        Dimensionless spin of the secondary black hole, 0 <= chi2 <= 1.

    Returns
    -------
    r_wide: float
        Critical orbital separation for wide nutation.
        If chi1 < chi2 (chi1 > chi2) the primary (secondary) spin may undergo
        wide nutations.

    """

    q, chi1, chi2 = toarray(q, chi1, chi2)
    r_wide = ((q*chi2 - chi1) / (1-q))**2

    return r_wide


#### Orbit averaged things ####

# TODO: this comes straight from precession_V1. Update docstrings. It's not necesssary that this function works on arrays
# TODO: replace quadrupole_formula flag with parameter to select a given PN order
def orbav_eqs(allvars,v,q,m1,m2,eta,chi1,chi2,S1,S2,tracktime=False,quadrupole_formula=False):

    '''
    Right-hand side of the orbit-averaged PN equations: d[allvars]/dv=RHS, where
    allvars is an array with the cartesian components of the unit vectors L, S1
    and S2. This function is only the actual system of equations, not the ODE
    solver.

    Equations are the ones reported in Gerosa et al. [Phys.Rev. D87 (2013) 10,
    104028](http://journals.aps.org/prd/abstract/10.1103/PhysRevD.87.104028);
    see references therein. In particular, the quadrupole-monopole term computed
    by Racine is included. The results presented in Gerosa et al. 2013 actually
    use additional unpublished terms, that are not listed in the published
    equations and are NOT included here. Radiation reaction is included up to
    3.5PN.

    The internal quadrupole_formula flag switches off all PN corrections in
    radiation reaction.

    The integration is carried over in the orbital velocity v (equivalent to the
    separation), not in time. If an expression for v(t) is needed, the code can
    be easiliy modified to return time as well.

    **Call:**

        allders=precession.orbav_eqs(allvars,v,q,S1,S2,eta,m1,m2,chi1,chi2,time=False)

    **Parameters:**
    - `allvars`: array of lenght 9 cointaining the initial condition for numerical integration for the components of the unit vectors L, S1 and S2.
    - `v`: orbital velocity.
    - `q`: binary mass ratio. Must be q<=1.
    - `S1`: spin magnitude of the primary BH.
    - `S2`: spin magnitude of the secondary BH.
    - `eta`: symmetric mass ratio.
    - `m1`: mass of the primary BH.
    - `m2`: mass of the secondary BH.
    - `chi1`: dimensionless spin magnitude of the primary BH. Must be 0<=chi1<=1
    - `chi2`: dimensionless spin magnitude of the secondary BH. Must be 0<=chi2<=1
    - `time`: if `True` also integrate t(r).

    **Returns:**

    - `allders`: array of lenght 9 cointaining the derivatives of allvars with respect to the orbital velocity v.
    '''

    # Unpack inputs
    Lh = np.array(allvars[0:3])
    S1h = np.array(allvars[3:6])
    S2h = np.array(allvars[6:9])
    if tracktime:
        t = allvars[9]

    # Angles
    ct1 = np.dot(S1h,Lh)
    ct2 = np.dot(S2h,Lh)
    ct12 = np.dot(S1h,S2h)

    # Spin precession for S1
    Omega1= eta*v**5*(2+3*q/2)*Lh  \
            + v**6*(S2*S2h-3*S2*ct2*Lh-3*q*S1*ct1*Lh)/2
    dS1hdt = np.cross(Omega1,S1h)

    # Spin precession for S2
    Omega2= eta*v**5*(2+3/(2*q))*Lh  \
            + v**6*(S1*S1h-3*S1*ct1*Lh-3*S2*ct2*Lh/q)/2
    dS2hdt = np.cross(Omega2,S2h)

    # Conservation of angular momentum
    dLhdt= -v*(S1*dS1hdt+S2*dS2hdt)/eta

    # Radiation reaction
    if quadrupole_formula: # Use to switch off higher-order terms
        dvdt= (32*eta*v**9/5)
    else:
        dvdt= (32*eta*v**9/5)* ( 1                                  \
            - v**2* (743+924*eta)/336                               \
            + v**3* (4*np.pi                                        \
                     - chi1*ct1*(113*m1**2/12 + 25*eta/4 )   \
                     - chi2*ct2*(113*m2**2/12 + 25*eta/4 ))  \
            + v**4* (34103/18144 + 13661*eta/2016 + 59*eta**2/18    \
                     + eta*chi1*chi2* (721*ct1*ct2 - 247*ct12) /48  \
                     + ((m1*chi1)**2 * (719*ct1**2-233))/96       \
                     + ((m2*chi2)**2 * (719*ct2**2-233))/96)      \
            - v**5* np.pi*(4159+15876*eta)/672                      \
            + v**6* (16447322263/139708800 + 16*np.pi**2/3          \
                     -1712*(0.5772156649+np.log(4*v))/105           \
                     +(451*np.pi**2/48 - 56198689/217728)*eta       \
                     +541*eta**2/896 - 5605*eta**3/2592)            \
            + v**7* np.pi*( -4415/4032 + 358675*eta/6048            \
                     + 91495*eta**2/1512)                           \
            )

    # Integrate in v, not in time
    dtdv=1./dvdt
    dLhdv=dLhdt*dtdv
    dS1hdv=dS1hdt*dtdv
    dS2hdv=dS2hdt*dtdv

    # Pack outputs
    if tracktime:
        return np.concatenate([dLhdv,dS1hdv,dS2hdv,[dtdv]])
    else:
        return np.concatenate([dLhdv,dS1hdv,dS2hdv])

# TODO: this comes straight from precession_V1. Update docstrings
def orbav_integrator(Lh0,S1h0,S2h0,r,q,chi1,chi2,tracktime=False,quadrupole_formula=False):

    '''
    Single orbit-averaged integration. Integrate the system of ODEs specified in
    `precession.orbav_eqs`. The initial configuration (at r_vals[0]) is
    specified through J, xi and S. The components of the unit vectors L, S1 and
    S2 are returned at the output separations specified by r_vals. The initial
    values of J and S must be compatible with the initial separation r_vals[0],
    otherwise an error is raised. Integration is performed in a reference frame
    in which the z axis is along J and L lies in the x-z plane at the initial
    separation. Equations are integrated in v (orbital velocity) but outputs are
    converted to r (separation).

    Of course, this can only integrate to/from FINITE separations.

    Bear in mind that orbit-averaged integrations are tpically possible from
    r<10000; integrations from larger separations take a very long time and can
    occasionally crash. If q=1, the initial binary configuration is specified
    through cos(varphi), not S.

    We recommend to use one of the wrappers `precession.orbit_averaged` and
    `precession.orbit_angles` provided.

    **Call:**
        Lhx_fvals,Lhy_fvals,Lhz_fvals,S1hx_fvals,S1hy_fvals,S1hz_fvals,S2hx_fvals,S2hy_fvals,S2hz_fvals=precession.orbav_integrator(J,xi,S,r_vals,q,S1,S2,time=False)

    **Parameters:**

    - `J`: magnitude of the total angular momentum.
    - `xi`: projection of the effective spin along the orbital angular momentum.
    - `S`: magnitude of the total spin.
    - `r_vals`: binary separation (array).
    - `q`: binary mass ratio. Must be q<=1.
    - `S1`: spin magnitude of the primary BH.
    - `S2`: spin magnitude of the secondary BH.
    - `time`: if `True` also integrate t(r).

    **Returns:**

    - `Lhx_vals`: x component of the unit vector L/|L|.
    - `Lhy_vals`: y component of the unit vector L/|L|.
    - `Lhz_vals`: z component of the unit vector L/|L|.
    - `S1hx_vals`: x component of the unit vector S1/|S1|.
    - `S1hy_vals`: y component of the unit vector S1/|S1|.
    - `S1hz_vals`: z component of the unit vector S1/|S1|.
    - `S2hx_vals`: x component of the unit vector S2/|S2|.
    - `S2hy_vals`: y component of the unit vector S2/|S2|.
    - `S2hz_vals`: z component of the unit vector S2/|S2|.
    - `t_fvals`: (optional) time as a function of the separation.
    '''

    def _compute(Lh0,S1h0,S2h0,r,q,chi1,chi2,quadrupole_formula):

        # I need unit vectors
        assert np.isclose(np.linalg.norm(Lh0),1)
        assert np.isclose(np.linalg.norm(S1h0),1)
        assert np.isclose(np.linalg.norm(S2h0),1)

        # Pack inputs
        if tracktime:
            ic = np.concatenate((Lh0,S1h0,S2h0,[0]))
        else:
            ic = np.concatenate((Lh0,S1h0,S2h0))

        # Compute these quantities here instead of inside the RHS for speed
        v=orbitalvelocity(r)
        m1=mass1(q)
        m2=mass2(q)
        S1,S2 = spinmags(q,chi1,chi2)
        eta=symmetricmassratio(q)

        # Integration
        res =scipy.integrate.odeint(orbav_eqs, ic, v, args=(q,m1,m2,eta,chi1,chi2,S1,S2,tracktime,quadrupole_formula), mxstep=5000000, full_output=0, printmessg=0,rtol=1e-12,atol=1e-12)

        # Returned output is
        # Lx, Ly, Lz, S1x, S1y, S1z, S2x, S2y, S2z, (t)
        return res.T


    if np.ndim(Lh0)==1:
        res = np.array([_compute(Lh0,S1h0,S2h0,r,q,chi1,chi2,quadrupole_formula)])
    else:
        res  = np.array(list(map(lambda x: _compute(*x,quadrupole_formula), zip(Lh0,S1h0,S2h0,r,q,chi1,chi2))))

    Lh = np.squeeze(np.swapaxes(res[:,0:3],1,2))
    S1h = np.squeeze(np.swapaxes(res[:,3:6],1,2))
    S2h = np.squeeze(np.swapaxes(res[:,6:9],1,2))

    if tracktime:
        t = np.squeeze(res[:,9])
        #Can't use toarray here because t has different shape
        return Lh,S1h,S2h,t
    else:
        return toarray(Lh,S1h,S2h)


def inspiral_orbav(theta1=None,theta2=None,deltaphi=None,S=None,Lh=None,S1h=None,S2h=None, J=None,kappa=None,r=None,u=None,xi=None,q=None,chi1=None,chi2=None,tracktime=False,quadrupole_formula=False,outputs=None):
    '''
    TODO: docstrings. Orbit average evolution; this is the function the user should call (I think)
    '''

    # Overwrite the tracktime flag if the user explicitely asked for the time output
    try:
        if 't' in outputs:
            tracktime=True
    except:
        pass

    def _compute(theta1,theta2,deltaphi,S,Lh,S1h,S2h,J,kappa,r,u,xi,q,chi1,chi2):

        if q is None:
            raise TypeError("Please provide q.")
        if chi1 is None:
            raise TypeError("Please provide chi1.")
        if chi2 is None:
            raise TypeError("Please provide chi2.")

        if r is not None and u is None:
            r=toarray(r)
            u = eval_u(r, np.repeat(q,flen(r)) )
        elif r is None and u is not None:
            u=toarray(u)
            r = eval_r(u, np.repeat(q,flen(u)) )
        else:
            raise TypeError("Please provide either r or u.")


        # User provides Lh, S1h, and S2h
        if Lh is not None and S1h is not None and S2h is not None and theta1 is None and theta2 is None and deltaphi is None and S is None and J is None and kappa is None and xi is None:
            pass

        # User provides theta1,theta2, and deltaphi.
        elif Lh is None and S1h is None and S2h is None and theta1 is not None and theta2 is not None and deltaphi is not None and S is None and J is None and kappa is None and xi is None:
            Lh, S1h, S2h = angles_to_Jframe(theta1, theta2, deltaphi, r[0], q, chi1, chi2)

        # User provides J, xi, and S.
        elif Lh is None and S1h is None and S2h is None and theta1 is None and theta2 is None and deltaphi is None and S is not None and J is not None and kappa is None and xi is not None:
            Lh, S1h, S2h = conserved_to_Jframe(S, J, r[0], xi, q, chi1, chi2)

        # User provides kappa, xi, and maybe S.
        elif Lh is None and S1h is None and S2h is None and theta1 is None and theta2 is None and deltaphi is None and S is not None and J is None and kappa is not None and xi is not None:
            J = eval_J(kappa=kappa,r=r[0],q=q)
            Lh, S1h, S2h = conserved_to_Jframe(S, J, r[0], xi, q, chi1, chi2)

        else:
            TypeError("Please provide one and not more of the following: (Lh,S1h,S2h), (theta1,theta2,deltaphi), (S,J,xi), (S,kappa,xi).")

        # Make sure vectors are normalized
        Lh = normalize_nested(Lh)
        S1h = normalize_nested(S1h)
        S2h = normalize_nested(S2h)

        # Integration
        outcome = orbav_integrator(Lh,S1h,S2h,r,q,chi1,chi2,tracktime=tracktime,quadrupole_formula=quadrupole_formula)
        Lh,S1h,S2h = outcome[0:3]
        if tracktime:
            t=outcome[3]
        else:
            t=None

        S1,S2= spinmags(q,chi1,chi2)
        L = angularmomentum(r,np.repeat(q,flen(r)))
        Lvec= (L*Lh.T).T
        S1vec= S1*S1h
        S2vec= S2*S2h

        theta1, theta2, deltaphi = vectors_to_angles(Lvec, S1vec, S2vec)
        S, J, xi = vectors_to_conserved(Lvec, S1vec, S2vec, q)
        kappa = eval_kappa(J, r, q)

        return toarray(t,theta1,theta2,deltaphi,S,Lh,S1h,S2h,J,kappa,r,u,xi,q,chi1,chi2)

    #This array has to match the outputs of _compute (in the right order!)
    alloutputs = np.array(['t','theta1','theta2','deltaphi','S','Lh','S1h','S2h','J','kappa','r','u','xi','q','chi1','chi2'])

    # allresults is an array of dtype=object because different variables have different shapes
    if flen(q)==1:
        allresults =_compute(theta1,theta2,deltaphi,S,Lh,S1h,S2h,J,kappa,r,u,xi,q,chi1,chi2)
    else:
        inputs = np.array([theta1,theta2,deltaphi,S,Lh,S1h,S2h,J,kappa,r,u,xi,q,chi1,chi2])
        for k,v in enumerate(inputs):
            if v==None:
                inputs[k] = itertools.repeat(None) #TODO: this could be np.repeat(None,flen(q)) if you need to get rid of the itertools dependence

        theta1,theta2,deltaphi,S,Lh,S1h,S2h,J,kappa,r,u,xi,q,chi1,chi2= inputs
        allresults = np.array(list(map(_compute, theta1,theta2,deltaphi,S,Lh,S1h,S2h,J,kappa,r,u,xi,q,chi1,chi2))).T

    # Handle the outputs.
    # Return all
    if outputs is None:
        outputs = alloutputs
    # Return only those requested (in1d return boolean array)
    wantoutputs = np.in1d(alloutputs,outputs)

    # Store into a dictionary
    outcome={}
    for k,v in zip(alloutputs[wantoutputs],allresults[wantoutputs]):
        if not tracktime and k=='t':
            continue
        # np.stack fixed shapes and object types
        outcome[k]=np.stack(np.atleast_1d(v))

    return outcome


def inspiral(*args, which=None,**kwargs):
    '''
    TODO write docstings. This is the ultimate wrapper the user should call.
    '''

    # Precession-averaged integrations
    if which in ['precession','precav','precessionaveraged','precessionaverage','precession-averaged','precession-average']:
        return inspiral_precav(*args, **kwargs)

    elif which in ['orbit','orbav','orbitaveraged','orbitaverage','orbit-averaged','orbit-average']:
        return inspiral_orbav(*args, **kwargs)

    else:
        raise ValueError("kind need to be either 'precav' or 'orbav'.")


if __name__ == '__main__':
    np.set_printoptions(threshold=sys.maxsize)
    #print(masses([0.5,0.6]))

    # r=[10,10]
    # #xi=[0.35,-0.675]
    # q=[0.8,0.2]
    # chi1=[1,1]
    # chi2=[1,1]
    # #J=[1,0.23]
    #
    # print(Jlimits(r=r,q=q,chi1=chi1,chi2=chi2))

    #print(Slimits_plusminus(J,r,xi,q,chi1,chi2))
    #t0=time.time()
    #print(Jofr(ic=1.8, r=np.linspace(100,10,100), xi=-0.5, q=0.4, chi1=0.9, chi2=0.8))
    #print(time.time()-t0)

    # t0=time.time()
    #print(repr(Jofr(ic=203.7430728810311, r=np.logspace(6,1,100), xi=-0.5, q=0.4, chi1=0.9, chi2=0.8)))
    # print(time.time()-t0)



    # theta1inf=0.5
    # theta2inf=0.5
    # q=0.5
    # chi1=0.6
    # chi2=0.7
    # kappainf, xi = angles_to_asymptotic(theta1inf,theta2inf,q,chi1,chi2)
    # r = np.concatenate(([np.inf],np.logspace(10,1,100)))
    # print(repr(Jofr(kappainf, r, xi, q, chi1, chi2)))


    # r=1e2
    # xi=-0.5
    # q=0.4
    # chi1=0.9
    # chi2=0.8
    #
    # Jmin,Jmax = Jlimits(r=r,xi=xi,q=q,chi1=chi1,chi2=chi2)
    # J0=(Jmin+Jmax)/2
    # #print(J)
    # #print(Jmin,Jmax)
    # r = np.logspace(np.log10(r),1,100)
    # J=Jofr(J0, r, xi, q, chi1, chi2)
    # print(J)
    #
    # J=Jofr([J0,J0], [r,r], [xi,xi], [q,q], [chi1,chi1], [chi2,chi2])
    #
    # print(J)



    #S = Ssampling(J,r,xi,q,chi1,chi2,N=1)

    #S = Ssampling([J,J],[r,r],[xi,xi],[q,q],[chi1,chi1],[chi2,chi2],N=[10,10])

    #print(repr(S))

    ##### INSPIRAL TESTING: precav, to/from finite #######
    q=0.5
    chi1=1
    chi2=1
    theta1=0.4
    theta2=0.45
    deltaphi=0.46
    S = 0.5538768649231461
    J = 2.740273008918153
    xi = 0.9141896967861489
    kappa = 0.5784355256550922
    r=np.logspace(2,1,6)
    d=inspiral_precav(theta1=theta1,theta2=theta2,deltaphi=deltaphi,q=q,chi1=chi1,chi2=chi2,r=r,outputs=['J'])
    print(d)

    d=inspiral(which='precav',theta1=theta1,theta2=theta2,deltaphi=deltaphi,q=q,chi1=chi1,chi2=chi2,r=r,outputs=['J'])

    print(d)

    d=inspiral_orbav(theta1=theta1,theta2=theta2,deltaphi=deltaphi,q=q,chi1=chi1,chi2=chi2,r=r,outputs=['J'])
    print(d)

    d=inspiral(which='orbav',theta1=theta1,theta2=theta2,deltaphi=deltaphi,q=q,chi1=chi1,chi2=chi2,r=r,outputs=['J'])

    print(d)

    #print('')

    # d=inspiral_precav(theta1=[theta1,theta1],theta2=[theta2,theta2],deltaphi=[deltaphi,deltaphi],q=[q,q],chi1=[chi1,chi1],chi2=[chi2,chi2],r=[r,r])
    #
    # # #d=inspiral_precav(theta1=theta1,theta2=theta2,deltaphi=deltaphi,q=q,chi1=chi1,chi2=chi2,r=r,outputs=['r','theta1'])
    # #
    # # #d=inspiral_precav(S=S,J=J,xi=xi,q=q,chi1=chi1,chi2=chi2,r=r)
    # # #d=inspiral_precav(J=J,xi=xi,q=q,chi1=chi1,chi2=chi2,r=r)
    # # #d=inspiral_precav(S=S,kappa=kappa,xi=xi,q=q,chi1=chi1,chi2=chi2,r=r)
    # # #d=inspiral_precav(kappa=kappa,xi=xi,q=q,chi1=chi1,chi2=chi2,r=r)
    # #
    # print(d)

    ###### INSPIRAL TESTING: precav, from infinite #######
    # q=0.5
    # chi1=1
    # chi2=1
    # theta1=0.4
    # theta2=0.45
    # kappa = 0.50941012
    # xi = 0.9141896967861489
    # r=np.concatenate(([np.inf],np.logspace(2,1,6)))
    #
    # #d=inspiral_precav(theta1=theta1,theta2=theta2,q=q,chi1=chi1,chi2=chi2,r=r)
    # d=inspiral_precav(kappa=kappa,xi=xi,q=q,chi1=chi1,chi2=chi2,r=r,outputs=['J','theta1'])
    #
    # print(d)
    #
    # d=inspiral_precav(kappa=[kappa,kappa],xi=[xi,xi],q=[q,q],chi1=[chi1,chi1],chi2=[chi2,chi2],r=[r,r],outputs=['J','theta1'])
    #
    # print(d)
    # ###### INSPIRAL TESTING #######
    # q=0.5
    # chi1=1
    # chi2=1
    # theta1=0.4
    # theta2=0.45
    # deltaphi=0.46
    # S = 0.5538768649231461
    # J = 1.2314871608018418
    # xi = 0.9141896967861489
    # kappa=0.7276876186801603
    #
    # #kappa = 0.5784355256550922
    # r=np.concatenate((np.logspace(1,4,6),[np.inf]))
    # #d=inspiral_precav(theta1=theta1,theta2=theta2,deltaphi=deltaphi,q=q,chi1=chi1,chi2=chi2,r=r)
    # #d=inspiral_precav(S=S,J=J,xi=xi,q=q,chi1=chi1,chi2=chi2,r=r)
    # #d=inspiral_precav(J=J,xi=xi,q=q,chi1=chi1,chi2=chi2,r=r)
    # #d=inspiral_precav(S=S,kappa=kappa,xi=xi,q=q,chi1=chi1,chi2=chi2,r=r)
    # d=inspiral_precav(kappa=kappa,xi=xi,q=q,chi1=chi1,chi2=chi2,r=r)
    #
    # print(d)
    #

    # q=0.5
    # chi1=1
    # chi2=1
    # theta1=0.4
    # theta2=0.45
    # deltaphi=0.46
    # S = 0.5538768649231461
    # J = 2.740273008918153
    # xi = 0.9141896967861489
    # kappa0 = 0.5784355256550922
    # r=np.logspace(2,1,6)
    # u=eval_u(r,q)
    # print(kappaofu(kappa0, u, xi, q, chi1, chi2))
    # print(kappaofu([kappa0,kappa0], [u,u], [xi,xi], [q,q], [chi1,chi1], [chi2,chi2]))



    #
    # xi=-0.5
    # q=0.4
    # chi1=0.9
    # chi2=0.8
    # r=np.logspace(2,1,100)
    # Jmin,Jmax = Jlimits(r=r[0],xi=xi,q=q,chi1=chi1,chi2=chi2)
    # J=(Jmin+Jmax)/2
    # Smin,Smax= Slimits(J=J,r=r[0],xi=xi,q=q,chi1=chi1,chi2=chi2)
    # S=(Smin+Smax)/2
    # Svec, S1vec, S2vec, Jvec, Lvec = conserved_to_Jframe(S, J, r[0], xi, q, chi1, chi2)
    # S1h0=S1vec/spin1(q,chi1)
    # S2h0=S2vec/spin2(q,chi2)
    # Lh0=Lvec/angularmomentum(r[0],q)
    #
    # print(J,S)

    # xi=-0.5
    # q=0.4
    # chi1=0.9
    # chi2=0.8
    # r=np.logspace(2,1,5)
    # Lh0,S1h0,S2h0 = sample_unitsphere(3)
    # #print(Lh0,S1h0,S2h0)
    # t0=time.time()
    # Lh,S1h,S2h = orbav_integrator(Lh0,S1h0,S2h0,r,q,chi1,chi2,tracktime=False)
    # print(Lh)
    #
    # Lh,S1h,S2h,t = orbav_integrator([Lh0,Lh0],[S1h0,S1h0],[S2h0,S2h0],[r,r],[q,q],[chi1,chi1],[chi2,chi2],tracktime=True)
    #
    # print(t)
    #
    # print(time.time()-t0)
    # #print(Lh)

    # ### ORBAV TESTING ####
    # xi=-0.5
    # q=0.4
    # chi1=0.9
    # chi2=0.8
    # r=np.logspace(2,1,5)
    # Lh,S1h,S2h = sample_unitsphere(3)
    #
    # d= inspiral_orbav(Lh=Lh,S1h=S1h,S2h=S2h,r=r,q=q,chi1=chi1,chi2=chi2,tracktime=True)
    # print(d)
    # print(" ")
    #
    # theta1,theta2,deltaphi = vectors_to_angles(Lh,S1h,S2h)
    # d= inspiral_orbav(theta1=theta1,theta2=theta2,deltaphi=deltaphi,r=r,q=q,chi1=chi1,chi2=chi2)
    # print(d)
    # print(" ")
    #
    # S,J,xi = angles_to_conserved(theta1,theta2,deltaphi,r[0],q,chi1,chi2)
    # d= inspiral_orbav(S=S,J=J,xi=xi,r=r,q=q,chi1=chi1,chi2=chi2)
    # print(d)
    # print(" ")
    #
    #
    # kappa=eval_kappa(J,r[0],q)
    # d= inspiral_orbav(S=S,kappa=kappa,xi=xi,r=r,q=q,chi1=chi1,chi2=chi2)
    # print(d)
    # print(" ")
    #
    # d= inspiral_orbav(Lh=Lh,S1h=S1h,S2h=S2h,r=r,q=q,chi1=chi1,chi2=chi2)
    # print(d)
    # print(" ")
    #
    #
    # d= inspiral_orbav(Lh=[Lh,Lh],S1h=[S1h,S1h],S2h=[S2h,S2h],r=[r,r],q=[q,q],chi1=[chi1,chi1],chi2=[chi2,chi2],tracktime=True)
    # print(d)
    # print(" ")


    # J=6.1
    # print("LS",Slimits_LJS1S2(J,r,q,chi1,chi2)**2)
    # print(S2roots(J,r,xi,q,chi1,chi2))
    #
    # J=6.6
    # print(Slimits_LJS1S2(J,r,q,chi1,chi2)**2)
    # print(S2roots(J,r,xi,q,chi1,chi2))
    #
    # # print(repr(Jofr(ic=(Jmin+Jmax)/2, r=np.logspace(6,1,100), xi=-0.5, q=0.4, chi1=0.9, chi2=0.8)))
    # for J in [5.99355616 ,6.0354517,6.20850742,6.57743474,6.94028614]:
    #     ssol = Slimits_plusminus(J,r,xi,q,chi1,chi2,coincident=True)[0]**2
    #     smin,smax = Slimits_LJS1S2(J,r,q,chi1,chi2)**2
    #     print(ssol>smin,ssol<smax)
    #


    # print( dSdtprefactor(r,xi,q) )
    # kappa=eval_kappa(J,r,q)
    # u=eval_u(r,q)
    # print(S2roots_NEW(kappa,u,xi,q,chi1,chi2))


    #print(Jresonances(r[0],xi[0],q[0],chi1[0],chi2[0]))
    #print(Jresonances(r[1],xi[1],q[1],chi1[1],chi2[1]))
    #print(Jresonances(r,xi,q,chi1,chi2))
    #print(Jlimits(r=r,xi=xi,q=q,chi1=chi1,chi2=chi2))
    #print(Jlimits(r=r,q=q,chi1=chi1,chi2=chi2))


    #
    # r=1e14
    # xi=-0.5
    # q=0.4
    # chi1=0.9
    # chi2=0.8
    #
    #
    # Jmin,Jmax = Jlimits(r=r,xi=xi,q=q,chi1=chi1,chi2=chi2)
    # print(Jmin,Jmax)
    #
    # print(Satresonance([Jmin,Jmax],[r,r],[xi,xi],[q,q],[chi1,chi1],[chi2,chi2]))
    #
    #
    # print(xiresonances((Jmin+Jmax)/2,r,q,chi1,chi2))
    #print(xiresonances(J[1],r[1],q[1],chi1[1],chi2[1]))
    #print(xiresonances(J,r,q,chi1,chi2))

    #
    # t0=time.time()
    # [S2roots(J[0],r[0],xi[0],q[0],chi1[0],chi2[0]) for i in range(100)]
    # #print(Slimits_plusminus(J,r,xi,q,chi1,chi2))
    # print(time.time()-t0)
    #
    # @np.vectorize
    # def ell(x):
    #   if x==0:
    #     return 1/2
    #   else:
    #       return (1- scipy.special.ellipe(x)/scipy.special.ellipk(x))/x
    #
    # # Should be equivalent to
    # def ell(x):
    #     return np.where(x==0, 1/2, (1- scipy.special.ellipe(x)/scipy.special.ellipk(x))/x)
    #
    # t0=time.time()
    # [ell(0.5) for i in range(100)]
    # print(time.time()-t0)

    #print(xilimits(q=q,chi1=chi1,chi2=chi2))

    #print(xilimits(J=J,r=r,q=q,chi1=chi1,chi2=chi2))
    #S=[0.4,0.6668]

    #print(effectivepotential_plus(S,J,r,q,chi1,chi2))
    #print(effectivepotential_minus(S,J,r,q,chi1,chi2))

    #print(Slimits_cycle(J,r,xi,q,chi1,chi2))


    #M,m1,m2,S1,S2=pre.get_fixed(q[0],chi1[0],chi2[0])
    #print(pre.J_allowed(xi[0],q[0],S1[0],S2[0],r[0]))

    #print(Jresonances(r,xi,q,chi1,chi2))


    #print(Jlimits(r,q,chi1,chi2))
    #print(S2roots(J,r,xi,q,chi1,chi2))



    #print(Slimits_check([0.24,4,6],q,chi1,chi2,which='S1S2'))

    # q=[0.7,0.7]
    # chi1=[0.7,0.7]
    # chi2=[0.9,0.9]
    # r=[30,30]
    # J=[1.48,1.48]
    # xi=[0.25,0.18]
    #print("stillworks",S2roots(J,r,xi,q,chi1,chi2))


    #print(morphology(J,r,xi,q,chi1,chi2))
    #print(morphology(J[0],r[0],xi[0],q[0],chi1[0],chi2[0]))

    # theta1=[0.567,1]
    # theta2=[1,1]
    # deltaphi=[1,2]
    #S,J,xi = angles_to_conserved(theta1,theta2,deltaphi,r,q,chi1,chi2)
    #print(S,J,xi)
    #theta1,theta2,deltaphi=conserved_to_angles(S,J,r,xi,q,chi1,chi2)
    #print(theta1,theta2,deltaphi)
    #print(eval_costheta1(0.4,J[0],r[0],xi[0],q[0],chi1[0],chi2[0]))

    #print(eval_thetaL([0.5,0.6],J,r,q,chi1,chi2))

    # tau = Speriod(J[0],r[0],xi[0],q[0],chi1[0],chi2[0])
    # Smin,Smax = Slimits_plusminus(J[0],r[0],xi[0],q[0],chi1[0],chi2[0])
    # t= np.linspace(0,tau,200)
    # S= Soft([t,t],J,r,xi,q,chi1,chi2)
    #
    # #print(t)
    # print(np.shape([t,t]))
    # print(np.shape(S))
    # #S= Soft(t,J[0],r[0],xi[0],q[0],chi1[0],chi2[0])

    #print(S[1:5])

    #S= Soft(t[4],J[0],r[0],xi[0],q[0],chi1[0],chi2[0])

    #print(S)

    #import pylab as plt
    #plt.plot(t/1e5,S)
    #plt.axhline(Smin)
    #plt.axhline(Smax)
    #plt.show()

    #
    # chi1=0.9
    # chi2=0.8
    # q=0.8
    # Lh,S1h,S2h = sample_unitsphere(3)
    # S1,S2= spinmags(q,chi1,chi2)
    # r=10
    # L = angularmomentum(r,q)
    # S1vec = S1*S1h
    # S2vec = S2*S2h
    # Lvec = L*Lh
    #
    # S, J, xi = vectors_to_conserved(Lvec, S1vec, S2vec, q)
    # theta1,theta2,deltaphi = conserved_to_angles(S,J,r,xi,q,chi1,chi2,sign=+1)
    # #print(theta1,theta2,deltaphi)
    # #print(vectors_to_conserved([S1vec,S1vec], [S2vec,S2vec], [Lvec,Lvec], [q,q+0.1]))
    # #print(' ')
    # #print(vectors_to_angles(S1vec, S2vec, Lvec))
    # #print(vectors_to_angles([S1vec,S1vec], [S2vec,S2vec], [Lvec,Lvec]))
    # # print(conserved_to_Jframe(S, J, r, xi, q, chi1, chi2))
    # # print(conserved_to_Jframe([S,S], [J,J], [r,r], [xi,xi], [q,q], [chi1,chi1], [chi2,chi2]))
    # #
    # # print(angles_to_Jframe(theta1, theta2, deltaphi, r, q, chi1, chi2))
    # #print(angles_to_Jframe([theta1,theta1], [theta2,theta2], [deltaphi,deltaphi], [r,r], [q,q], [chi1,chi1], [chi2,chi2]))
    #
    # #print(angles_to_Lframe(theta1, theta2, deltaphi, r, q, chi1, chi2))
    # print(angles_to_Lframe([theta1,theta1], [theta2,theta2], [deltaphi,deltaphi], [r,r], [q,q], [chi1,chi1], [chi2,chi2]))
    #
    # print(conserved_to_Lframe([S,S], [J,J], [r,r], [xi,xi], [q,q], [chi1,chi1], [chi2,chi2]))

    # r=10
    # q=0.5
    # chi1=2
    # chi2=2
    # which='uu'
    # print(omega2_aligned([r,r], [q,q], [chi1,chi1], [chi2,chi2], 'dd'))
