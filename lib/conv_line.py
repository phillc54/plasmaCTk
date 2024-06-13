'''
conv_line.py

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
from plasmac import line as LINE

for f in sys.path:
    if '/lib/python' in f:
        if '/usr' in f:
            localeDir = 'usr/share/locale'
        else:
            localeDir = os.path.join(f"{f.split('/lib')[0]}",'share','locale')
        break
gettext.install('linuxcnc', localedir=localeDir)

def preview(self):
    if self.convLine['xLineEnd'] != self.conv_is_float(self.l1Value.get()) or \
       self.convLine['yLineEnd'] != self.conv_is_float(self.l2Value.get()):
        self.convLine['addSegment'] = 0
    if self.lineCombo.get() == _('LINE POINT ~ POINT'):
        error = LINE.do_line_point_to_point(self, self.l1Value.get(), self.l2Value.get(), \
                                            self.l3Value.get(), self.l4Value.get())
        if not error[0]:
            self.convLine['xLineEnd'] = error[1]
            self.convLine['yLineEnd'] = error[2]
            self.convLine['gcodeLine'] = error[3]
        else:
            error_set(self, f'{error[1]}\n')
            return
    elif self.lineCombo.get() == _('LINE BY ANGLE'):
        error = LINE.do_line_by_angle(self, self.l1Value.get(), self.l2Value.get(), \
                                      self.l3Value.get(), self.l4Value.get())
        if not error[0]:
            self.convLine['xLineEnd'] = error[1]
            self.convLine['yLineEnd'] = error[2]
            self.convLine['gcodeLine'] = error[3]
        else:
            error_set(self, f'{error[1]}\n')
            return
    elif self.lineCombo.get() == _('ARC 3P'):
        error = LINE.do_arc_3_points(self, self.l1Value.get(), self.l2Value.get(), \
                                     self.l3Value.get(), self.l4Value.get(), \
                                     self.l5Value.get(), self.l6Value.get())
        if not error[0]:
            self.convLine['xLineEnd'] = error[1]
            self.convLine['yLineEnd'] = error[2]
            self.convLine['gcodeLine'] = error[3]
        else:
            error_set(self, f'{error[1]}\n')
            return
    elif self.lineCombo.get() == _('ARC 2P +RADIUS'):
        arcType = '3' if 'CCW' in self.g23Arc.cget('text') else '2'
        error = LINE.do_arc_2_points_radius(self, self.l1Value.get(), self.l2Value.get(), self.l3Value.get(), \
                                                  self.l4Value.get(), self.l5Value.get(), arcType)
        if not error[0]:
            self.convLine['xLineEnd'] = error[1]
            self.convLine['yLineEnd'] = error[2]
            self.convLine['gcodeLine'] = error[3]
        else:
            error_set(self, f'{error[1]}\n')
            return
    elif self.lineCombo.get() == _('ARC ANGLE +RADIUS'):
        arcType = '3' if 'CCW' in self.g23Arc.cget('text') else '2'
        error = LINE.do_arc_by_angle_radius(self, self.l1Value.get(), self.l2Value.get(), self.l3Value.get(),
                                                  self.l4Value.get(), self.l5Value.get(), arcType)
        if not error[0]:
            self.convLine['xLineEnd'] = error[1]
            self.convLine['yLineEnd'] = error[2]
            self.convLine['gcodeLine'] = error[3]
        else:
            error_set(self, f'{error[1]}\n')
            return
    if self.convLine['addSegment'] == 1:
        LINE.next_segment(self.fTmp, self.fNgc)
    else:
        valid, self.convLine['xLineStart'] = self.conv_is_float(self.l1Value.get())
        valid, self.convLine['yLineStart'] = self.conv_is_float(self.l2Value.get())
        LINE.first_segment(self.fTmp, self.fNgc, self.fNgcBkp, self.preAmble, \
                           self.lineCombo.get(), self.convLine['xLineStart'], self.convLine['yLineStart'], \
                           int(self.matCombo.get().split(':')[0]), \
                           self.matCombo.get().split(':')[1].strip())
    LINE.last_segment(self.fTmp, self.fNgc, self.convLine['gcodeLine'], self.postAmble)
    self.file_loader(self.fNgc, True, False)
    self.addC.configure(state = 'normal')
    self.undoC.configure(state = 'normal')
    self.preview_button_pressed(True)
    if self.convLine['addSegment'] == 1:
        self.convLine['addSegment'] = 2
    self.previewActive = True

def auto_preview(self):
    if self.l1Value.get() and self.l2Value.get() and self.l3Value.get() and self.l4Value.get():
        if self.lineCombo.get() == _('LINE POINT ~ POINT') or \
           self.lineCombo.get() == _('LINE BY ANGLE') or \
           (self.lineCombo.get() == _('ARC 3P') and self.l5Value.get() and self.l6Value.get()) or \
           (self.lineCombo.get() == _('ARC 2P +RADIUS') and self.l5Value.get()) or \
           (self.lineCombo.get() == _('ARC ANGLE +RADIUS') and self.l5Value.get()):
            preview(self)

def arc_type_changed(self):
    text = 'CW - G2' if 'CCW' in self.g23Arc.cget('text') else 'CCW - G3'
    self.g23Arc.configure(text = text)
    auto_preview(self)

def line_type_changed(self, text, refresh):
#    self.lineCombo.selection_clear()
    if text == _('LINE POINT ~ POINT'):
        if not refresh:
            set_line_point_to_point(self)
    elif text == _('LINE BY ANGLE'):
        if not refresh:
            set_line_by_angle(self)
    elif text == _('ARC 3P'):
        if not refresh:
            set_arc_3_points(self)
    elif text == _('ARC 2P +RADIUS'):
        if not refresh:
            set_arc_2_points_radius(self)
    elif text == _('ARC ANGLE +RADIUS'):
        if not refresh:
            set_arc_by_angle_radius(self)
    self.l3Entry.focus()

def clear_widgets(self):
    set_start_point(self)
    for w in [self.l3Label, self.l4Label, self.l5Label, self.l6Label, ]:
        w.configure(text = '')
    for w in [self.l3Entry, self.l4Entry, self.l5Entry, self.l6Entry, ]:
        w.grid_remove()
    self.g23Arc.grid_remove()

def set_start_point(self):
    text = _('START')
    self.l1Label.configure(text = _('X START'))
    self.l1Value.set(f'{self.convLine["xLineStart"]:0.3f}')
    self.l2Label.configure(text = _('Y START'))
    self.l2Value.set(f'{self.convLine["yLineStart"]:0.3f}')

def set_line_point_to_point(self):
    clear_widgets(self)
    self.l3Label.configure(text = _('X END'))
    self.l4Label.configure(text = _('Y END'))
    for w in [self.l3Value, self.l4Value]:
        w.set('')
    self.l3Entry.grid(column=1, row=4, pady=(3))
    self.l4Entry.grid(column=1, row=5, pady=3)

def set_line_by_angle(self):
    clear_widgets(self)
    self.l3Label.configure(text = _('LENGTH'))
    self.l4Label.configure(text = _('ANGLE'))
    self.l4Value.set('0.000')
    for w in [self.l3Value, self.l4Value]:
        w.set('')
    self.l3Entry.grid(column=1, row=4, pady=3)
    self.l4Entry.grid(column=1, row=5, pady=3)

def set_arc_3_points(self):
    clear_widgets(self)
    self.l3Label.configure(text = _('X NEXT'))
    self.l4Label.configure(text = _('Y NEXT'))
    self.l5Label.configure(text = _('X END'))
    self.l6Label.configure(text = _('Y END'))
    for w in [self.l3Value, self.l4Value, self.l5Value, self.l6Value]:
        w.set('')
    self.l3Entry.grid(column=1, row=4, pady=3)
    self.l4Entry.grid(column=1, row=5, pady=3)
    self.l5Entry.grid(column=1, row=6, pady=3)
    self.l6Entry.grid(column=1, row=7, pady=3)

def set_arc_2_points_radius(self):
    clear_widgets(self)
    self.l3Label.configure(text = _('X END'))
    self.l4Label.configure(text = _('Y END'))
    self.l5Label.configure(text = _('RADIUS'))
    self.l5Value.set('0.000')
    self.l6Label.configure(text = _('DIRECTION'))
    for w in [self.l3Value, self.l4Value, self.l5Value]:
        w.set('')
    self.l3Entry.grid(column=1, row=4, pady=3)
    self.l4Entry.grid(column=1, row=5, pady=3)
    self.l5Entry.grid(column=1, row=6, pady=3)
    self.g23Arc.grid(column=1, row=7, pady=3)

def set_arc_by_angle_radius(self):
    clear_widgets(self)
    self.l3Label.configure(text = _('LENGTH'))
    self.l4Label.configure(text = _('ANGLE'))
    self.l4Value.set('0.000')
    self.l5Label.configure(text = _('RADIUS'))
    self.l6Label.configure(text = _('DIRECTION'))
    for w in [self.l3Value, self.l4Value, self.l5Value]:
        w.set('')
    self.l3Entry.grid(column=1, row=4, pady=3)
    self.l4Entry.grid(column=1, row=5, pady=3)
    self.l5Entry.grid(column=1, row=6, pady=3)
    self.g23Arc.grid(column=1, row=7, pady=3)

def error_set(self, error):
    self.dialog_show_ok(_('Line Error'), error)

def widgets(self):
    if self.parent.comp['development']:
        reload(LINE)
    # start settings
    self.previewActive = False
    if not self.settingsExited:
        self.dValue.set('')
        self.convLine['xLineStart'] = 0.0
        self.convLine['yLineStart'] = 0.0
        self.convLine['addSegment'] = 0
        self.convLine['gcodeSave'] = ''
    self.dLabel.configure(text = _('DIAMETER'))
    #connections
    self.previewC.configure(command = lambda:preview(self))
    self.g23Arc.configure(command = lambda:arc_type_changed(self))
    self.lineCombo.configure(command = lambda v:line_type_changed(self, v, False))
    #add to layout
    self.matLabel.grid(column=0, row=0, padx=3, pady=3, sticky='e')
    self.matCombo.grid(column=1, row=0, padx=3, pady=3, columnspan=3, sticky='ew')
    self.lnLabel.grid(column=0, row=1, padx=3, pady=3, sticky='e')
    self.lineCombo.grid(column=1, row=1, padx=3, pady=3, columnspan=2, sticky='ew')
    self.l1Label.grid(column=0, row=2, padx=3, pady=3, sticky='e')
    self.l1Entry.grid(column=1, row=2, padx=3, pady=3, sticky='w')
    self.l2Label.grid(column=0, row=3, padx=3, pady=3, sticky='e')
    self.l2Entry.grid(column=1, row=3, padx=3, pady=3, sticky='w')
    self.l3Label.grid(column=0, row=4, padx=3, pady=3, sticky='e')
    self.l3Entry.grid(column=1, row=4, padx=3, pady=3, sticky='w')
    self.l4Label.grid(column=0, row=5, padx=3, pady=3, sticky='e')
    self.l4Entry.grid(column=1, row=5, padx=3, pady=3, sticky='w')
    self.l5Label.grid(column=0, row=6, padx=3, pady=3, sticky='e')
    self.l5Entry.grid(column=1, row=6, padx=3, pady=3, sticky='w')
    self.l6Label.grid(column=0, row=7, padx=3, pady=3, sticky='e')
    self.l6Entry.grid(column=1, row=7, padx=3, pady=3, sticky='w')
    # finish setup
    if not self.settingsExited:
        line_type_changed(self, self.lineCombo.get(), False)
    self.settingsExited = False
