#!/usr/bin/python3

import sys
import numpy as np
from scipy.sparse import coo_matrix

class electron():
    def __init__(self):
        self.center = 512.
        self.width = 1.25
        self.delay = .25
        self.name = 'unnamed'
    def print(self):
        outstring = '%s:\t%.2f\t%.2f\t%.2f'%(self.name,self.center,self.width,self.delay)
        print(outstring)

    def setname(self,x):
        self.name = x
        return self
    def setcenter(self,x):
        self.center = x
        return self
    def setwidth(self,x):
        self.width = x
        return self
    def setdelay(self,x):
        self.delay = x
        return self
    def setcenterwidthdelay(self,x,y,z):
        self.center = x
        self.width = y
        self.delay = z
        return self
    def __call__(self):
        return self.center,self.width,self.delay

class Photo(electron):
    def setcenterwidthdelay(self,x,y,z):
        self.center = x - self.binding
        self.width = y
        self.delay = z
        return self
    def setbinding(self,x):
        self.binding = x
        return self

class Auger(electron):
    def this(self):
        self.this = 0
        return self

def e2ind(e,emin,emax,n):
    v = int((float(e)-emin)*float(n)/float(emax-emin))
    if v<1:
        return int(0)
    if v>n-1:
        return int(n-1)
    return int(v)

def phi2ind(p,pmin,pmax,n):
    phase = int((float(p)-pmin)*float(n)/float(pmax-pmin))
    if phase<1:
        return int(0)
    if phase>n-1:
        return int(n-1)
    return int(phase)

def coordout(mat):
    inds = np.where(mat)
    return np.c_[np.c_[inds],mat[inds]]

def main():
    if len(sys.argv)<3:
        print('syntax:\t%s <outputfilehead> <nimages> <streakamp optional> <nelectrons scale optional>'%(sys.argv[0]))
        return
    streakamp = 20.
    nimages = 10
    scalein = 100
    if len(sys.argv)>2:
        nimages = int(sys.argv[2])
    if len(sys.argv)>3:
        streakamp = float(sys.argv[3])
    if len(sys.argv)>4:
        scalein = int(sys.argv[4])

    outhead = sys.argv[1]
    nangles = 64 
    nenergies = 2048 
    emin = 0
    emax = 512

    etotalwidth = 10.
    ecentral = 534.5
    angles = np.linspace(0,np.pi*2.,nangles+1)
    energies = np.linspace(emin,emax,nenergies+1)

    nitrogenaugers = [Auger() for i in range(3)]
    nitrogenaugers[0].setcenterwidthdelay(365,1.5,.5)
    nitrogenaugers[1].setcenterwidthdelay(369,1.5,.25)
    nitrogenaugers[2].setcenterwidthdelay(372,1.5,.25)

    carbonaugers = [Auger() for i in range(3)]
    carbonaugers[0].setcenterwidthdelay(255,2.5,.5)
    carbonaugers[1].setcenterwidthdelay(260,2.5,.25)
    carbonaugers[2].setcenterwidthdelay(252,1.5,.75)

    oxygenaugers = [Auger() for i in range(6)]
    oxygenaugers[0].setcenterwidthdelay(495,2.5,.125)
    oxygenaugers[1].setcenterwidthdelay(480,2.5,.25)
    oxygenaugers[2].setcenterwidthdelay(482,1.5,.25)
    oxygenaugers[3].setcenterwidthdelay(502,1.5,.5)
    oxygenaugers[4].setcenterwidthdelay(507,1.0,.5)
    oxygenaugers[5].setcenterwidthdelay(507,0.5,1.75)

    nphases = int(64)
    

    
    for img in range(nimages):
        timeenergy_NNO = np.zeros((nenergies,nphases),dtype=int)
        timeenergy_OCO = np.zeros((nenergies,nphases),dtype=int)
        hist_ens_NNO = np.zeros((nenergies,nangles),dtype=int)
        hist_ens_OCO = np.zeros((nenergies,nangles),dtype=int)
        hist_ens_auger_NNO = np.zeros((nenergies,nangles),dtype=int)
        hist_ens_auger_OCO = np.zeros((nenergies,nangles),dtype=int)
        outname = '%s.%02i'%(outhead,img)
        npulses = int(np.random.uniform(3,8))
        ecenters = np.random.normal(ecentral,etotalwidth,(npulses,))
        ewidths = np.random.gamma(3.5,.125,(npulses,))+.5
        ephases= np.random.uniform(0.,2.*np.pi,(npulses,))
        # rather than this, let's eventually switch to using a dict for the AUger features and then for every ncounts photoelectron, we pick from this distribution an Auger electron.
        augerfeatures_NNO = {505:2.5,497:1.,492:1.,365:1.5,369:1.5,372:1.5}
        augerfeatures_OCO = {505:2.5,497:1.,492:1.,250.:3.,255.:2.5,260.:2.5}
        #augerfeatures = {505:1.5,492:1.,365:1.5,372:1.5,250.:1.,260.:1.5}
        nitrogencenters = ecenters+535.-410.
        carboncenters = ecenters+535.-285.

        oxygenphotos = [Photo().setbinding(543.1).setcenterwidthdelay(ecenters[i],ewidths[i],ephases[i]) for i in range(npulses)]
        oxygenvalencephotos = [Photo().setbinding(41.6).setcenterwidthdelay(ecenters[i],ewidths[i],ephases[i]) for i in range(npulses)]
        nitrogenphotos = [Photo().setbinding(409.9).setcenterwidthdelay(ecenters[i],ewidths[i],ephases[i]) for i in range(npulses)]
        nitrogenvalencephotos = [Photo().setbinding(37.3).setcenterwidthdelay(ecenters[i],ewidths[i],ephases[i]) for i in range(npulses)]
        carbonphotos = [Photo().setbinding(284.2).setcenterwidthdelay(ecenters[i],ewidths[i],ephases[i]) for i in range(npulses)]
        scale = [int(v) for v in np.random.normal(scalein,scalein/10.,npulses)]
        for i in range(npulses):
            c0 = 1.
            c2 = np.random.uniform(-1,1)
            c2 = -1.
            c4 = np.random.uniform(-(c0+c2),c0+c2)
            c4 = 0.
            poldist = np.polynomial.legendre.Legendre([c0,0,c2,0,c4])(np.cos(angles[:-1]))
            c,w,p = nitrogenphotos[i]()
            timeenergy_NNO[e2ind(c,emin,emax,nenergies) , phi2ind(p,0,2*np.pi,nphases)] += scale[i]
            c,w,p = carbonphotos[i]()
            timeenergy_OCO[e2ind(c,emin,emax,nenergies) , phi2ind(p,0,2*np.pi,nphases)] += scale[i]

            for a in range(nangles):
                ncounts = int(poldist[a] * scale[i])
                augercounts = scale[i]
                if ncounts > 0:

                    #hist_ens_NNO[:,a] += np.histogram(np.random.normal(ecenters[i]+streak,ewidths[i],(ncounts,)),energies)[0]
                    c,w,p = nitrogenphotos[i]()
                    streak = streakamp*np.cos(angles[a]-p)
                    hist_ens_NNO[:,a] += np.histogram(np.random.normal(c+streak,w,(ncounts,)),energies)[0]
                    #augercenters_NNO = np.random.choice(list(augerfeatures_NNO.keys()),(augercounts,))
                    #ens_auger_NNO = [np.random.normal(c,augerfeatures_NNO[c])+streak for c in augercenters_NNO]
                    #hist_ens_auger_NNO[:,a] += np.histogram(ens_auger_NNO,energies)[0]
                    #hist_ens_OCO[:,a] += np.histogram(np.random.normal(ecenters[i]+streak,ewidths[i],(ncounts,)),energies)[0]
                    c,w,p = carbonphotos[i]()
                    hist_ens_OCO[:,a] += np.histogram(np.random.normal(c+streak,w,(ncounts,)),energies)[0]
                    #augercenters_OCO = np.random.choice(list(augerfeatures_OCO.keys()),(augercounts,))
                    #ens_auger_OCO = [np.random.normal(c,augerfeatures_OCO[c])+streak for c in augercenters_OCO]
                    #hist_ens_auger_OCO[:,a] += np.histogram(ens_auger_OCO,energies)[0]

        #np.savetxt(outname,hist_ens,fmt='%i')
        #np.savetxt('%s.%s'%(outname,'augers'),hist_ens_auger,fmt='%i')
        np.savetxt('%s.%s'%(outname,'timeenergy_NNO'),coordout(timeenergy_NNO),fmt='%i')
        np.savetxt('%s.%s'%(outname,'timeenergy_OCO'),coordout(timeenergy_OCO),fmt='%i')
        #np.savetxt('%s.%s'%(outname,'full_NNO'),hist_ens_NNO.T,fmt='%i')
        #np.savetxt('%s.%s'%(outname,'full_OCO'),hist_ens_OCO.T,fmt='%i')
        np.savetxt('%s.%s'%(outname,'full_NNO'),coordout(hist_ens_NNO),fmt='%i')
        np.savetxt('%s.%s'%(outname,'full_OCO'),coordout(hist_ens_OCO),fmt='%i')
    '''
    fig, ax = plt.subplots()#subplot_kw={"projection": "3d"})
    X,Y = np.meshgrid(angles,energies)
    Z = hist_ens.copy()
    surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)

    fig.colorbar(surf, shrink=0.5, aspect=5)

    plt.show()
    '''

    
    return


if __name__ == '__main__':
    main()
