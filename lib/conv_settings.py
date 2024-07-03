'''
conv_settings.py

Copyright (C) 2020, 2021, 2022  Phillip A Carter
Copyright (C) 2020, 2021, 2022  Gregory D Carl

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

import os, sys
import gettext

for f in sys.path:
    if '/lib/python' in f:
        if '/usr' in f:
            localeDir = 'usr/share/locale'
        else:
            localeDir = os.path.join(f"{f.split('/lib')[0]}",'share','locale')
        break
gettext.install('linuxcnc', localedir=localeDir)

def save_clicked(self):
    msg = []
    self.preAmble = self.preValue.get()
    self.postAmble = self.pstValue.get()
    self.origin = self.spButton.cget('text') == 'Center'
    error = ''
    valid, self.leadIn = self.conv_is_float(self.liValue.get())
    if not valid:
        msg = _('Invalid Lead in entry detected')
        error += f"{msg}\n\n"
    valid, self.leadOut = self.conv_is_float(self.loValue.get())
    if not valid:
        msg = _('Invalid Lead out entry detected')
        error += f"{msg}\n\n"
    valid, self.smallHoleDia = self.conv_is_float(self.shValue.get())
    if not valid:
        msg = _('Invalid Diameter entry detected')
        error += f"{msg}\n\n"
    valid, self.smallHoleSpeed = self.conv_is_int(self.hsValue.get())
    if not valid:
        msg = _('Invalid Speed % entry detected')
        error += f"{msg}\n\n"
    if error:
        self.dialog_show_ok(_('Settings Error'), error)
        return
    self.parent.prefs.set('CONVERSATIONAL', 'Preamble', self.preAmble)
    self.parent.prefs.set('CONVERSATIONAL', 'Postamble', self.postAmble)
    self.parent.prefs.set('CONVERSATIONAL', 'Origin', self.origin)
    self.parent.prefs.set('CONVERSATIONAL', 'Leadin', self.leadIn)
    self.parent.prefs.set('CONVERSATIONAL', 'Leadout', self.leadOut)
    self.parent.prefs.set('CONVERSATIONAL', 'Hole diameter', self.smallHoleDia)
    self.parent.prefs.set('CONVERSATIONAL', 'Hole speed', self.smallHoleSpeed)
    self.savedSettings['lead_in'] = self.liValue.get()
    self.savedSettings['lead_out'] = self.loValue.get()
    self.savedSettings['start_pos'] = self.spButton.cget('text')
    self.parent.parameter_write()
    self.settingsExited = 1

def reload_clicked(self):
    load(self, self.preAmble, self.leadIn, self.smallHoleDia, self.postAmble)
    show(self)
    if not self.settingsExited:
        self.settingsExited = 2

def exit_clicked(self):
    for child in self.parent.convTools.winfo_children():
        if child.winfo_class() == 'Radiobutton':
            child.configure(state = 'normal')
    self.restore_buttons()
    if not self.settingsExited:
        self.settingsExited = 3
    self.shape_request(self.oldConvButton)

def load(self, preAmble, leadin, smallHole, postAmble=None):
    postAmble = postAmble if postAmble else preAmble
    self.preAmble = self.parent.prefs.get('CONVERSATIONAL', 'Preamble', preAmble)
    self.postAmble = self.parent.prefs.get('CONVERSATIONAL', 'Postamble', postAmble)
    self.origin = bool(self.parent.prefs.get('CONVERSATIONAL', 'Origin', 0))
    self.leadIn = float(self.parent.prefs.get('CONVERSATIONAL', 'Leadin', leadin))
    self.leadOut = float(self.parent.prefs.get('CONVERSATIONAL', 'Leadout', 0))
    self.smallHoleDia = float(self.parent.prefs.get('CONVERSATIONAL', 'Hole diameter', smallHole))
    self.smallHoleSpeed = int(self.parent.prefs.get('CONVERSATIONAL', 'Hole speed', 60))
    self.parent.parameter_write()

def show(self):
    self.preValue.set(self.preAmble)
    self.pstValue.set(self.postAmble)
    self.liValue.set(self.leadIn)
    self.loValue.set(self.leadOut)
    self.shValue.set(f"{self.smallHoleDia}")
    self.hsValue.set(f"{self.smallHoleSpeed}")
    if self.origin:
        self.spButton.configure(text = _('Center'))
    else:
        self.spButton.configure(text = _('Btm left'))

def widgets(self):
    # connections
    self.spButton.configure(command=lambda:self.start_point_clicked())
    self.saveS.configure(command=lambda:save_clicked(self))
    self.reloadS.configure(command=lambda:reload_clicked(self))
    self.exitS.configure(command=lambda:exit_clicked(self))
    # remove common widgets
    self.previewC.grid_remove()
    self.addC.grid_remove()
    self.undoC.grid_remove()
    # add to layout
    self.preLabel.grid(column=0, row=0, padx=3, pady=3, sticky='e')
    self.preEntry.grid(column=1, row=0, padx=3, pady=3, sticky='ew', columnspan=3)
    self.pstLabel.grid(column=0, row=1, padx=3, pady=3, sticky='e')
    self.pstEntry.grid(column=1, row=1, padx=3, pady=3, sticky='ew', columnspan=3)
    self.llLabel.grid(column=0, row=2, padx=3, pady=3, sticky='ew', columnspan=4)
    self.liLabel.grid(column=0, row=3, padx=3, pady=3, sticky='e')
    self.liEntry.grid(column=1, row=3, padx=3, pady=3, sticky='w')
    self.loLabel.grid(column=2, row=3, padx=3, pady=3, sticky='e')
    self.loEntry.grid(column=3, row=3, padx=3, pady=3, sticky='w')
    self.shLabel.grid(column=0, row=4, padx=3, pady=3, sticky='ew', columnspan=4)
    self.dLabel.grid(column=0, row=5, padx=3, pady=3, sticky='e')
    self.shEntry.grid(column=1, row=5, padx=3, pady=3, sticky='w')
    self.hsLabel.grid(column=2, row=5, padx=3, pady=3, sticky='e')
    self.hsEntry.grid(column=3, row=5, padx=3, pady=3, sticky='w')
    self.pvLabel.grid(column=0, row=6, padx=3, pady=3, sticky='ew', columnspan=4)
    self.spLabel.grid(column=0, row=7, padx=3, pady=3, sticky='e')
    self.spButton.grid(column=1, row=7, padx=3, pady=3, sticky='w')
    self.saveS.grid(column=0, row=12)
    self.reloadS.grid(column=1, row=12, columnspan=2)
    self.exitS.grid(column=3, row=12)
    # finish setup
    self.preEntry.focus()
