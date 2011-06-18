'''
* This file is part of Touhou SRPG.
* Copyright (c) Hans Lo
*
* Touhou SRPG is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* Touhou SRPG is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with Touhou SRPG.  If not, see <http://www.gnu.org/licenses/>.
'''

from pygame.locals import *

#User Event defines
UI_EVENT = USEREVENT+3
OBJECTEVENT = USEREVENT+4

#Interface modes
I_BROWSE, I_MOVE, I_ATTACK = range(3)

# UI Event subtypes
MOVETO, ATTACK, ENDTURN = range(3)

# Animation facings
N, S, E, W = range(4)

# Character Menu Options
M_MOVE = 0
M_ATTACK = 1

# Creature Types
C_PLAYER = 0
C_ENEMY = 1

