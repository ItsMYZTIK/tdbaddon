"""
    Copyright (C) 2016 ECHO Wizard

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
"""
import xbmc, xbmcaddon, xbmcgui, xbmcplugin,os,base64,sys,xbmcvfs
import urllib2,urllib
import re
import glob
import extract
import plugintools
import downloader
import time
import common as Common
import wipe
from urllib import FancyURLopener

class MyOpener(FancyURLopener):
	version = 'TheWizardIsHere'

myopener = MyOpener()
urlretrieve = MyOpener().retrieve
urlopen = MyOpener().open
AddonTitle="[COLOR lime]ECHO[/COLOR] [COLOR white]Wizard[/COLOR]"
USERDATA     =  xbmc.translatePath(os.path.join('special://home/userdata',''))
ECHO_VERSION  =  os.path.join(USERDATA,'echo_build.txt')
BASEURL = base64.b64decode(b"aHR0cDovL2VjaG9jb2Rlci5jb20v")

dp = xbmcgui.DialogProgress()
dialog = xbmcgui.Dialog()

############################
###CHECK FOR UPDATES########
############################

def updateaddons():

	xbmc.executebuiltin( "ActivateWindow(busydialog)" )
	xbmc.executebuiltin('UpdateAddonRepos()')
	xbmc.executebuiltin('UpdateLocalAddons()')
	xbmc.executebuiltin( "Dialog.Close(busydialog)" )
	dialog.ok(AddonTitle,'[COLOR ghostwhite]All repositories have been checked for updates.[/COLOR]','[COLOR smokewhite]All available addon updates have now been installed.[/COLOR]','')

def check():	

	xbmc.executebuiltin( "ActivateWindow(busydialog)" )

#######################################################################
#						Check for ECHO Updates
#######################################################################

	#Information for ECHO Wizard OTA updates.
	if os.path.exists(ECHO_VERSION):
		VERSIONCHECK = ECHO_VERSION
		FIND_URL = BASEURL + base64.b64decode(b'YnVpbGRzL3dpemFyZC91cGRhdGVfd2l6LnR4dA==')
		checkurl = BASEURL + base64.b64decode(b'YnVpbGRzL3dpemFyZC92ZXJzaW9uX2NoZWNrLnR4dA==')
		pleasecheck = 1

	if pleasecheck == 1:
		dialog = xbmcgui.Dialog()
		vers = open(VERSIONCHECK, "r")
		regex = re.compile(r'<build>(.+?)</build><version>(.+?)</version>')
		for line in vers:
			if pleasecheck == 1:
				currversion = regex.findall(line)
				for build,vernumber in currversion:
					if vernumber > 0:
						req = urllib2.Request(checkurl)
						req.add_header('User-Agent','TheWizardIsHere')
						try:
							response = urllib2.urlopen(req)
						except:
							dialog.ok(AddonTitle,'Sorry we are unable to check for updates!','The update host appears to be down.','Please check for updates later via the wizard.')
							sys.exit(1)			
							xbmc.executebuiltin( "Dialog.Close(busydialog)" )
						link=response.read()
						response.close()
						match = re.compile('<build>'+build+'</build><version>(.+?)</version><fresh>(.+?)</fresh>').findall(link)	
						for newversion,fresh in match:
							if newversion > vernumber:
								choice = xbmcgui.Dialog().yesno("UPDATE AVAILABLE", 'Found a new update for the Build', build + " ver: "+newversion, 'Do you want to install it now?', yeslabel='[B][COLOR green]YES[/COLOR][/B]',nolabel='[B][COLOR lightskyblue]NO[/COLOR][/B]')
								if choice == 1: 
									if fresh =='false': # TRUE
										updateurl = FIND_URL
										req = urllib2.Request(updateurl)
										req.add_header('User-Agent','TheWizardIsHere')
										try:
											response = urllib2.urlopen(req)
										except:
											dialog.ok(AddonTitle,'Sorry we were unable to download the update!','The update host appears to be down.','Please check for updates later via the wizard.')
											sys.exit(1)		
											xbmc.executebuiltin( "Dialog.Close(busydialog)" )
										link=response.read()
										response.close()
										match = re.compile('<build>'+build+'</build><url>(.+?)</url>').findall(link)
										for url in match:
								
											path = xbmc.translatePath(os.path.join('special://home/addons','packages'))
											name = "build"
											dp = xbmcgui.DialogProgress()

											dp.create(AddonTitle,"Downloading ",'', 'Please Wait')
											lib=os.path.join(path, name+'.zip')
											try:
												os.remove(lib)
											except:
												pass
									
											downloader.download(url, lib, dp)
											addonfolder = xbmc.translatePath(os.path.join('special://','home'))
											time.sleep(2)
											dp.update(0,"", "Extracting Zip Please Wait")
											print '======================================='
											print addonfolder
											print '======================================='
											extract.all(lib,addonfolder,dp)
											xbmc.executebuiltin( "Dialog.Close(busydialog)" )
											dialog = xbmcgui.Dialog()
											dialog.ok(AddonTitle, "Your build has succesfully been updated to the latest version.","Kodi must now force close to complete the update.")							
											Common.KillKodi()
									else:
										dialog.ok('[COLOR lightskyblue]A WIPE is required for the update[/COLOR]','Select the [COLOR green]YES[/COLOR] option in the NEXT WINDOW to wipe now.','Select the [COLOR lightskyblue]NO[/COLOR] option in the NEXT WINDOW to update later.','[I][COLOR smokewhite]If you wish to update later you can do so in [/COLOR][COLOR ghostwhite]ECHO[/COLOR] [COLOR lightsteelblue]Wizard[/COLOR][/I]')
										xbmc.executebuiltin( "Dialog.Close(busydialog)" )
										wipe.FRESHSTART()
										sys.exit(1)		
								else:
									xbmc.executebuiltin( "Dialog.Close(busydialog)" )
									sys.exit(1)		
							else:
								xbmc.executebuiltin( "Dialog.Close(busydialog)" )
								dialog.ok(AddonTitle,'[COLOR ghostwhite]Your build is up to date.[/COLOR]', "[COLOR ghostwhite]Current Build: [/COLOR][COLOR smokewhite]" + build + "[/COLOR]", "[COLOR ghostwhite]Current Version: [/COLOR][COLOR smokewhite]" + newversion + "[/COLOR]")
								sys.exit(1)	

	#LAST LINE OF UPDATES
	xbmc.executebuiltin( "Dialog.Close(busydialog)" )
	dialog.ok(AddonTitle,'[COLOR ghostwhite]An unknown error occurred.[/COLOR]', "[COLOR smokewhite]Please contact ECHO Wizard to resolve this issue.[/COLOR]", "[COLOR ghostwhite]http://www.echocoder.com[/COLOR]")