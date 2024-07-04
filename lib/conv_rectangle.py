'''
conv_rectangle.py

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
from importlib import reload
from plasmac import rectangle as RECTANGLE

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
    isOvercut = self.ocButton.cget('state') == 'normal' and self.ocButton.cget('text') == _('On')
    kerfWidth = self.parent.materialFileDict[matNum]['kerf_width']
    styles = [None, 'extRadius', 'extRadius', 'extRadius', 'extRadius']
    values = [None, self.r1Button.cget('text'), self.r2Button.cget('text'), self.r3Button.cget('text'), self.r4Button.cget('text')]
    for n in range(1, 5):
        if values[n].startswith(_('Chamfer')):
            styles[n] = 'chamfer'
        elif values[n].startswith(_('Fillet')):
            styles[n] = 'intRadius'
    error = RECTANGLE.preview(self, self.fTmp, self.fNgc, self.fNgcBkp, \
            matNum, matNam, \
            self.preAmble, self.postAmble, \
            self.liValue.get(), self.loValue.get(), \
            isCenter, self.xsValue.get(), self.ysValue.get(), \
            kerfWidth, isExternal, \
            self.wValue.get(), self.hValue.get(), self.aValue.get(), \
            styles[1], styles[2], styles[3], styles[4], \
            self.r1Value.get(), self.r2Value.get(), self.r3Value.get(), self.r4Value.get(),
            self.r1Button.cget('text'), self.r2Button.cget('text'), self.r3Button.cget('text'), self.r4Button.cget('text'))
    if error:
        self.dialog_show_ok(_('Rectangle Error'), error)
    else:
        self.file_loader(self.fNgc, True, False)
        self.addC.configure(state = 'normal')
        self.undoC.configure(state = 'normal')
        self.preview_button_pressed(True)

def auto_preview(self):
    if self.wValue.get() and self.hValue.get():
        preview(self)

def radius_button_pressed(self, button, sequence):
    if button.cget('text')[:-2] == _('Radius'):
        text = _('Chamfer')
    elif button.cget('text')[:-2] == _('Chamfer'):
        text = _('Fillet')
    else:
        text = _('Radius')
    button.configure(text=f'{text} {sequence}')
    auto_preview(self)

def widgets(self):
    if self.parent.comp['development']:
        reload(RECTANGLE)
    # start settings
    if not self.settingsExited:
        self.wValue.set('')
        self.hValue.set('')
        self.aValue.set('')
        self.r1Value.set('')
        self.r1Button.configure(text=_('Radius 1'))
        self.r2Value.set('')
        self.r2Button.configure(text=_('Radius 2'))
        self.r3Value.set('')
        self.r3Button.configure(text=_('Radius 3'))
        self.r4Value.set('')
        self.r4Button.configure(text=_('Radius 4'))
    #connections
    self.ctButton.configure(command=lambda:self.cut_type_clicked())
    self.spButton.configure(command=lambda:self.start_point_clicked())
    self.previewC.configure(command=lambda:preview(self))
    self.r1Button.configure(command=lambda:radius_button_pressed(self, self.r1Button, '1'))
    self.r2Button.configure(command=lambda:radius_button_pressed(self, self.r2Button, '2'))
    self.r3Button.configure(command=lambda:radius_button_pressed(self, self.r3Button, '3'))
    self.r4Button.configure(command=lambda:radius_button_pressed(self, self.r4Button, '4'))
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
    self.hLabel.grid(column=2, row=4, padx=2, pady=2, sticky='e')
    self.hEntry.grid(column=3, row=4, padx=(2,4), pady=2, sticky='w')
    self.aLabel.grid(column=0, row=5, padx=(4,2), pady=2, sticky='e')
    self.aEntry.grid(column=1, row=5, padx=2, pady=2, sticky='w')
    self.r1Button.grid(column=0, row=6, padx=(4,2), pady=2, sticky='e')
    self.r1Entry.grid(column=1, row=6, padx=2, pady=2, sticky='w')
    self.r2Button.grid(column=2, row=6, padx=2, pady=2, sticky='e')
    self.r2Entry.grid(column=3, row=6, padx=(2,4), pady=2, sticky='w')
    self.r3Button.grid(column=0, row=7, padx=(4,2), pady=2, sticky='e')
    self.r3Entry.grid(column=1, row=7, padx=2, pady=2, sticky='w')
    self.r4Button.grid(column=2, row=7, padx=2, pady=2, sticky='e')
    self.r4Entry.grid(column=3, row=7, padx=(2,4), pady=2, sticky='w')
    # finish setup
    self.wEntry.focus()
    self.settingsExited = False
