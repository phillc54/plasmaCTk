#!/bin/python3

import os
import sys
import gcode
import math
import customtkinter as ctk
from customtkinter import filedialog
from CTkMessagebox import CTkMessagebox
import tkinter as tk
from shutil import copy
from importlib import reload
from PIL import Image

import time

APPDIR = os.path.dirname(os.path.realpath(__file__))
TMPPATH = '/tmp/plasmactk'
IMGPATH = os.path.join(APPDIR, 'images')
if not os.path.isdir(TMPPATH):
    os.mkdir(TMPPATH)

class Conversational():
    def __init__(self, parent, unitsPerMm, materials, matNum, standalone=False):
        super().__init__()
        print('conversational is initialized')
        self.parent = parent
        self.convFirstRun = True
        self.rE = parent.tk.eval

        self.unitsPerMm = unitsPerMm

        self.materials = materials
        self.matIndex = matNum
        self.standalone = standalone
#        self.initialdir = os.path.expanduser('~/linuxcnc/nc_files')
        self.initialdir = os.path.expanduser('~/linuxcnc/nc_files/plasmac')
        self.existingFile = None
        self.mytags = ['mytags']
#        print(f"self.unitsPerMm:{self.unitsPerMm}   self.standalone={self.standalone}")
#        self.materials = materialFileDict
#        self.matIndex = matIndex


##        parent.convTools = toolFrame
##        parent.convInput = convFrame
 #       self.unitsPerMm = 1#        self.unitsPerMm = unitsPerMm
#        self.prefs = prefs
#        self.getPrefs = getprefs
#        self.putPrefs = putprefs
##        self.comp = comp
#        self.file_loader = file_loader
#        self.wcs_rotation = wcs_rotation
#        self.pVars = pVars
#        self.conv_toggle = conv_toggle
#        self.o = o
        self.shapeLen = {'x':None, 'y':None}
#        self.combobox = combobox
        self.fTmp = os.path.join(TMPPATH, 'temp.ngc')
        self.fNgc = os.path.join(TMPPATH, 'shape.ngc')
        self.fNgcBkp = os.path.join(TMPPATH, 'backup.ngc')
        self.fNgcSent = os.path.join(TMPPATH, 'sent_shape.ngc')
        self.filteredBkp = os.path.join(TMPPATH, 'filtered_bkp.ngc')
        self.savedSettings = {'start_pos':None, 'cut_type':None, 'lead_in':None, 'lead_out':None}
        self.buttonState = {'newC':False, 'saveC':False, 'sendC':False, 'settingsC':False}
        self.convButton = 'line'
        self.oldConvButton = 'line'
        self.module = None
        self.oldModule = None
        self.convLine = {}
#FIXME - different for standalone vs normal
        if self.unitsPerMm == 1:
            smallHole = 32
            leadin = 5
            preAmble = 'G21\nG64P0.25'
        else:
            smallHole = 1.25
            leadin = 0.2
            preAmble = 'G20\nG64P0.01'
        self.preAmble = f"{preAmble}\nG40\nG49\nG80\nG90\nG92.1\nG94\nG97"
        self.xOrigin = 0.000
        self.yOrigin = 0.000
        self.showRapids = False
        self.rapidArrowLen = 5
        self.zoomLimits = ()
        if not self.convFirstRun and self.parent.comp['development']:
            reload(CONVSET)
        else:
            CONVSET.load(self, self.preAmble, leadin, smallHole, self.preAmble)
        if self.convFirstRun or self.parent.comp['development']:
            self.create_toolbar_widgets()
            self.create_input_widgets()
            self.create_preview_widgets()
            self.show_common_widgets()
#            color_change()
        self.polyCombo.configure(values=[_('CIRCUMSCRIBED'), _('INSCRIBED'), _('SIDE LENGTH')])
        self.lineCombo.configure(values=[_('LINE POINT ~ POINT'), _('LINE BY ANGLE'), _('ARC 3P'),\
                               _('ARC 2P +RADIUS'), _('ARC ANGLE +RADIUS')])
        self.addC.configure(command = self.add_shape_to_file)
        self.loadC.configure(command = self.load_file)
        self.undoC.configure(command = self.undo_shape)
        self.newC.configure(command = lambda: self.new_pressed(True))
        self.saveC.configure(command = self.save_pressed)
        self.settingsC.configure(command = self.settings_pressed)
        self.sendC.configure(command = self.send_pressed)
        for entry in self.entries:
            #entry.bind('<KeyRelease>', self.auto_preview) # plays havoc with good error detection
            #entry.bind('<Return>', self.auto_preview, add='+')
            #entry.bind('<KP_Enter>', self.auto_preview, add='+')
            entry.bind('<Return>', self.preview, add='+')
            entry.bind('<KP_Enter>', self.preview, add='+')
        for entry in self.buttons: entry.bind('<space>', self.button_key_pressed)
        self.entry_validation()
        self.canon = Canon()
        parameter = os.path.join(TMPPATH, 'parameters')
        self.canon.parameter_file = parameter
#        print(f"self.canon.line={self.canon.line}")
        self.convFirstRun = False

#    def start(self, materialFileDict, matIndex, existingFile, g5xIndex):
    def start(self):
        self.buttonOnColor = self.spButton.cget('hover_color')
        self.buttonOffColor = self.spButton.cget('fg_color')
#        print(dir(self.parent.convPreview))
#        self.bgColor = self.parent.convPreview.cget('bg_color')
#        print(self.bgColor)
        self.g5xIndex = 1 # do we need this without a real preview ???

#        self.metric = metric
#        print(f"self.metric:{self.metric}   matIndex:{matIndex}   materialFileDict:{materialFileDict}")
#        print(self.unitsPerMm)
#        print(self.materials[1]['name'])
#        print(self.matIndex)



        # sDiff = 40 + int(self.pVars.fontSize.get()) - 7
        # for i in range(len(self.convShapes)):
        #     self.toolButton[i]['width'] = sDiff
        #     self.toolButton[i]['height'] = sDiff
        # self.materials = materialFileDict
        # self.matIndex = matIndex
#        self.existingFile = existingFile
#        self.g5xIndex = g5xIndex
        self.previewActive = False
        self.settingsExited = False
        self.validShape = False
        self.invalidLeads = 0
        self.ocEntry.configure(state = 'disabled')
        self.undoC.configure(text = _('RELOAD'))
        self.addC.configure(state = 'disabled')
        self.loadC.configure(state = 'normal')
        self.newC.configure(state = 'normal')
        self.saveC.configure(state = 'disabled')
        self.sendC.configure(state = 'disabled')
        self.settingsC.configure(state = 'normal')
        self.polyCombo.set(self.polyCombo.cget('values')[0])
        self.lineCombo.set(self.lineCombo.cget('values')[0])
        self.convLine = {}
        self.convBlock = [False, False]
        values = []
        for m in self.materials:
            values.append(f"{m}:{self.materials[m]['name']}")
            self.matCombo.configure(values=values)
        self.matCombo.set(values[self.matIndex])
        self.convButton = self.oldConvButton
        self.shape_request(self.oldConvButton)
        # if self.existingFile:
        #     if 'shape.ngc' not in self.existingFile:
        #         copy(self.filteredBkp, self.fNgc)
        #         copy(self.filteredBkp, self.fNgcBkp)
        # else:
        #     self.new_pressed(False)
        #     self.l3Entry.focus()
        self.new_pressed(False)
        self.l3Entry.focus()

    def rgb_to_hex(self, r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"

    def file_loader(self, file, a, b):
        print(f"file_loader   file{file}   a:{a}   b:{b}")
        self.plot(file)

    def load_file(self):
        filetypes = [('G-Code Files', '*.ngc *.nc *.tap'), ('All Files', '*.*')]
        file = None
        file = filedialog.askopenfile(initialdir=self.initialdir, filetypes=filetypes)
        if file:
            self.initialdir = os.path.dirname(file.name)

            copy(file.name, self.fNgc)
            copy(file.name, self.fNgcBkp)
            self.existingFile = file.name
            self.plot(file.name)

    def plot(self, filename, title=True):
        if len(self.parent.convPreview.winfo_children()) > 1:
            self.canvas.destroy()
        self.canvas = ctk.CTkCanvas(self.parent.convPreview, bg=self.bgColor[1])#, highlightthickness=0)
        self.canvas.grid(row=0, column=1, padx=3, pady=3, sticky='nsew')
        # if we are in stand-alone mode we need to make a
        # temp file because we cannot use named parameters
        if self.standalone:
            file = os.path.join(TMPPATH, 'stand-alone.tmp')
            with open(filename, 'r') as inFile:
                with open(file, 'w') as outFile:
                    for line in inFile:
                        line = line.replace('#<_hal[plasmac.cut-feed-rate]>', '1')
                        line = line.replace('#<_ini[axis_z]max_limit>', '1')
                        outFile.write(line)
            name = f"{os.path.basename(file)} from {os.path.basename(filename)}"
        else:
            file = filename
            name = os.path.basename(filename)
        if not title:
            name = ''
        # parse the gcode file
        unitcode = 'G21 G49'
        initcode = 'G21 G40 G49 G80 G90 G92.1 G94 G97 M52P1'
        self.canon.__init__()
        result, seq = gcode.parse(file, self.canon, unitcode, initcode)
        if result > gcode.MIN_ERROR:
            print(f"\nG-code error in line {seq - 1}:\n{gcode.strerror(result)}")
            return
        print(f"\nPLOT {filename}")
        count = 0
        for point in self.canon.points:
            pass
        #     shape = None
        #     linestyle = ':' if point['shape'] == 'rapid' else '-'
        #     color = '#c0c0c0'
            if point['shape'] == 'arc': # arcs
                count += 1
                self.canvas.create_arc(point['x1'],
                                       point['y1'],
                                       point['x2'],
                                       point['y2'],
                                       start=point['startAngle'],
                                       extent=point['extent'],
                                       width=1,
                                       outline='gray90',
                                       style='arc')
#                if (point['extent'] > 190 and point['extent'] < 359) or (point['extent'] < -190 and point['extent'] > -359):
#                if (point['extent'] > 190) or (point['extent'] < -190):
#                    print(f"BAD {count}: self.canvas.create_arc({point['x1']:.2f}, {point['y1']:.2f}, {point['x2']:.2f}, {point['y2']:.2f}, start={point['startAngle']:.2f}, extent={point['extent']:.2f}, style='arc', width=1, outline='cyan')")
            elif point['shape'] == 'line': # lines
                self.canvas.create_line(point['points'],
                                        fill='gray90')
            elif point['shape'] == 'rapid' and self.showRapids:
                self.canvas.create_line(point['points'],
                                        fill='gray60')
        self.parent.update()
        if self.canon.points:# or 1:
            canvasWidth = int(self.canvas.winfo_width())
            canvasHeight = int(self.canvas.winfo_height())
#            print(f"\ncanvas W:{canvasWidth}   H:{canvasHeight}")
            x1, y1, x2, y2 = self.canvas.bbox('all')
            viewWidth = x2 - x1
            viewHeight = y2 - y1
#            print(f"bbox org X1{x1}   Y1{y1}   X2{x2}   Y2{y2}   W:{viewWidth}   H:{viewHeight}")
            xScale = round(canvasWidth / viewWidth, 2)
            yScale = round(canvasHeight / viewHeight, 2)
            scale = min(xScale, yScale) * 0.95
#            print(f"scalex:{xScale:.4f}   scaley:{yScale:.4f}   scale  {scale:.4f}")
            diffX = (canvasWidth - viewWidth) / 2
            diffY = (canvasHeight - viewHeight) / 2
#            print(f"diffx:{diffX}   diffY:{diffY}")
            mX = -x1 + diffX
            mY = (-y1 + diffY)# * scale
#            print(f"moveX {mX}     moveY {mY}")
            self.canvas.move('all', mX, mY)
            self.scale_canvas(scale)

    def scale_canvas(self, scale):
        self.canvas.scale('all', 0, 0, scale, scale)
        canvasWidth = int(self.canvas.winfo_width())
        canvasHeight = int(self.canvas.winfo_height())
        x1, y1, x2, y2 = self.canvas.bbox('all')
        viewWidth = x2 - x1
        viewHeight = y2 - y1
#        print(f"bbox scaled X1{x1}   Y1{y1}   X2{x2}   Y2{y2}   W:{viewWidth}   H:{viewHeight}")
        diffX = (canvasWidth - viewWidth) / 2
        diffY = (canvasHeight - viewHeight) / 2
#        print(f"diffx:{diffX}   diffY:{diffY}")
        mX = -x1 + diffX
        mY = (-y1 + diffY)
#        print(f"moveX {mX}     moveY {mY}")
        self.canvas.move('all', mX, mY)

    def entry_validation(self):
        self.vcmd = (self.parent.register(self.validate_entries))
        for w in self.uInts:
            w.configure(validate='key', validatecommand=(self.vcmd, 'int', '%P', '%W'))
        for w in self.sFloats:
            w.configure(validate='key', validatecommand=(self.vcmd, 'flt', '%P', '%W'))
        for w in self.uFloats:
            w.configure(validate='key', validatecommand=(self.vcmd, 'pos', '%P', '%W'))

    def validate_entries(self, style, value, widget):
        widget = self.parent.nametowidget(widget)
        # determine the type of circle
        if self.convButton == 'circle' and (widget == self.dEntry or widget == self.shEntry):
            circleType = 'circle'
        elif self.convButton == 'boltcircle' and (widget == self.hdEntry or widget == self.shEntry):
            circleType = 'boltcircle'
        else:
            circleType = None
        # blank is valid
        if value == '':
            if circleType:
                self.circle_check(circleType, value)
            return True
        # period in a int is invalid and more than one period is invalid
        if ('.' in value and style == 'int') or value.count('.') > 1:
            return False
        # a negative in a posfloat or int is invalid and more than one negative is invalid
        if ('-' in value and (style == 'pos' or style == 'int')) or value.count('-') > 1:
            return False
        # cannot do math on "-", ".", or "-." but they are valid
        if value == '.' or value == '-' or value == '-.':
            if circleType:
                self.circle_check(circleType, value)
            return True
        # if a float cannot be calculated from value then it is invalid
        try:
            v = float(value)
        except:
            return False
        # must be a valid value
        if circleType:
            self.circle_check(circleType, value)
        return True

    def preview(self, event):
#        # this stops focus moving to the root when return pressed
#        self.rE(f"after 5 focus {event.widget}")
        self.module.preview(self)

    def auto_preview(self, event):
        # this stops focus moving to the root when return pressed
#        self.rE(f"after 5 focus {event.widget}")
        # we have no interest in this list of keys
        if event.keysym in ['Tab']:
            return
        # not enough info for an auto_preview yet
        if event.widget.get() in ['.','-','-.']:
            print('return due to . - -.')
            return
        # if auto preview is valid
        if self.previewC.cget('state') == 'normal' and self.convButton != 'settings':
            self.module.auto_preview(self)

    def button_key_pressed(self, event):
        # dummy function for:
        # press a button widget via the keyboard spacebar
        pass

    def circle_check(self, circleType, dia):
        self.invalidLeads = 0
        try:
            dia = float(dia)
        except:
            dia = 0
        # cannot do overcut if large hole, no hole, or external circle
        if dia >= self.smallHoleDia or dia == 0 or (self.ctButton.cget('text') == _('EXTERNAL') and circleType == 'circle'):
            self.ocButton.configure(text = _('OFF'))
            self.ocButton.configure(state = 'disabled')
            self.ocEntry.configure(state = 'disabled')
        else:
            self.ocButton.configure(state = 'normal')
            self.ocEntry.configure(state = 'normal')
        # cannot do leadout if small hole
        if self.ctButton.cget('text') == _('INTERNAL') or circleType == 'boltcircle':
            if dia < self.smallHoleDia:
                self.loLabel.configure(state = 'disabled')
                self.loEntry.configure(state = 'disabled')
                self.invalidLeads = 2
            else:
            # test for large leadin or leadout
                try:
                    lIn = float(self.liValue.get())
                except:
                    lIn = 0
                try:
                    lOut = float(self.loValue.get())
                except:
                    lOut = 0
                if lIn and lIn > dia / 4:
                    self.loLabel.configure(state = 'disabled')
                    self.loEntry.configure(state = 'disabled')
                    self.invalidLeads = 2
                elif lOut and lOut > dia / 4:
                    self.loLabel.configure(state = 'disabled')
                    self.invalidLeads = 1
                else:
                    self.loLabel.configure(state = 'normal')
                    self.loEntry.configure(state = 'normal')
                    self.invalidLeads = 0
        else:
            self.loLabel.configure(state = 'normal')
            self.loEntry.configure(state = 'normal')
            self.invalidLeads = 0

    # dialog call from shapes
    def dialog_show_ok(self, title, message):
        return CTkMessagebox(master=self.parent, title=title, message=message, icon='warning').get()

    def new_pressed(self, buttonPressed):
        if buttonPressed and (self.saveC.cget('state') or self.sendC.cget('state') or self.previewActive):
            title = _('Unsaved Shape')
            msg0 = _('You have an unsaved, unsent, or active previewed shape')
            msg1 = _('If you continue it will be deleted')
            message = f"{msg0}\n\n{msg1}\n"
            reply = CTkMessagebox(master=self.parent, title=title, message=message, icon='question', options=['Continue', 'Cancel']).get()
            if reply == 'Cancel':
                return
        if self.oldConvButton == 'line':
            if self.lineCombo.get() == _('LINE POINT ~ POINT'):
                CONVLIN.set_line_point_to_point(self)
            elif self.lineCombo.get() == _('LINE BY ANGLE'):
                CONVLIN.set_line_by_angle(self)
            elif self.lineCombo.get() == _('ARC 3P'):
                CONVLIN.set_arc_3_points(self)
            elif self.lineCombo.get() == _('ARC 2P +RADIUS'):
                CONVLIN.set_arc_2_points_radius(self)
            elif self.lineCombo.get() == _('ARC ANGLE +RADIUS'):
                CONVLIN.set_arc_by_angle_radius(self)
        with open(self.fNgc, 'w') as outNgc:
            outNgc.write('(new conversational file)\nM2\n')
        copy(self.fNgc, self.fTmp)
        copy(self.fNgc, self.fNgcBkp)
        self.plot(self.fNgc, title=False)
        self.saveC.configure(state = 'disabled')
        self.sendC.configure(state = 'disabled')
        self.validShape = False
        self.convLine['xLineStart'] = self.convLine['xLineEnd'] = 0
        self.convLine['yLineStart'] = self.convLine['yLineEnd'] = 0
        self.coValue.set('')
        self.roValue.set('')
        self.preview_button_pressed(False)

    def save_pressed(self):
#        self.parent.convInput.unbind_all('<KeyRelease>')
#        self.parent.convInput.unbind_all('<Return>')
        title = _('Save Error')
        with open(self.fNgc, 'r') as inFile:
            for line in inFile:
                if '(new conversational file)' in line:
                    message = _('An empty file cannot be saved')
                    CTkMessagebox(master=self.parent, title=title, message=message, icon='warning')
                    return
#        self.vkb_show() if we add a virtual keyboard ??????????????????????????
        filetypes = [('G-Code Files', '*.ngc *.nc *.tap'), ('All Files', '*.*')]
        defaultextension = '.ngc'
        file = None
        file = filedialog.asksaveasfilename(filetypes=filetypes, defaultextension=defaultextension)
        if file:
             print(file)
             copy(self.fNgc, file)
             self.saveC.configure(state = 'disabled')
#        self.vkb_show(True) if we add a virtual keyboard ??????????????????????
        for entry in self.entries:
            #entry.bind('<KeyRelease>', self.auto_preview) # plays havoc with good error detection
            #entry.bind('<Return>', self.auto_preview, add='+')
            #entry.bind('<KP_Enter>', self.auto_preview, add='+')
            entry.bind('<Return>', self.preview, add='+')
            entry.bind('<KP_Enter>', self.preview, add='+')

    def settings_pressed(self):
        self.savedSettings['lead_in'] = self.liValue.get()
        self.savedSettings['lead_out'] = self.loValue.get()
        self.savedSettings['start_pos'] = self.spButton.cget('text')
        self.savedSettings['cut_type'] = self.ctButton.cget('text')
        self.buttonState['newC'] = self.newC.cget('state')
        self.buttonState['sendC'] = self.sendC.cget('state')
        self.buttonState['saveC'] = self.saveC.cget('state')
        self.buttonState['settingsC'] = self.settingsC.cget('state')
        self.newC.configure(state = 'disabled')
        self.sendC.configure(state = 'disabled')
        self.saveC.configure(state = 'disabled')
        self.settingsC.configure(state = 'disabled')
        self.clear_widgets()
        if self.parent.comp['development']:
            reload(CONVSET)
        for child in self.parent.convTools.winfo_children():
            if child.winfo_class() == 'Radiobutton':
                child.configure(state = 'disabled')
        CONVSET.widgets(self)
        CONVSET.show(self)

    def send_pressed(self):
        copy(self.fNgc, self.fNgcSent)
        #copy(self.fNgc, self.filteredBkp)
        self.existingFile = self.fNgc
        self.saveC.configure(state = 'disabled')
        self.sendC.configure(state = 'disabled')
#FIXME we need to load the file in linuxcnc here
        print(f"we need to load the file in linuxcnc here {self.fNgc}")
        #self.file_loader(self.fNgc, False, False)
#        self.conv_toggle(0, True)

    def block_request(self):
#       may need to add this halpin for wcs rotation on abort etc.
#       self.convBlockLoaded = self.h.newpin('CONVBLO_loaded', hal.HAL_BIT, hal.HAL_IN)
        if not self.settingsExited:
            if self.previewActive and self.active_shape():
                return True
            title = _('Array Error')
            with open(self.fNgc) as inFile:
                for line in inFile:
                    if '(new conversational file)' in line:
                        message = _('An empty file cannot be arrayed, rotated, or scaled')
                        CTkMessagebox(master=self.parent, title=title, message=message, icon='warning')
                        return True
                    # see if we can do something about NURBS blocks down the track
                    elif 'g5.2' in line.lower() or 'g5.3' in line.lower():
                        message = _('Cannot scale a GCode NURBS block')
                        CTkMessagebox(master=self.parent, title=title, message=message, icon='warning')
                        return True
                    elif 'M3' in line or 'm3' in line:
                        break
        return

    def shape_request(self, shape): #, material):
#        print(f"shape_request={shape}")#   {self.toolButton[self.convShapes.index(shape)].cget('text')}")
#            self.toolButton[self.convShapes.index(self.oldConvButton)].select()
        if shape == 'closer':
            if self.standalone:
                title = 'Close'
                message = 'Do you wish to close this stand-alone conversational session'
                reply = CTkMessagebox(master=self.parent, title=title, message=message, icon='question', options=['Yes', 'No']).get()
                if reply == 'Yes':
                    sys.exit()
            else:
                print('WE NEED TO SHOW THE MAIN TAB HERE')
            return
        if not self.settingsExited:
            if self.previewActive and self.active_shape():
                return
            self.preview_button_pressed(False)
        self.oldModule = self.module
        if shape == 'block':
            # if self.o.canon is not None:
            #     unitsMultiplier = 25.4 if self.unitsPerMm == 1 else 1
            #     self.shapeLen['x'] = (self.o.canon.max_extents[0] - self.o.canon.min_extents[0]) * unitsMultiplier
            #     self.shapeLen['y'] = (self.o.canon.max_extents[1] - self.o.canon.min_extents[1]) * unitsMultiplier
            self.module = CONVBLO
            if self.block_request():
                self.toolButton[self.convShapes.index(self.oldConvButton)].invoke()
                return
        elif shape == 'line': self.module = CONVLIN
        elif shape == 'circle': self.module = CONVCIR
        elif shape == 'ellipse': self.module = CONVELL
        elif shape == 'triangle': self.module = CONVTRI
        elif shape == 'rectangle': self.module = CONVREC
        elif shape == 'polygon': self.module = CONVPOL
        elif shape == 'boltcircle': self.module = CONVBOL
        elif shape == 'slot': self.module = CONVSLO
        elif shape == 'star': self.module = CONVSTA
        elif shape == 'gusset': self.module = CONVGUS
        elif shape == 'sector': self.module = CONVSEC
        else: return
        if self.parent.comp['development']:
            reload(self.module)
        self.oldConvButton = self.convButton
        self.convButton = shape
        self.toolButton[self.convShapes.index(self.oldConvButton)].configure(state='enabled', fg_color=self.buttonOffColor)
        self.toolButton[self.convShapes.index(self.convButton)].configure(state='disabled', fg_color=self.buttonOnColor)
        self.settingsC.configure(state = 'normal')
        self.previewC.configure(state = 'normal')
        self.loLabel.configure(state = 'normal')
        self.loEntry.configure(state = 'normal')
        if self.validShape:
            self.undoC.configure(state = 'normal')
        self.addC.configure(state = 'disabled')
        self.clear_widgets()
        self.ocButton.configure(fg_color = self.bBackColor)#relief='raised', bg=self.bBackColor)
        if self.settingsExited:
            self.liValue.set(self.savedSettings['lead_in'])
            self.loValue.set(self.savedSettings['lead_out'])
            self.spButton.configure(text = self.savedSettings['start_pos'])
            self.ctButton.configure(text = self.savedSettings['cut_type'])
        else:
            self.ctButton.configure(text = _('EXTERNAL'))
            if self.origin:
                self.spButton.configure(text = _('CENTER'))
            else:
                self.spButton.configure(text = _('BTM LEFT'))
            self.liValue.set(f"{self.leadIn}")
            self.loValue.set(f"{self.leadOut}")
        self.module.widgets(self)
        self.settingsExited = False

    def preview_button_pressed(self, state):
        self.previewActive = state
        if state:
            self.saveC.configure(state = 'disabled')
            self.sendC.configure(state = 'disabled')
            self.undoC.configure(text = _('UNDO'))
        else:
            if self.validShape:
                self.saveC.configure(state = 'normal')
                self.sendC.configure(state = 'normal')
            self.undoC.configure(text=_('RELOAD'))
            self.addC.configure(state = 'disabled')

    def active_shape(self):
        title = _('Active Preview')
        message = _('Cannot continue with an active previewed shape')
        reply = CTkMessagebox(master=self.parent, title=title, message=message, icon='warning').get()
        self.module = self.oldModule
        return reply

    def restore_buttons(self):
        self.newC.configure(state = self.buttonState['newC'])
        self.sendC.configure(state = self.buttonState['sendC'])
        self.saveC.configure(state = self.buttonState['saveC'])
        self.settingsC.configure(state = self.buttonState['settingsC'])

    def conv_is_float(self, entry):
        try:
            return True, float(entry)
        except:
            reply = -1 if entry else 0
            return False, reply

    def conv_is_int(self, entry):
        try:
            return True, int(entry)
        except:
            reply = -1 if entry else 0
            return False, reply

    def undo_shape(self):
        if not self.previewActive:
            title = _('Reload Request')
            if self.existingFile:
                name = os.path.basename(self.existingFile)
                msg0 = _('The original file will be loaded')
                msg1 = _('If you continue all changes will be deleted')
                message = f"{msg0}:\n\n{name}\n\n{msg1}\n"
                reply = CTkMessagebox(master=self.parent, title=title, message=message, icon='question', options=['Continue', 'Cancel']).get()
                if reply == 'Cancel':
                    return(True)
            else:
                msg0 = _('An empty file will be loaded')
                msg1 = _('If you continue all changes will be deleted')
                message = f"{msg0}\n\n{msg1}\n"
                reply = CTkMessagebox(master=self.parent, title=title, message=message, icon='question', options=['Continue', 'Cancel']).get()
                if reply == 'Cancel':
                    return(True)
            if self.existingFile:
                copy(self.existingFile, self.fNgcBkp)
                self.plot(self.existingFile)
            else:
                with open(self.fNgcBkp, 'w') as outNgc:
                    outNgc.write('(new conversational file)\nM2\n')
            self.validShape = False
            self.previewC.configure(state = 'normal')
            self.undoC.configure(state = 'disabled')
            self.saveC.configure(state = 'disabled')
            self.sendC.configure(state = 'disabled')
        if self.convButton == 'line':
            if self.previewActive:
                if self.convLine['addSegment'] > 1:
                    self.convLine['addSegment'] = 1
                self.module.line_type_changed(self, self.lineCombo.get(), True)
            else:
                self.convLine['addSegment'] = 0
                self.module.line_type_changed(self, self.lineCombo.get(),False)
            if self.undoC.cget('text') == _('RELOAD'):
                self.convLine['xLineStart'] = 0.000
                self.convLine['yLineStart'] = 0.000
                self.l1Value.set('0.000')
                self.l2Value.set('0.000')
            self.convLine['xLineEnd'] = self.convLine['xLineStart']
            self.convLine['yLineEnd'] = self.convLine['yLineStart']
            if len(self.convLine['gcodeSave']):
                self.convLine['gcodeLine'] = self.convLine['gcodeSave']
            self.previewActive = False
        # undo the shape
        if os.path.exists(self.fNgcBkp):
            copy(self.fNgcBkp, self.fNgc)
            self.plot(self.fNgc)
            self.addC.configure(state = 'disabled')
            if not self.validShape:
                self.undoC.configure(state = 'disabled')
            if not self.convBlock[1]:
                self.convBlock[0] = False
            self.preview_button_pressed(False)

    def add_shape_to_file(self):
        copy(self.fNgc, self.fNgcBkp)
        self.validShape = True
        self.addC.configure(state = 'disabled')
        self.saveC.configure(state = 'normal')
        self.sendC.configure(state = 'normal')
        self.preview_button_pressed(False)
        if self.convButton == 'line':
            self.convLine['convAddSegment'] = self.convLine['gcodeLine']
            self.convLine['xLineStart'] = self.convLine['xLineEnd']
            self.convLine['yLineStart'] = self.convLine['yLineEnd']
            self.l1Value.set(f"{self.convLine['xLineEnd']:0.3f}")
            self.l2Value.set(f"{self.convLine['yLineEnd']:0.3f}")
            self.convLine['addSegment'] = 1
            self.module.line_type_changed(self, self.lineCombo.get(), True)
            self.addC.configure(state = 'disabled')
            self.previewActive = False

    def clear_widgets(self):
#        print('clear_widgets')
        for child in self.parent.convInput.winfo_children():
            if not self.settingsExited and isinstance(child, tk.Entry):
                if child.winfo_name() == str(getattr(self, 'liEntry')).rsplit('.',1)[1]:
                    pass
                elif child.winfo_name() == str(getattr(self, 'loEntry')).rsplit('.',1)[1]:
                    pass
                elif child.winfo_name() == str(getattr(self, 'liEntry')).rsplit('.',1)[1]:
                    pass
                elif child.winfo_name() == str(getattr(self, 'liEntry')).rsplit('.',1)[1]:
                    pass
                elif child.winfo_name() == str(getattr(self, 'caEntry')).rsplit('.',1)[1]:
                    self.caValue.set('360')
                elif child.winfo_name() == str(getattr(self, 'cnEntry')).rsplit('.',1)[1]:
                    self.cnValue.set('1')
                elif child.winfo_name() == str(getattr(self, 'rnEntry')).rsplit('.',1)[1]:
                    self.rnValue.set('1')
                elif child.winfo_name() == str(getattr(self, 'scEntry')).rsplit('.',1)[1]:
                    self.scValue.set('1.0')
                elif child.winfo_name() == str(getattr(self, 'ocEntry')).rsplit('.',1)[1]:
                    self.ocValue.set(f"{4 * self.unitsPerMm}")
            child.grid_remove()
        self.show_common_widgets()

    def cut_type_clicked(self, circle=False):
        if self.ctButton.cget('text') == _('EXTERNAL'):
            self.ctButton.configure(text = _('INTERNAL'))
        else:
            self.ctButton.configure(text = _('EXTERNAL'))
        if circle:
            try:
                dia = float(self.dValue.get())
            except:
                dia = 0
            if dia >= self.smallHoleDia or dia == 0 or self.ctButton.cget('text') == _('EXTERNAL'):
                self.ocButton.configure(state = 'disabled')#, relief='raised', bg=self.bBackColor)
                self.ocEntry.configure(state = 'disabled')
            else:
                self.ocButton.configure(state = 'normal')
                self.ocEntry.configure(state = 'normal')
        self.module.auto_preview(self)

    def start_point_clicked(self):
        if self.spButton.cget('text') == _('BTM LEFT'):
            self.spButton.configure(text = _('CENTER'))
        else:
            self.spButton.configure(text = _('BTM LEFT'))
        self.module.auto_preview(self)

    def material_changed(self, material):
        self.module.auto_preview(self)

    def pan_left(self):
        xMin,xMax = self.ax.get_xlim()
        pan = (xMax - xMin) /10
        self.ax.set_xlim(xMin - pan, xMax - pan)
        self.canvas.draw()

    def pan_right(self):
        xMin,xMax = self.ax.get_xlim()
        pan = (xMax - xMin) /10
        self.ax.set_xlim(xMin + pan, xMax + pan)
        self.canvas.draw()

    def pan_up(self):
        yMin,yMax = self.ax.get_ylim()
        pan = (yMax - yMin) / 10
        self.ax.set_ylim(yMin + pan, yMax + pan)
        self.canvas.draw()

    def pan_down(self):
        yMin,yMax = self.ax.get_ylim()
        pan = (yMax - yMin) / 10
        self.ax.set_ylim(yMin - pan, yMax - pan)
        self.canvas.draw()

    def zoom_in(self):
        x = (self.zoomLimits[0][1] - self.zoomLimits[0][0]) / 10
        y = (self.zoomLimits[1][1] - self.zoomLimits[1][0]) / 10
        xMin = self.ax.get_xlim()[0] + x
        xMax = self.ax.get_xlim()[1] - x
        yMin = self.ax.get_ylim()[0] + y
        yMax = self.ax.get_ylim()[1] - y
        if xMin > xMax or yMin > yMax:
# FIXME - delete when scaling done
#                print(f"\nLIMIT   X({self.ax.get_xlim()[0]:7.2f}, {self.ax.get_xlim()[1]:7.2f})   Y({self.ax.get_ylim()[0]:7.2f}, {self.ax.get_ylim()[1]:7.2f})")
#                print(f"\n  BAD   X({xMin:7.2f}, {xMax:7.2f})   Y({yMin:7.2f}, {yMax:7.2f})")
            x = self.ax.get_xlim()[1] - self.ax.get_xlim()[0]
            y = self.ax.get_ylim()[1] - self.ax.get_ylim()[0]
# FIXME - delete when scaling done
#                print(f"X:{x}   Y:{y}")
            if x < 100 or y < 100:
                return
            xMid = self.ax.get_xlim()[0] + (x / 2)
            yMid = self.ax.get_ylim()[0] + (y / 2)
# FIXME - delete when scaling done
#                print(f"xMid:{xMid}   yMid:{yMid}")
#FIXME - this needs scaling
            if x > y:
                xLen = 50 * (x / y)
                yLen = 50
            else:
                xLen = 50 * (y / x)
                yLen = 50
            xMin = xMid - xLen
            xMax = xMid + xLen
            yMin = yMid - yLen
            yMax = yMid + yLen
# FIXME - delete when scaling done
#                print(f"xMin:{xMin}   xMax:{xMax}   yMin:{yMin}   yMax:{yMax}")
        self.ax.set_xlim(xMin, xMax)
        self.ax.set_ylim(yMin, yMax)
        self.canvas.draw()

    def zoom_out(self):
        x = (self.zoomLimits[0][1] - self.zoomLimits[0][0]) / 10
        y = (self.zoomLimits[1][1] - self.zoomLimits[1][0]) / 10
        self.ax.set_xlim(self.ax.get_xlim()[0] - x, self.ax.get_xlim()[1] + x)
        self.ax.set_ylim(self.ax.get_ylim()[0] - y, self.ax.get_ylim()[1] + y)
        self.canvas.draw()

    def zoom_all(self):
        self.ax.set_xlim(self.zoomLimits[0])
        self.ax.set_ylim(self.zoomLimits[1])
        self.canvas.draw()

    def show_common_widgets(self):
        self.spacer.grid(column=0, row=11, sticky='ns')
        self.previewC.grid(column=0, row=12, padx=3, pady=3)
        if self.standalone:
            self.loadC.grid(column=1, row=12, padx=3, pady=3)
            self.addC.grid(column=2, row=12, padx=3, pady=3)
        else:
            self.addC.grid(column=1, row=12, columnspan=2, pady=3)
        self.undoC.grid(column=3, row=12, padx=3, pady=3)
        self.sepline.grid(column=0, row=13, columnspan=4, sticky='ew', padx=8, pady=3)
        self.newC.grid(column=0, row=14, padx=3, pady=3)
        self.saveC.grid(column=1, row=14, padx=3, pady=3)
        self.settingsC.grid(column=2, row=14, padx=3, pady=3)
        self.sendC.grid(column=3, row=14, padx=3, pady=3)

    def create_toolbar_widgets(self):
        for s in self.parent.convTools.pack_slaves():
            s.destroy()
        self.convShapes = ['line','circle','ellipse','triangle','rectangle','polygon', \
                           'boltcircle','slot','star','gusset','sector','block','closer']
        self.convSizes = [(36, 36), (36, 36), (36, 20), (36, 36), (36, 36), (36, 36), \
                          (36, 36), (36, 20), (36, 36), (36, 36), (36, 36), (36, 36), (36, 36)]
        self.toolButton = []
        # toolbar buttons
        for i in range(len(self.convShapes)):
            image = ctk.CTkImage(light_image = Image.open(os.path.join(IMGPATH, f"{self.convShapes[i]}.png")), size = self.convSizes[i])
            self.toolButton.append(ctk.CTkButton(self.parent.convTools, text='', width=40, height=40, image=image, \
                                                 command=lambda i=i: self.shape_request(self.convShapes[i])))
            self.toolButton[i].grid(row=0, column=[i], padx=3, pady=3, sticky='ns')

    def create_input_widgets(self):
        for s in self.parent.convInput.grid_slaves():
            s.destroy()
        width = 80 # width of label, entry, and button widgets
        widthM = 252 # width of material selector
        self.matLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('MATERIAL'))
        self.matCombo = ctk.CTkComboBox(self.parent.convInput, width=widthM, justify='left', border_width=1, command=self.material_changed)
        self.spLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('START'))
        self.spButton = ctk.CTkButton(self.parent.convInput, width=width)
        self.ctLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('CUT TYPE'))
        self.ctButton = ctk.CTkButton(self.parent.convInput, width=width)
        self.xsLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('X ORIGIN'))
        self.xsValue = tk.StringVar(value='0')
        self.xsEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.xsValue)
        self.ysLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('Y ORIGIN'))
        self.ysValue = tk.StringVar(value='0')
        self.ysEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.ysValue)
        self.liLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('LEAD IN'))
        self.liValue = tk.StringVar()
        self.liEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.liValue)
        self.loLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('LEAD OUT'))
        self.loValue = tk.StringVar()
        self.loEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.loValue)
        self.polyLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('TYPE'))
        self.polyCombo = ctk.CTkComboBox(self.parent.convInput, justify='left', border_width=1)
        self.sLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('SIDES'))
        self.sValue = tk.StringVar()
        self.sEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.sValue)
        self.dLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('DIAMETER'))
        self.dValue = tk.StringVar()
        self.dEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.dValue)
        self.lLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('LENGTH'))
        self.lValue = tk.StringVar()
        self.lEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.lValue)
        self.wLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('WIDTH'))
        self.wValue = tk.StringVar()
        self.wEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.wValue)
        self.hLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('HEIGHT'))
        self.hValue = tk.StringVar()
        self.aaLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('A ANGLE'))
        self.aaValue = tk.StringVar()
        self.aaEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.aaValue)
        self.alLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('a LENGTH'))
        self.alValue = tk.StringVar()
        self.alEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.alValue)
        self.baLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('B ANGLE'))
        self.baValue = tk.StringVar()
        self.baEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.baValue)
        self.blLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('b LENGTH'))
        self.blValue = tk.StringVar()
        self.blEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.blValue)
        self.caLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('C ANGLE'))
        self.caValue = tk.StringVar()
        self.caEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.caValue)
        self.clLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('c LENGTH'))
        self.clValue = tk.StringVar()
        self.clEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.clValue)
        self.hEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.hValue)
        self.hdLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('HOLE DIA'))
        self.hdValue = tk.StringVar()
        self.hdEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.hdValue)
        self.hoLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('# HOLES'))
        self.hoValue = tk.StringVar()
        self.hoEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.hoValue)
        self.bcaLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('CIRCLE ANG'))
        self.bcaValue = tk.StringVar()
        self.bcaEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.bcaValue)
        self.ocLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('OVERCUT'))
        self.ocValue = tk.StringVar()
        self.ocEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.ocValue)
        self.ocButton = ctk.CTkButton(self.parent.convInput, width=width, text=_('OFF'))
        self.pLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('POINTS'))
        self.pValue = tk.StringVar()
        self.pEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.pValue)
        self.odLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('OUTER DIA'))
        self.odValue = tk.StringVar()
        self.odEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.odValue)
        self.idLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('INNER DIA'))
        self.idValue = tk.StringVar()
        self.idEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.idValue)
        self.rLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('RADIUS'))
        self.rButton = ctk.CTkButton(self.parent.convInput, width=width, text=_('RADIUS'))
        self.rValue = tk.StringVar()
        self.rEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.rValue)
        self.saLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('SEC ANGLE'))
        self.saValue = tk.StringVar(value='0')
        self.saEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.saValue)
        self.aLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('ANGLE'))
        self.aValue = tk.StringVar(value='0')
        self.aEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.aValue)
        self.r1Button = ctk.CTkButton(self.parent.convInput, width=width)
        self.r1Value = tk.StringVar()
        self.r1Entry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.r1Value)
        self.r2Button = ctk.CTkButton(self.parent.convInput, width=width)
        self.r2Value = tk.StringVar()
        self.r2Entry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.r2Value)
        self.r3Button = ctk.CTkButton(self.parent.convInput, width=width)
        self.r3Value = tk.StringVar()
        self.r3Entry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.r3Value)
        self.r4Button = ctk.CTkButton(self.parent.convInput, width=width)
        self.r4Value = tk.StringVar()
        self.r4Entry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.r4Value)
        # block
        self.ccLabel = ctk.CTkLabel(self.parent.convInput, width=width, text=_('COLUMNS'))
        self.cnLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('NUMBER'))
        self.cnValue = tk.StringVar(value='1')
        self.cnEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.cnValue)
        self.coLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('OFFSET'))
        self.coValue = tk.StringVar(value='0')
        self.coEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.coValue)
        self.rrLabel = ctk.CTkLabel(self.parent.convInput, width=width, text=_('ROWS'))
        self.rnLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('NUMBER'))
        self.rnValue = tk.StringVar(value='1')
        self.rnEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.rnValue)
        self.roLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('OFFSET'))
        self.roValue = tk.StringVar(value='0')
        self.roEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.roValue)
        self.bsLabel = ctk.CTkLabel(self.parent.convInput, width=width, text=_('SHAPE'))
        self.scLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('SCALE'))
        self.scValue = tk.StringVar(value='1')
        self.scEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.scValue)
        self.rtLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('ROTATION'))
        self.rtValue = tk.StringVar(value='0')
        self.rtEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.rtValue)
        self.mirror = ctk.CTkButton(self.parent.convInput, width=width, text=_('MIRROR'))
        self.flip = ctk.CTkButton(self.parent.convInput, width=width, text=_('FLIP'))
        self.oLabel = ctk.CTkLabel(self.parent.convInput, width=width, text=_('ORIGIN OFFSET'))
        # lines and arcs
        self.lnLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('TYPE'))
        self.lineCombo = ctk.CTkComboBox(self.parent.convInput, justify='left', border_width=1)
        self.l1Label = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text='')
        self.l1Value = tk.StringVar()
        self.l1Entry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.l1Value)
        self.l2Label = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text='')
        self.l2Value = tk.StringVar()
        self.l2Entry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.l2Value)
        self.l3Label = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text='')
        self.l3Value = tk.StringVar()
        self.l3Entry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.l3Value)
        self.l4Label = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text='')
        self.l4Value = tk.StringVar()
        self.l4Entry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.l4Value)
        self.l5Label = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text='')
        self.l5Value = tk.StringVar()
        self.l5Entry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.l5Value)
        self.l6Label = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text='')
        self.l6Value = tk.StringVar()
        self.l6Entry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.l6Value)
        self.g23Arc = ctk.CTkButton(self.parent.convInput, width=width, text='CW - G2')
        # settings
        self.preLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('PREAMBLE'))
        self.preValue = tk.StringVar()
        self.preEntry = ctk.CTkEntry(self.parent.convInput, width=width, border_width=1, textvariable=self.preValue)
        self.pstLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('POSTAMBLE'))
        self.pstValue = tk.StringVar()
        self.pstEntry = ctk.CTkEntry(self.parent.convInput, width=width, border_width=1, textvariable=self.pstValue)
        self.llLabel = ctk.CTkLabel(self.parent.convInput, width=width, text=_('LEAD LENGTHS'))
        self.shLabel = ctk.CTkLabel(self.parent.convInput, width=width, text=_('SMALL HOLES'))
        self.shValue = tk.StringVar()
        self.shEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.shValue)
        self.hsValue = tk.StringVar()
        self.hsEntry = ctk.CTkEntry(self.parent.convInput, width=width, justify='right', border_width=1, textvariable=self.hsValue)
        self.hsLabel = ctk.CTkLabel(self.parent.convInput, width=width, anchor='e', text=_('SPEED %'))
        self.pvLabel = ctk.CTkLabel(self.parent.convInput, width=width, text=_('PREVIEW'))
        self.saveS = ctk.CTkButton(self.parent.convInput, width=width, text=_('SAVE'))
        self.reloadS = ctk.CTkButton(self.parent.convInput, width=width, text=_('RELOAD'))
        self.exitS = ctk.CTkButton(self.parent.convInput, width=width, text=_('EXIT'))
        # bottom
        self.previewC = ctk.CTkButton(self.parent.convInput, width=width, text=_('PREVIEW'))
        self.addC = ctk.CTkButton(self.parent.convInput, width=width, text=_('ADD'))
        self.loadC = ctk.CTkButton(self.parent.convInput, width=width, text=_('LOAD'))
        self.undoC = ctk.CTkButton(self.parent.convInput, width=width, text=_('UNDO'))
        self.newC = ctk.CTkButton(self.parent.convInput, width=width, text=_('NEW'))
        self.saveC = ctk.CTkButton(self.parent.convInput, width=width, text=_('SAVE'))
        self.settingsC = ctk.CTkButton(self.parent.convInput, width=width, text=_('SETTINGS'))
        self.sendC = ctk.CTkButton(self.parent.convInput, width=width, text=_('SEND'))
        # spacer and separator
        self.spacer = ctk.CTkLabel(self.parent.convInput, text='')
        self.sepline = ctk.CTkFrame(self.parent.convInput, width = 120, height = 2, fg_color = '#808080')
        # get default background color
        self.bBackColor = self.sendC.cget('fg_color')
        # create lists of entries
        self.uInts   = [self.hoEntry, self.sEntry, self.pEntry, self.cnEntry, self.rnEntry]
        self.sFloats = [self.xsEntry, self.ysEntry, self.aEntry, self.caEntry, \
                        self.coEntry, self.roEntry, self.rtEntry]
        self.uFloats = [self.liEntry, self.loEntry, self.dEntry, self.ocEntry, self.hdEntry, \
                        self.wEntry, self.rEntry, self.saEntry, self.hEntry, self.r1Entry, \
                        self.r2Entry, self.r3Entry, self.r4Entry, self.lEntry, self.odEntry, \
                        self.idEntry, self.aaEntry, self.baEntry, self.caEntry, self.alEntry, \
                        self.blEntry, self.clEntry, self.scEntry, self.shEntry, self.hsEntry, \
                        self.l1Entry, self.l2Entry, self.l3Entry, self.l4Entry, self.l5Entry, \
                        self.l6Entry, ]
        self.entries   = []
        for entry in self.uInts: self.entries.append(entry)
        for entry in self.sFloats: self.entries.append(entry)
        for entry in self.uFloats: self.entries.append(entry)
        self.buttons   = [self.spButton, self.ctButton, self.ocButton, self.rButton, self.r1Button, \
                          self.r2Button, self.r3Button, self.r4Button, self.mirror, self.flip, \
                          self.g23Arc, self.saveS, self.reloadS, self.exitS, self.previewC, self.addC, \
                          self.loadC, self.undoC, self.newC, self.saveC, self.settingsC, self.sendC]
#FIXME - takefocus not applicable for ctk
        # for button in self.buttons:
        #     print(f"button: {button._name}")
        #     button.configure(takefocus=0)
        # self.combos = [self.matCombo, self.polyCombo, self.lineCombo]
        # for combo in self.combos:
        #     combo.configure(takefocus=0)

    def create_preview_widgets(self):
        for s in self.parent.convPreview.grid_slaves():
            s.destroy()
# PLOTTER WIDGETS
        previewButtons = ctk.CTkFrame(self.parent.convPreview, fg_color='transparent', width=20)
        self.bgColor = previewButtons.cget('bg_color')
        previewButtons.grid(row=0, column=0, padx=3, pady=3, sticky='nsew')
        previewButtons.grid_rowconfigure((0, 10), weight=1)
        zoomIn = ctk.CTkButton(master = previewButtons, text = '+', command = self.zoom_in, width=40, height=40, font=('', 24))
        zoomIn.grid(row=1, column=0, padx=3, pady=3, sticky='ew')
        zoomOut = ctk.CTkButton(master = previewButtons, text = '-', command = self.zoom_out, width=40, height=40, font=('', 24))
        zoomOut.grid(row=2, column=0, padx=3, pady=3, sticky='ew')
        zoomAll = ctk.CTkButton(master = previewButtons, text = '\u25cb', command = self.zoom_all, width=40, height=40, font=('', 24))
        zoomAll.grid(row=4, column=0, padx=3, pady=23, sticky='ew')
        panLeft = ctk.CTkButton(master = previewButtons, text = '\u2190', command = self.pan_left, width=40, height=40, font=('', 24))
        panLeft.grid(row=6, column=0, padx=3, pady=3, sticky='ew')
        panRight = ctk.CTkButton(master = previewButtons, text = '\u2192', command = self.pan_right, width=40, height=40, font=('', 24))
        panRight.grid(row=7, column=0, padx=3, pady=3, sticky='ew')
        panUp = ctk.CTkButton(master = previewButtons, text = '\u2191', command = self.pan_up, width=40, height=40, font=('', 24))
        panUp.grid(row=8, column=0, padx=3, pady=3, sticky='ew')
        panDown = ctk.CTkButton(master = previewButtons, text = '\u2193', command = self.pan_down, width=40, height=40, font=('', 24))
        panDown.grid(row=9, column=0, padx=3, pady=3, sticky='ew')

class Canon:
    ''' use this class instead of glcanon as we are only interested in:
          points:  from arc_feed, straight_feed, and straight_traverse
          offsets: from set_g5x_offset and set_xy_rotation '''

    def __init__(self):
        self.points = []
        self.offsetX = 0.0
        self.offsetY = 0.0
        self.angle = 0.0
        self.g5x_offset = ()

        self.count = 0

    def __getattr__(self, attr):

        def set_units(f):
            #FIXME we need to set units properly here
            if isinstance(f, float):
                return round(f * 25.4, 4)
            return f

        def inner(*args):
            ''' adds shapes to the points list 
                we negate the y axis coordinates to suit the silly tkinter canvas '''
            if attr not in ['arc_feed', 'straight_feed', 'straight_traverse', 'set_g5x_offset', 'set_xy_rotation']:
                return
            # no need to scale angles
            if attr == 'set_xy_rotation':
                self.angle = math.radians(args[0])
                return
            # scale all coordinates
            args = list(map(set_units, args))
            if attr == 'set_g5x_offset':
                self.offsetX = args[1]
                self.offsetY = args[2]
                self.g5x_offset = (self.offsetX, self.offsetY)
                return
            # get origin coordinates
            if len(self.points): # if shape has begun
                if self.points[-1]['shape'] == 'rapid' or self.points[-1]['shape'] == 'line':
                    originX = self.points[-1]['lastX'] + self.offsetX
                    originY = self.points[-1]['lastY'] + self.offsetY
                else:
                    originX = self.points[-1]['lastX'] + self.offsetX
                    originY = self.points[-1]['lastY'] + self.offsetY
            else: # start a new shape
                originX = self.offsetX
                originY = self.offsetY
            # set start coordinates
            startX = round(self.offsetX + ((originX - self.offsetX) * math.cos(self.angle) - (originY - self.offsetY) * math.sin(self.angle)), 4)
            startY = round(self.offsetY + ((originX - self.offsetX) * math.sin(self.angle) + (originY - self.offsetY) * math.cos(self.angle)), 4)
            # set end coordinates
            endX = round(self.offsetX + (args[0] * math.cos(self.angle) - args[1] * math.sin(self.angle)), 4)
            endY = round(self.offsetY + (args[0] * math.sin(self.angle) + args[1] * math.cos(self.angle)), 4)
            if attr == 'arc_feed': # arcs

                self.count += 1

                # set arc parameters
                if len(self.points): # if start point exists
                    # set arc center coordinates
                    centerX = round(self.offsetX + (args[2] * math.cos(self.angle) - args[3] * math.sin(self.angle)), 4)
                    centerY = round(self.offsetY + (args[2] * math.sin(self.angle) + args[3] * math.cos(self.angle)), 4)
                    # set arc radius
                    radius = round(math.sqrt((centerX - endX)**2 + (centerY - endY)**2), 4)
                    dir = 1
                    start = round(math.degrees(math.atan2(startY - centerY, startX - centerX)) * dir, 4)
                    end = round(math.degrees(math.atan2(endY - centerY, endX - centerX)) * dir, 4)
#                    print(f"1:   s:{start} e:{end} d:{dir} a:{args[4]}   sx:{startX} cx:{centerX} ex:{endX}   sy:{startY} cy:{centerY} ey:{endY}   r:{radius}")
                    startAngle = round(start, 4)
                    endAngle = round(end, 4)
                    # we can use an arc to simulate a circle but it cannot be a full 360 degrees
                    extent = endAngle - startAngle if endAngle - startAngle != 0 else 359.99
# FIXME - a wacky and incorrect way to prevent arc being drawn in the reverse direction
#                    if (extent > 190 and extent < 359) or (extent < -190 and extent > -359):
                    if (extent > 190) or (extent < -190):
#                        print(f" BAD{self.count}:   {attr}   {args[:5]}   extent: {extent:.2f}   start{startAngle:.2f}:   end{endAngle:.2f}")
                        if extent < 0:
                            extent = 360 - extent * -1
                        else:
                            startAngle = endAngle
                            extent = 360 - extent
                        #print(f"      new extent: {extent}")
#                        if (extent > 180) or (extent < -180):
#                            print(f" BAD{self.count}:   {attr}   {args[:5]}   extent: {extent:.2f}   start{startAngle:.2f}:   end{endAngle:.2f}")
                    x1 = centerX - radius
                    y1 = (centerY - radius) * -1
                    x2 = centerX + radius
                    y2 = (centerY + radius) * -1
                    # add new arc to points list
                    self.points.append({'shape': 'arc',
                                        'x1': x1,
                                        'y1': y1,
                                        'x2': x2,
                                        'y2': y2,
                                        'startAngle': startAngle,
                                        'extent': extent,
                                        'lastX': args[0],
                                        'lastY': args[1]})
                # arcs cannot start from nowhere
                else:
                    print(f"arc without a previous move: {args}")
            else: # lines and rapids
                shape = 'line' if attr == 'straight_feed' else 'rapid'
                # add point to last line/rapid in  points list
                if len(self.points) and self.points[-1]['shape'] == shape:
                    self.points[-1]['points'].append((endX, -endY))
                    self.points[-1]['lastX'] = args[0]
                    self.points[-1]['lastY'] = args[1]
                    # delete extra rapid points if required
                    if self.points[-1]['shape'] == 'rapid' and len(self.points[-1]['points']) > 2:
                        if self.points[-1]['points'][1] == self.points[-1]['points'][2]:
                            del self.points[-1]['points'][2]
                        elif self.points[-1]['shape'] == 'rapid' and len(self.points[-1]['points']) > 2:
                                if (-self.points[-1]['points'][0][0], self.points[-1]['points'][0][1]) == self.g5x_offset:
                                    del self.points[-1]['points'][1]
                                else:
                                    del self.points[-1]['points'][0]
                # create new line/rapid in points list
                self.points.append({'shape': shape,
                                        'points': [(startX, -startY), (endX, -endY)],
                                        'lastX': args[0],
                                        'lastY': args[1]})
        return inner

    def next_line(self, linecode):
        pass

    ''' these cannot return None '''
    def get_external_length_units(self):
        return 1.0 # dinosaur

    def get_external_angular_units(self):
        return 1.0

    def get_axis_mask(self):
        # return 7 # (x y z)
        return 15 # (x y z a)

    def get_block_delete(self):
        return False

    def get_tool(self, pocket):
        return -1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0


''' ##############################################################################################

    The following allows conversational to run in standalone mode
    If LinuxCNC is run in place it requires:
        a path to the root of the repository
        a path to a material file, if not specified then a single basic material will be allocated
    Options are:
        -i          - Imperial mode, metric is the default
        -l "path"   - Path to root of rip repository eg ~/linuxcnc-dev
        -m "path"   - Path to a material file

'''

class Window(ctk.CTk):
    def __init__(self, metric, materials):
        super().__init__()
        self.geometry("1024x768")
        self.title("Standalone Conversational")
        self.borderColor = '#808080'
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.convTools = ctk.CTkFrame(self, border_width=1, border_color=self.borderColor, height=40)
        self.convTools.grid(row=0, column=0, columnspan=2, padx=1, pady = 1, sticky='nsew')
        self.convInput = ctk.CTkFrame(self, border_width=1, border_color=self.borderColor, width=120)
        self.convInput.grid(row=1, column=0, padx=1, pady = 1, sticky='nsew')
        self.convInput.grid_rowconfigure(10, weight=1)
        self.convPreview = ctk.CTkFrame(self, border_width=1, border_color=self.borderColor)
        self.convPreview.grid(row=1, column=1, padx=1, pady = 1, sticky='nsew')
        self.convPreview.grid_rowconfigure(0, weight=1)
        self.convPreview.grid_columnconfigure(1, weight=1)
        # self.canvasFrame = ctk.CTkFrame(self.convPreview)
        # self.canvasFrame.grid(row=0, column=1, sticky='nsew')
        # self.update()
        # print(f"self          W:{self.winfo_width()}   H:{self.winfo_height()}")
        # print(f"convTools     W:{self.convTools.winfo_width()}   H:{self.convTools.winfo_height()}")
        # print(f"convInput     W:{self.convInput.winfo_width()}   H:{self.convInput.winfo_height()}")
        # print(f"convPreview   W:{self.convPreview.winfo_width()}   H:{self.convPreview.winfo_height()}")
        # print(f"canvasFrame   W:{self.canvasFrame.winfo_width()}   H:{self.canvasFrame.winfo_height()}")


        self.comp = {'development': False}
        matDict = {}
        if materials:
            num, nam, kw = None, None, None
            with open(materials, 'r') as inFile:
                for line in inFile:
                    if line.startswith('[MATERIAL'):
                        num = int(line.split('R_')[1].replace(']', ''))
                        matDict[num] = {}
                    elif line.startswith('NAME'):
                        nam = line.split('=')[1].strip()
                        matDict[num]['name'] = nam
                    elif line.startswith('KERF'):
                        kw = line.split('=')[1].strip()
                        matDict[num]['kerf_width'] = kw
        if metric:
            unitsPerMm = 1
            if not matDict:
                matDict = {1: {'name': 'Material #1', 'kerf_width': 1.0}}
        else:
            unitsPerMm = 0.03937
            if not matDict:
                matDict = {1: {'name': 'Material #1', 'kerf_width': 0.04}}
        matNum = 0
        conv = Conversational(self, unitsPerMm, matDict, matNum, True)
        conv.start()

if __name__ == '__main__':
    error = ''
    metric = True
    materials = None
    args = sys.argv[1:]
    if len(args):
        if '-i' in args:
            metric = False
        if '-m' in args:
            file = args[args.index('-m') + 1] if '-l' != args[-1] else ''
            if os.path.isfile(file):
                materials = file
            else:
                error += f"invalid materials file:      {file}\n"
        if '-l' in args:
            path = args[args.index('-l') + 1] if '-l' != args[-1] else ''
            if os.path.isdir(path):
                sys.path.append(os.path.join(path, 'lib/python'))
            else:
                error += f"invalid linuxcnc repository: {path}\n"
    else: # this is temp to allow easy run from ctrl-r within vscode
        materials = os.path.expanduser('~/linuxcnc/configs/0_qtplasmac_metric/metric_material.cfg')
        sys.path.append(os.path.expanduser('~/git/linuxcnc-dev/lib/python'))
    if error:
        usage  = 'Stand-alone options are:\n'
        usage += '  -i          - Imperial mode, metric is the default\n'
        usage += '  -l "path"   - Path to root of rip repository, e.g. ~/linuxcnc-dev\n'
        usage += '  -m "path"   - Path to a material file, e.g. ~/linuxcnc/configs/plasma/plasma_material.cfg\n\n'
        print(f"\nError:\n{error}\n{usage}")
        sys.exit()
    import conv_settings as CONVSET
    import conv_line as CONVLIN
    import conv_circle as CONVCIR
    import conv_ellipse as CONVELL
    import conv_triangle as CONVTRI
    import conv_rectangle as CONVREC
    import conv_polygon as CONVPOL
    import conv_bolt as CONVBOL
    import conv_slot as CONVSLO
    import conv_star as CONVSTA
    import conv_gusset as CONVGUS
    import conv_sector as CONVSEC
    import conv_block as CONVBLO
    app = Window(metric, materials)
    app.mainloop()
