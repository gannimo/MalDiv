#!/usr/bin/env python

import subprocess as sub

def int32(n):
    """Wrap an unsigned integer to stay in the range of an 
    unsigned 32-bit integer

    Note: this function is handy in cases where python might automatically
          promote an int to long type
    """
    return n % (2**32)

def address_to_bytes(a, num_bytes=4):
    """Translate an address represented by an integer to a sequence
    of bytes to be used in x86 machine code"""
    result = []
    
    assert type(a) in (int, long), "Was expecting int or long, but was %s (%s)" % (type(a), a)
    
    is_negative = (a < 0)
    if is_negative:
        a = a + 2**(num_bytes*8)
        assert a >= 0
    
    for _ in xrange(num_bytes):
        result += [(a % 256)]
        a = a / 256
        
    assert a == 0
    
    return result          
    
def find_instruction(instructions, base_addr, addr):
    """Return an index into a nested linked list representing
    a sequence of instructions

    instructions: list of instructions, each represented by a
                  list of machine code bytes
    base_addr:    memory address of the first instruction
    addr:         address of the bytes to be looked up
    """
    for index, instr in enumerate(instructions):
        if base_addr <= addr < base_addr + len(instr):
            return (index, addr - base_addr)
        base_addr += len(instr)
    return (None, None)    
    
def execute(command):
    """Execute a command and return the stdout"""
    p = sub.Popen(command, shell=True, stdout=sub.PIPE, stderr=sub.PIPE)
    stdout, stderr = p.communicate()
    return stdout

def bytes_to_int(xs):
    """Converts a list of bytes to an integer"""
    result = 0
    for x in reversed(xs):
        if not(0 <= x < 256):
            raise Exception("Is not a byte: %d" % x)
        result = result * 256 + x
    return result    
    
if __name__ == '__main__':
    assert address_to_bytes(64, num_bytes=4) == [0x40, 0, 0, 0]    
    assert address_to_bytes(-1, num_bytes=4) == [0xff, 0xff, 0xff, 0xff]
    assert address_to_bytes(-10, num_bytes=4) == [0xf6, 0xff, 0xff, 0xff]    

    assert bytes_to_int([0x00, 0x67, 0x08, 0x08]) == 0x8086700