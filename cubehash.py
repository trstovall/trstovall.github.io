
import sys, struct

def add(a, b):
    return (a + b) & (2**32-1)

def rot(x, n):
    return ((x << n) | (x >> (32-n))) & (2**32-1)

def stoi(s):
    s = bytearray(s + b'\x00' * ((4 - len(s)) & 3))
    return struct.unpack('<{}I'.format(int(len(s) / 4)), s)

def itob(i):
    return bytearray(struct.pack('<{}I'.format(len(i)), *i))

def round(s):
    #1
    x = [add(a, b) for a,b in zip(s[:16], s[16:])]
    x = [rot(a, 7) for a in s[:16]] + x
    #3
    x[:16] = x[8:16] + x[:8]
    x[:16] = [a ^ b for a,b in zip(x[:16], x[16:])]
    x[16:] = [x[i ^ 2] for i in range(16, 32)]
    #6
    x[16:] = [add(a, b) for a,b in zip(x[:16], x[16:])]
    x[:16] = [rot(a, 11) for a in x[:16]]
    x[16:] = [x[i ^ 4] for i in range(16, 32)]
    #9
    x[:16] = [a ^ b for a,b in zip(x[:16], x[16:])]
    x[16:] = [x[i ^ 1] for i in range(16, 32)]
    return x
    
def hash(       # CubeHash[i+r/b+f-h](m)
        m,      # the message to be hashed, a string less than 2**125 bytes long
        i=16,   # the number of initialization rounds
        r=16,   # the number of rounds per message block
        b=32,   # the number of bytes per message block
        f=32,   # the number of finalization rounds
        h=512): # the number of output bits
    # pad
    padding = '\x80' + '\x00' * ((b - len(m) - 1) % b)
    m += padding
    state = [h/8, b, r] + [0] * 29
    # initialize
    for n in range(i):
        state = round(state)
    # process
    for n in range(0, len(m), b):
        x = stoi(m[n:n+b])
        state[:len(x)] = [_a ^ _b for _a,_b in zip(state[:len(x)], x)]
        for n in range(r):
            state = round(state)
    # finalize
    state[-1] ^= 1
    for n in range(f):
        state = round(state)
    # truncate
    return itob(state[:h/32])
#

if __name__ == '__main__':
    for x in hash(sys.argv[1], *[int(i) for i in sys.argv[2:]]):
        print('{:02x}'.format(x)),

