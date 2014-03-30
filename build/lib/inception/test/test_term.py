'''
Inception - a FireWire physical memory manipulation and hacking tool exploiting
IEEE 1394 SBP-2 DMA.

Copyright (C) 2011-2013  Carsten Maartmann-Moe

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Created on Jan 13, 2013

@author: Carsten Maartmann-Moe <carsten@carmaa.com> aka ntropy
'''
from _pyio import StringIO
from inception import cfg
from inception import term
import sys
import unittest


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass
    
        
    def test_write(self):
        s = 'A' * (3 * term.size())
        cfg.wrapper.width = term.size()
        sys.stdout = StringIO() # Suppress output
        sys.stdout.write('')
        term.write(s)
        out = sys.stdout.getvalue()
        sys.stdout = sys.__stdout__ # Restore output
        expected = 'A' * term.size()
        n = term.size()
        expected = 'A' * term.size() + '\n    '
        t = 'A' * (2 * term.size())
        expected = expected + '\n    '.join([t[i:i+n-4] for i in range(0, len(t) -4 , n-4)]) + '\n'
        self.assertEqual(out, expected)


if __name__ == "__main__":
    unittest.main()