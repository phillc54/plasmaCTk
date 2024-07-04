'''
conv_ellipse.py

Copyright (C) 2021, 2022  Phillip A Carter
Copyright (C) 2021, 2022  Gregory D Carl

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
from importlib import reload
from plasmac import ellipse as ELLIPSE

for f in sys.path:
    if '/lib/python' in f:
        if '/usr' in f:
            localeDir = 'usr/share/locale'
        else:
            localeDir = os.path.join(f"{f.split('/lib')[0]}",'share','locale')
        break
gettext.install('linuxcnc', localedir=localeDir)

def preview(self):
    matNum = int(self.matCombo.get().split(':')[0])
    matNam = self.matCombo.get().split(':')[1].strip()
    isCenter = self.spButton.cget('text') == _('Center')
    isExternal = self.ctButton.cget('text') == _('External')
    kerfWidth = self.parent.materialFileDict[matNum]['kerf_width']
    error = ELLIPSE.preview(self, self.fTmp, self.fNgc, self.fNgcBkp, \
            matNum, matNam, \
            self.preAmble, self.postAmble, \
            self.liValue.get(), self.loValue.get(), \
            isCenter, self.xsValue.get(), self.ysValue.get(), \
            kerfWidth, isExternal, \
            self.wValue.get(), self.hValue.get(), self.aValue.get(), \
            self.unitsPerMm)
    if error:
        self.dialog_show_ok(_('Ellipse Error'), error)
    else:
        self.plot_file(self.fNgc)
        self.addC.configure(state = 'normal')
        self.undoC.configure(state = 'normal')
        self.preview_button_pressed(True)

def auto_preview(self):
    if self.wValue.get() and self.hValue.get():
        preview(self)

def widgets(self):
    if self.parent.comp['development']:
        reload(ELLIPSE)
    # start settings
    if not self.settingsExited:
        self.wValue.set('')
        self.hValue.set('')
        self.aValue.set('')
    #connections
    self.ctButton.configure(command=lambda:self.cut_type_clicked())
    self.spButton.configure(command=lambda:self.start_point_clicked())
    self.previewC.configure(command=lambda:preview(self))
    #add to layout
    self.matLabel.grid(column=0, row=0, padx=(4,2), pady=(4,2), sticky='e')
    self.matCombo.grid(column=1, row=0, padx=(2,4), pady=2, columnspan=3, sticky='ew')
    self.spLabel.grid(column=0, row=1, padx=(4,2), pady=2, sticky='e')
    self.spButton.grid(column=1, row=1, padx=2, pady=2, sticky='w')
    self.ctLabel.grid(column=2, row=1, padx=2, pady=2, sticky='e')
    self.ctButton.grid(column=3, row=1, padx=(2,4), pady=2, sticky='w')
    self.xsLabel.grid(column=0, row=2, padx=(4,2), pady=2, sticky='e')
    self.xsEntry.grid(column=1, row=2, padx=2, pady=2, sticky='w')
    self.ysLabel.grid(column=2, row=2, padx=2, pady=2, sticky='e')
    self.ysEntry.grid(column=3, row=2, padx=(2,4), pady=2, sticky='w')
    self.liLabel.grid(column=0, row=3, padx=(4,2), pady=2, sticky='e')
    self.liEntry.grid(column=1, row=3, padx=2, pady=2, sticky='w')
    self.loLabel.grid(column=2, row=3, padx=2, pady=2, sticky='e')
    self.loEntry.grid(column=3, row=3, padx=(2,4), pady=2, sticky='w')
    self.wLabel.grid(column=0, row=4, padx=(4,2), pady=2, sticky='e')
    self.wEntry.grid(column=1, row=4, padx=2, pady=2, sticky='w')
    self.hLabel.grid(column=0, row=5, padx=(4,2), pady=2, sticky='e')
    self.hEntry.grid(column=1, row=5, padx=2, pady=2, sticky='w')
    self.aLabel.grid(column=0, row=6, padx=(4,2), pady=2, sticky='e')
    self.aEntry.grid(column=1, row=6, padx=2, pady=2, sticky='w')
    # finish setup
    self.wEntry.focus()
    self.settingsExited = False
