import subprocess as sp
import os
import itertools as it
from math import e
import numpy as np
from scipy import optimize

###########
# Classes #
###########

class Site:
    '''
    A class to represent a binding site for a TF.
    '''
    def __init__(self,TF,start,stop,score):
        self.TF = TF
        self.start = start
        self.stop = stop
        self.score = score
    def __repr__(self):
        rep = "(" + self.TF + ", " + str(self.start) + ", " + str(self.stop) +  ", " + str(self.score) + ")"
        return rep


##############################################
# Functions involved in the algorithm itself #
##############################################


def Z(i,sites,Zs,R,w):
    '''
    The function Z(i) in the publication.
    '''
    q = R[sites[i].TF]*e**(-1000*sites[i].score)
    recur = 1.0 # variable to hold the result of the recursion
    #recurse over all sites *before the one in the outer loop*
    j = 0
    while j < i and sites[j].stop < sites[i].start:
        recur += w[sites[i].TF][sites[j].TF] * Zs[j]
        j += 1
    return q * recur

def I(a,b):
    '''
    Indicator function for if two strings are equal.
    Used to test whether a binding site is for a particular TF.
    '''
    if a == b:
        return 1.0
    else:
        return 0.0

def Y(i,k,sites,Ys,Zs,R,w):
    '''
    The function Y(i) from the paper.
    '''
    q = R[sites[i].TF]*e**(-1000*sites[i].score)
    recur = I(sites[i].TF,k)
    j = 0
    while j < i and sites[j].stop < sites[i].start:
        recur += w[sites[i].TF][sites[j].TF] * (Ys[j] + I(sites[i].TF,k)*Zs[j])
        j += 1
    return q * recur


def numbound(k,sites,R,w):
    '''
    Given a transcription factor/motif 'k', the list of sites in a sequence,
    and dictionaries of parameters (R and w), calculates the
    number of TFs bound to the sequence.
    '''
    denom = 1.0
    numer = 0.0
    Zs = {} # memoizing Z
    Ys = {} # memoizing Y
    for idx in range(0,len(sites)):
        thisZ =  Z(idx,sites,Zs,R,w)
        thisY =  Y(idx,k,sites,Ys,Zs,R,w)
        numer += thisY
        denom += thisZ
        Zs[idx] = thisZ
        Ys[idx] = thisY
    return numer/denom


##############################
# Functions for optimization #
##############################


def errfxn(params,TF,motifs,sitelists,target_vals):
    '''
    Calculates the squared error between a prediction, which is
    computed for the given params (a flat array), TF (a string),
    motifs (a list of strings), and sitelists (dict with a list of
    sites for each sequence) and known target values, which are given
    for each sequence in the list target_vals.
    '''
    # unravel parameters into dictionaries
    R,w = unravel_params(motifs,params)
    error = 0.0
    # do calculations and determine error
    for seq in sitelists:
            error += (numbound(TF,sitelists[seq],R,w) - target_vals[seq]) ** 2
    return error


def ravel_params(motifs,R,w):
    '''
    ravel dicts of parameters into a flat array suitable for passing to scipy.optimize.minimize
    '''
    nTFs = len(motifs)
    # make an ndarray of the correct size
    parray = np.empty([nTFs,nTFs+1])
    # assign R values to the first column of the array
    for idx,motif in enumerate(motifs):
        parray[idx,0] = R[motif]
    # assign w values to the remaining columns
    for idx,val in np.ndenumerate(parray[:,1:]):
        parray[:,1:][idx] = w[motifs[idx[0]]][motifs[idx[1]]]
    return parray.flatten()

def unravel_params(motifs,parray):
    '''
    unravel parameters from a flat array into dictionaries so they
    can be used in calls to Z,Y, and numbound.
    '''
    #reshape the flat array
    nTFs = len(motifs)
    parray = parray.reshape([nTFs,nTFs+1])
    # get out R values
    R = {}
    for idx,motif in enumerate(motifs):
        R[motif] = parray[idx,0]
    # get out w values
    w = {}
    for motif in motifs:
        w[motif] = {}
    for idx,val in np.ndenumerate(parray[:,1:]):
        w[motifs[idx[0]]][motifs[idx[1]]] = parray[:,1:][idx]
    return R,w


def processfiles(seqsfname,motifsfname,thresh):
    '''
    process files and return a list of measured affinities,
    list of motif names, and dictionary of sites for each sequence,
    sorted by start site
    '''
    seqsfile = open(seqsfname)
    motifsfile = open(motifsfname)
    seqvals = {}
    for line in seqsfile:
        if ">" in line:
            spl = line.split()
            seqvals[spl[1]] = float(spl[2])
            
    # get motifs using fimo, within each sequence, sort by start
    # get fimo output
    with open(os.devnull, 'w') as devnull:
        fimout = sp.Popen(["fimo","--text","--thresh",str(thresh),motifsfname,seqsfname],
                          stdout=sp.PIPE,
                          stderr=devnull)

    # build up a list of sites in each sequence
    sitelists = {}
    # also build up a list of motifs
    motifs = []
    for line in fimout.stdout:
        if "#" in line or "Using" in line:
            continue
        spl = line.split("\t")
        if spl[1] not in sitelists.keys():
            sitelists[spl[1]] = []
        sitelists[spl[1]].append(Site(spl[0],int(spl[2]),int(spl[3]),float(spl[6])))
        # build up a list of motifs as we go
        if spl[0] not in motifs:
            motifs.append(spl[0])
            
    # now sort the sites in each list by position
    for sequence in sitelists:
        sitelists[sequence].sort(key=lambda site: site.start)
    return seqvals,motifs,sitelists


def stap(TF, seqsfname, motifsfname, thresh, meth = "L-BFGS-B",cb = None):
    '''
    Takes as input a TF of interest,
    a sequence file containing sequences and their measured binding
    affinities to TF of interest, a motif file of motifs to consider,
    and outputs the optimal parameters.
    meth and cb can be used to set the method and callback used in parameter tuning.
    '''
    seqvals,motifs,sitelists = processfiles(seqsfname, motifsfname, thresh)

    # now we want to set up the parameters and make initial guesses for each one
    R = {}
    for motif in motifs:
        R[motif] = 10*np.random.rand()#np.exp(np.random.normal(loc = 0.0, scale = 1.1))
    w = {}
    for outer_motif in motifs:
        w[outer_motif] = {}
        for inner_motif in motifs:
            w[outer_motif][inner_motif] = 10* np.random.rand()

    
    # now we do parameter tuning using scipy.optimize.minimize
    parray = ravel_params(motifs,R,w)
    return optimize.minimize(errfxn,
                             parray,
                             args=[TF,motifs,sitelists,seqvals],
                             method = meth,
                             bounds = [(0,None) for i in range(0,len(parray.flatten()))],
                             callback = cb)
