#!/usr/bin/python

'''
Python script for encrypting / decrypting using a Vigenere cipher.
Supports arbitrary number of keywords.
'''

import argparse

#function definitions

def genkey(in_key,msg):
    '''generate the key string, capitalized, spaces stripped, and of the correct length'''
    if len(in_key) > len(msg):
        key = ''.join(in_key.upper().split())[:len(msg)]
    else:
        key = ''.join(in_key.upper().split())
        a, b = divmod(len(msg),len(in_key))
        key = key * a + key[:b]
    return key

def tonums(s):
    '''convert chars to numbers'''
    return [ord(i)-65 for i in s]

def encrypt(msg, key):
    '''encrypt message using key'''
    cipher_nums = [i % 26 for i in map(sum,zip(tonums(msg),tonums(key)))]
    cipher_text = ''.join([str(unichr(i + 65)) for i in cipher_nums])
    return cipher_text


def decrypt(msg, key):
    '''decrypt message using key'''
    plain_nums =  [i % 26 for i in map(lambda x,y:x-y,tonums(msg),tonums(key))]
    plain_text =  ''.join([str(unichr(i + 65)) for i in plain_nums])
    return plain_text

#argument parsing, encryption / decryption and returning

parser = argparse.ArgumentParser(description='Vigenere cipher')

parser.add_argument('message')
parser.add_argument('keys', nargs="*")
parser.add_argument('-e', action="store_true")
parser.add_argument('-d', action="store_true")

args = parser.parse_args()

if args.e and args.d:
    print "You must choose encryption or decryption!"
    raise SystemExit

#capitalize the message and remove spaces
msg = ''.join(args.message.upper().split())
#capitalize string and make it the correct length
keys = [genkey(key,msg) for key in args.keys]
    
#if the -e flag was passed, encrypt using each key in the stream until none are left
if args.e:
    print reduce(encrypt,keys,msg)

#if the -d flag was passed, decrypt using each key until none are left
if args.d:
    args.keys.reverse()
    print reduce(decrypt,keys,msg)
