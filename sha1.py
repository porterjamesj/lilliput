# sha1.py
# compute sha1 hash given filename

import bitstring as bs
import sys

# binary left rotation operator (for 32 bit ints only)
lrot = lambda x, n: (x << n) | (x >> (32 - n))

def sha1(fname):
    # initialize
    h0 = 0x67452301
    h1 = 0xEFCDAB89
    h2 = 0x98BADCFE
    h3 = 0x10325476
    h4 = 0xC3D2E1F0
    
    # read file in as bitstring
    msg = bs.BitArray(bs.Bits(filename=fname))
    #msg = bs.BitArray(bytes = "")
    beforelen = len(msg)

    # preprocessing
    # append '1'
    msg.append('0b1')
    #append '0' until we are congruent with 488 (mod 512)
    while((msg.length-448) % 512 != 0):
        msg.append('0b0')
    # append the length of original message
    msg.append(bs.BitArray(bs.Bits(intbe=beforelen,length=64)))

    #iterate over 512 bit chunks
    chunks = [msg[i*512:i*512+512] for i in range(0,msg.len/512)]
    for chunk in chunks:
        #print chunk.bin
        words = [chunk[i*32:i*32+32] for i in range(0,chunk.len/32)]
        words.extend(range(16,80))
        #expand to 80 words
        for i in range(16,80):
            words[i] = (words[i-3] ^ words[i-8] ^ words[i-14] ^ words[i-16])
            words[i].rol(1)

        #initialize chunks
        a = h0
        b = h1
        c = h2
        d = h3
        e = h4

        #hash that thing
        for i in range(0,80):
            if (0<=i<=19):
                f = ((b & c) | ((~b) & d))
                k = 0x5A827999
                print "herp"
            elif (20<=i<=39):
                f = (b^c^d)
                k = 0x6ED9EBA1
            elif (40<=i<=59):
                f = ((b&c)|(b&d)|(c&d))
                k =  0x8F1BBCDC
            elif (60<=i<=79):
                f = (b^c^d)
                k = 0xCA62C1D6

            tmp = (lrot(a,5) + f + e + k + words[i].int) % (2**32)
            e = d
            d = c
            c = lrot(b,30)
            b = a
            a = tmp

        h0 = (h0 + a) % (2**32)
        h1 = (h1 + b) % (2**32)
        h2 = (h2 + c) % (2**32)
        h3 = (h3 + d) % (2**32)
        h4 = (h4 + e) % (2**32)

    #compute hex digest and return it
    return hex(h0)[2:] + hex(h2)[2:] + hex(h2)[2:] + hex(h3)[2:] + hex(h4)[2:]
