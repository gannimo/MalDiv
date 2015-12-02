#!/usr/bin/env python

"""
Handles extracting information about binary executables using ObjDump.
"""

import copy
import os
import pprint
import re
import subprocess as sub
import sys

from util import address_to_bytes, \
                 int32, \
                 find_instruction, \
                 execute

class ObjDump(object):
    """Represents information about a binary extracted using ObjDump"""

    def __init__(self, path=None):
        """Initializes a new ObjDump instance with data extracted from the binary
        located at 'path'"""

        self.sections = {}
        self.labels = {}
        self.min_address = None
        self.max_address = None
        self.path = path

        if path is not None and not os.path.exists(path):
            raise Exception("'%s' does not exist" % path)
        
        # Extract symbols
        self.extract_symbols(path)

        # Extract relocation information
        self.extract_relocations()

        if path is not None:
            parse_dump(execute('objdump -d "%s"' % path), self)

    def extract_relocations(self):
        """Extracts relocation information"""
        s = execute('objdump -rR "%s"' % self.path)
        self.relocations = []

        for line in s.splitlines():
            cols = line.split(None, 3)
            if len(cols) != 3:
                continue
            
            addr, reloc_type, value = cols
            try:
                addr = int(addr, 16)
            except ValueError:
                continue
            
            self.relocations += [(addr, reloc_type, value)]

        self.relocations.sort()

    def extract_symbols(self, path):
        """Extracts symbol table information"""
        s = execute('objdump -t "%s"' % path)
        for line in s.splitlines():
            line = line.strip()

            if not line:
                continue

            try:
                l, r = line.split('\t')
            except ValueError:
                continue

            l = l.strip()
            addr, sep, typ = l.partition(' ')
            if not sep:
                continue
            
            r = r.strip()
            size, sep, name = r.partition(' ')
            if not sep:
                continue
            
            size = size.strip()
            size.lstrip('0')
            name = name.strip()

            size = int(size, 16)
            addr = int(addr, 16)

            if addr == 0:
                continue

            if typ.find("g") == -1 or typ.find("gcc_except_table") != -1 or typ.find("F") != -1:
                name = name + "<" + str(addr) + ">"

            # Create label and store
            if name in self.labels:
                if self.labels[name]['offset'] != addr:
                    sys.stderr.write('Warning: %s: -t reported %x, already is %x\n' % (name, addr, self.labels[name]['offset']))
                    print typ
                        
            label = {
                'name': name,
                'offset': addr,
                'end_offset': addr + size
            }
            self.labels[name] = label

    def find_relocations(self, start, end):
        """Returns all relocations that start in the range [start, end["""
        return ((addr, reloc_type, name) for (addr, reloc_type, name) in self.relocations if start <= addr < end)

    def label_info(self, name, debug_fallback=False):
        """Returns the symbol information for symbol with name 'name'

        Note: does not resort to debugging information if no entry in symbol table is found

        Raises an Exception if no symbol with that name exists"""
        if name in self.labels:            
            return self.labels[name]
        raise Exception("Label %s does not exist." % name)

    def label_location(self, name):
        """Returns the location and length of a symbol or (None, None) if it does not exists"""
        # Try resolving using basic information
        if name in self.labels:
            label = self.labels[name]
            return (label['offset'], label['end_offset'])

        # Try resolving using debug information
        if name in self.debug_info.name_to_tag:
            tag = self.debug_info.name_to_tag[name]
            return (tag['location'], tag['location']+1)

        return (None, None)

    def label_for_address(self, addr):
        """Returns the name of a symbol and offset within it at which 'addr' is located"""
        # Try resolving using basic information
        for name, label in self.labels.iteritems():
            if label['offset'] <= addr < label['end_offset']:
                #print '%x < %x < %x' % (label['offset'], addr, label['end_offset'])
                return (label['name'], addr - label['offset'])

        # Try resolving using debug information
        for (start, end), tag in self.debug_info.address_to_tag.iteritems():  
            if start <= addr < end:
                return (tag['name'], addr - start)

        return None
        
    def __str__(self):
        return pprint.pformat({
            'sections': self.sections,
            'labels': self.labels
        }, indent=2)
        
    def __repr__(self):
        return self.__str__()


def parse_dump(s, result=None):
    """Parses the stdout from a call to objdump with parameter -d and stores it
    in an ObjDump instance"""

    if result is None:
        result = ObjDump()
    
    section_name = None
    current_section = None
    current_label = None

    for line in s.split('\n'):
        if len(line.strip()) == 0:
            continue
        cols = [col.strip() for col in line.split('\t')]

        # Section name        
        m = re.match('Disassembly of section (.*?):', cols[0])
        if m is not None:
            section_name = m.groups()[0]
            current_section = {
                'name': section_name,
                'instructions': [],
                'mnemonics': []
            }
            result.sections[section_name] = current_section
            continue

        # Section offset
        m = re.match('([0-9abcdef]+) \\<(.*?)\\>:', cols[0])
        if m is not None:
            offset, name = m.groups()
            result.labels[name] = {
                'name': name,
                'offset': int(offset, 16),
                'end_offset': int(offset, 16),
                'instructions': [],
                'mnemonics': []
            }
            
            current_label = result.labels[name]
            
            if 'offset' not in current_section:
                current_section['offset'] = offset
            continue

        # Assume: instructions
        if len(cols) == 3:
            offset, binary, source = cols
            
            offset = offset.strip(':')
            offset = int(offset, 16)
            
            binary = [int(byte, 16) for byte in binary.split()]

            if source.find(" ") != -1:
              src = source[0:source.find(" ")]
            else:
              src = source
            current_section['instructions'] += [list(binary)]
            current_label['instructions'] += [list(binary)]
            current_section['mnemonics'].append(src)
            current_label['mnemonics'].append(src)
            assert current_label['end_offset'] == offset, '%x == %x' % (current_label['end_offset'], offset)

            current_label['end_offset'] += len(binary)
            current_section['end_offset'] = offset + len(binary)                    
            continue

        # Assume: instruction without assembly source code            
        if len(cols) == 2:
            if cols[0] == '':
                continue
            offset, binary = cols
            
            offset = offset.strip(':')
            offset = int(offset, 16)
            
            binary = [int(byte, 16) for byte in binary.split()]
            
            assert len(current_section['instructions']) > 0
            assert current_label['end_offset'] == offset, '%x == %x' % (current_label['end_offset'], offset)
            current_label['end_offset'] += len(binary)    

            current_section['end_offset'] = offset + len(binary)        
            
            current_section['instructions'][-1] += binary
            current_label['instructions'][-1] += binary
                        
            continue
    return result
