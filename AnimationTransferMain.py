###### This code runs the exporter with the GUI ######

import sys

path = r"G:\Animation Transfer Script"

if sys.path.count(path) < 1:
    sys.path.append(path)

import loadXMLUI

ui = loadXMLUI.loadUI(path + "/GUI.ui")
controller = loadXMLUI.UIController(ui)
print "# GUI Loaded #"