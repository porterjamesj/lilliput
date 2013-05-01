import numpy as np
import random

#what is the probability that we find the bomb if it is in the square we search?
#The globality is a hack, it should be a parameter passed to the look and search functions
q = 0.95

def choosefrompdf(pdf):
    '''
    Given a numpy array representing a probability density function,
    randomly choose a cell according to the specified probabilites and
    return its indicies as a tuple.
    '''
    #the cumulative distribution function
    cdf = pdf.cumsum()
    #generate a random number on [0,1) and then ask what the indicies of this
    #number were to be if it were to be sorted into the cdf.
    return np.unravel_index(np.searchsorted(cdf,
                                            np.random.random_sample()),
                            pdf.shape)

def choosebest(pdf):
    '''
    Given a probability distribution, choose the cell with the
    highest probability (if multiple cells have the same highest
    probability, choose one randomly).
    '''
    #find the highest value in the array
    highprob = pdf[np.unravel_index(np.argmax(pdf),pdf.shape)]
    #get all indices whose value is approx equal to the highest probability
    indices = []
    for index, val in np.ndenumerate(pdf):
        if np.allclose(val,highprob):
            indices.append(index)
    #choose from among these randomly
    return random.choice(indices)
    
def initialize(filename):
    '''Get a search field (pdf) from a file and place the bomb.  The
    search field is the probability density function we want to search
    over. It might look something like this:

    0.1 0.1 0.1
    0.1 0.2 0.1
    0.1 0.1 0.1

    which specifies a 3x3 array in which the center cell has
    probability 0.2 of containing the object we are looking for (which
    I am calling the bomb) and all other cells have probability 0.1.

    The field can be of any size (as long as it is a proper array) and the
    probabilites don't need to sum to one; they will be scaled up or
    down if they don't. For example, the following input:

    1 1 1
    1 2 1
    1 1 1

    Is equivalent to the first example. Returns sfield, an array
    containing the probabilities, and bomb, a tuple representing the
    location of the bomb.
    '''
    sfield = np.loadtxt(filename)
    sfield = sfield  / sfield.sum()
    # assign the bomb a location according to the probability distribution
    #note that this assumes the given distribution is correct
    bomb = choosefrompdf(sfield)
    return sfield,bomb


def look(_sfield,bomb,q, method = "best"):
    '''
    Looks for the bomb in the given search field, returning a bool
    representing whether it was found and the updated search field
    probabilities.

    Takes the search field as an array, the bomb location as a tuple,
    q (the uncertainty parameter) as a number, and an optional
    argument that specifies the search method, of which there are two:

    best: always chooses the cell with the greatest probability.

    random: chooses a cell randomly using the probabilities in the
    search field.

    The default method is best.
    '''
    #prevent the global object from being mutated
    sfield = np.copy(_sfield)
    #select a cell to look in using the specified method
    if method == "best":
        lookcell = choosebest(sfield)
    if method == "random":
        lookcell = choosefrompdf(sfield)
    #look for the bomb in the choosen lookcell
    if bomb == lookcell and np.random.random_sample() < q:
        return True,sfield
    else:
        #if the bomb is not found, apply the math from:
        #https://en.wikipedia.org/wiki/Bayesian_search_theory
        p = sfield[lookcell]
        for x,y in np.ndindex(sfield.shape):
            if (x,y) == lookcell:
                sfield[x,y] = p*((1.-q)/(1.-p*q))
            else:
                r = sfield[x,y]
                sfield[x,y] = r*(1./(1.-p*q))
        return False,sfield

def search(sfield,bomb,method = "best"):
    '''
    Search for the specified bomb (tuple) in the specified search field (an array), using
    the specified method ("best" or "random"). Returns the number of
    looks it took to find the bomb.
    '''
    m = method
    tries = 0
    found = False
    while found == False:
        tries += 1
        found,sfield = look(sfield,bomb,method = m)
    return tries
