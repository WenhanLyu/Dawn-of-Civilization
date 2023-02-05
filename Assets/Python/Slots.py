from Core import *
from RFCUtils import *

from SettlerMaps import getMap as getSettlerMap
from WarMaps import getMap as getWarMap
from Logging import time


def findSlot(iCiv):
	iSlot = next(iSlot for iSlot in range(iNumPlayers) if civ(iSlot) == iCiv)
	if iSlot is not None:
		return iSlot
	
	iSlot = next(iSlot for iSlot in range(iNumPlayers) if civ(iSlot) == -1)
	if iSlot is not None:
		return iSlot
	
	iSlot = next(iSlot for iSlot in range(iNumPlayers) if availableSlot(iSlot))
	if iSlot is not None:
		return iSlot

	return -1
	
def availableSlot(iSlot):
	if player(iSlot).isAlive():
		return False
	
	if player(iSlot).isHuman():
		return False
	
	if player(iSlot).isMinorCiv():
		return False
	
	return True
	
def addPlayer(iPlayer, iCiv, iBirthTurn=-1, bAlive=False, bMinor=False):
	game.addPlayer(iPlayer, 0, iCiv, iBirthTurn, bAlive, bMinor)
	data.dSlots[iCiv] = iPlayer

def updateCivilization(iPlayer, iCiv, iBirthTurn=-1):
	data.dSlots[iCiv] = iPlayer
	data.players[iPlayer].resetStability()
	
	iCurrentCivilization = player(iPlayer).getCivilizationType()
	if iCiv == iCurrentCivilization:
		return
	
	resetRevealedOwner(iPlayer)
	
	addPlayer(iPlayer, iCiv, iBirthTurn=iBirthTurn, bAlive=True)
	
	if iCurrentCivilization in data.dSlots:
		del data.dSlots[iCurrentCivilization]

def getImpact(iCiv):
	iActiveCiv = civ()

	if iActiveCiv == iCiv:
		return iImpactPlayer
	
	if iCiv in dNeighbours[iActiveCiv]:
		return iImpactPlayer
	
	if iCiv in dInfluences[iActiveCiv]:
		return iImpactPlayer
	
	iImpact = infos.civ(iCiv).getImpact()
	
	if not canEverRespawn(iCiv):
		iImpact -= 1
	
	if isOutdated(iCiv):
		iImpact -= 1
	
	return max(iImpactMarginal, iImpact)
			
def isOutdated(iCiv):
	if year() < year(dFall[iCiv]):
		return False

	lResurrections = dResurrections[iCiv]
	if not lResurrections:
		return True
	
	iFirstResurrectionStart = lResurrections[0][0]
	iLastResurrectionEnd = lResurrections[-1][1]
		
	if iLastResurrectionEnd < 2020:
		return True
		
	if iFirstResurrectionStart > dFall[iCiv]:
		return True
	
	return False

def getNextBirth():
	lUpcomingCivs = [iCiv for iCiv, iYear in dBirth.items() if turn() < year(iYear) - turns(5)]
	return find_min(lUpcomingCivs, dBirth.__getitem__).result

def getUnavailableSlots():
	return count(1 for iSlot in range(iNumPlayers) if not availableSlot(iSlot))

def allSlotsTaken():
	return getUnavailableSlots() >= iNumPlayers-1