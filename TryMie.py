import math
Pi = math.pi
import numpy

#NANG = 90

#Translated into Python from bhmie.c

#This uses one-based arrays because it descends from a
#Fortran original.  The zero index isn't used. To rationalize
#the code, it should be re-written as zero-based, but that
#needs to be done cautiously since it's easy to introduce
#mistakes..
#
#Inputs:
#         x        2*Pi*rad*REFMED/lam
#         refrel   Relative index of refraction of particle
#         nang     Number of angles for phase function
#
#If called with the default nang, it returns only the scattering eff,
#absorption eff, and asymmetry factor.  If called with nang>2, it
#returns the theta array and the phase function as well.
#

#----------------------------------------------------------------
#
#6/13/2013: Replaced numpy with numpy and fixed Float type so
#           it works with numpy
#
#Change Log:
def bhmie(x,refrel,nang = 2):
    an_old = 0. + 0.j
    bn_old = 0. + 0.j
    amu = numpy.zeros(nang+1,numpy.float)
    theta = numpy.zeros(nang+1,numpy.float)
    pi = numpy.zeros(nang+1,numpy.float)
    tau = numpy.zeros(nang+1,numpy.float)
    pi0 = numpy.zeros(nang+1,numpy.float)
    pi1 = numpy.zeros(nang+1,numpy.float)

    d = numpy.zeros(3000,numpy.complex) #**Change this to a dynamical allocation
    s1 = numpy.zeros(2*nang,numpy.complex)
    s2 = numpy.zeros(2*nang,numpy.complex)
    dx = x
    y = x*refrel
    xstop = x + 4.*x**(1./3.) + 2.
    nstop = int(xstop)
    ymod = abs(y)
    
    if xstop > ymod:
        nmx = int(xstop + 15)
    else:
        nmx = int(ymod + 15)
    dang = (Pi/2.)/(nang - 1.)
    for j in range(1,nang+1):
        theta[j] = (j - 1.)*dang
        amu[j] = math.cos(theta[j])

    d[nmx] = 0. + 0.j
    nn = nmx - 1
    for n in range(1,nn+1):
        rn = nmx - n + 1
        d[nmx-n] =rn/y -1./(d[nmx-n+1] + rn/y)
        
    for j in range(1,nang+1):
        pi0[j] = 0.0
        pi1[j] = 1.0
    nn = 2*nang - 1

    for j in range(1,nn+1):
        s1[j] = complex(0.0,0.0)
        s2[j] = complex(0.0,0.0)

    psi0 = math.cos(dx)
    psi1 = math.sin(dx)
    chi0 = -math.sin(x)
    chi1 = math.cos(x)
    apsi0 = psi0
    apsi1 = psi1
    xi0 = complex(apsi0,-chi0)
    xi1 = complex(apsi1,-chi1)
    qsca = 0.0
    g = 0.0
    n = 1
#--------------------------------------
    while n - 1 - nstop < 0:
        dn = float(n)
        rn = float(n)
        fn = (2.*rn + 1.)/(rn*(rn + 1.))
        psi = (2.*dn - 1.)*psi1/dx - psi0
        apsi = psi
        chi = (2.*rn - 1.)*chi1/x - chi0
        xi = complex(apsi,-chi)
#-----------------------------------------        
        an =apsi*(d[n]/refrel+rn/x) - apsi1
        an = an/((d[n]/refrel+rn/x)*xi-xi1)
        bn = apsi*(refrel*d[n]+rn/x) - apsi1
        bn = bn/((refrel*d[n]+rn/x)*xi-xi1)
        qsca += (2*rn + 1.)*(abs(an)**2 + abs(bn)**2)
        if rn > 1:
            g += ((rn - 1.)*(rn + 1.)/rn)*(an_old*an.conjugate()+bn_old*bn.conjugate()).real +\
                 ((2.*(rn - 1.) + 1.)/((rn - 1.)*rn))*(an_old*bn_old.conjugate()).real                
        an_old = an
        bn_old = bn
#------------------------------------------
        for  j in range(1,nang+1):
            jj = 2*nang - j
            pi[j] = pi1[j]
            tau[j] = rn*amu[j]*pi[j] - (rn + 1)*pi0[j]
            p = (-1)**(n-1)
            s1[j] = s1[j]+fn*(pi[j]*an +tau[j]*bn)
            t = (-1)**n
            s2[j] = s2[j]+fn*(tau[j]*an+pi[j]*bn)
##      if(j == jj) continue; 
            if not (j == jj):
                s1[jj] = s1[jj] + fn*(pi[j]*p*an+tau[j]*t*bn)
                s2[jj] = s2[jj]+  fn*(tau[j]*t*an+pi[j]*p*bn)
  
        psi0 = psi1
        psi1 = psi
        apsi1 = psi1
        chi0 = chi1
        chi1 = chi
        xi1 = complex(apsi1,-chi1)
        n = n + 1
        rn = float(n)

        for j in range(1,nang+1):
            pi1[j] = ((2.*rn - 1.)/(rn - 1.))*amu[j]*pi[j]
            pi1[j] = pi1[j] - rn*pi0[j]/(rn - 1.)
            pi0[j] = pi[j]
#  while(n - 1 - nstop < 0);
#-------------------------------
#Returns
    qsca *= 2./x**2
    qext = (4./x**2)*s1[1].real 
    qback = (4./x**2)*abs(s1[2*nang - 1])**2
    g *= 4./(x**2*qsca)
    qabs = qext - qsca
    #
    #Compute the phase function and normalize it
    P = numpy.absolute(s1)**2 + numpy.absolute(s2)**2
    P = P[1:] #Convert it to a zero based array 
    thetaAll = numpy.array([j*dang for j in range(len(P))])
    sinthetaAll = numpy.sin(thetaAll)
    norm = sum(sinthetaAll*P*dang)
    P = 2.*P/norm #Normalize such that int P dOmega = 4Pi
    if nang > 2:
        return qabs,qsca,g,thetaAll,P
    else:
        return qabs,qsca,g

