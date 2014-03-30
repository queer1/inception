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

Created on Jan 14, 2013

@author: Carsten Maartmann-Moe <carsten@carmaa.com> aka ntropy
'''

class InceptionException(Exception):
    '''
    Non... rien de rien
    Non je ne regrette rien
    Ni le bien... qu'on m'a fait
    Ni le mal, tout ça m'est bien égale...
    '''
    def __init__(self, message, Errors):

        # Call the base class constructor
        Exception.__init__(self, message)

        # Handle errors (for now assign to base class Errors)
        self.Errors = Errors