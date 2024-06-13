#!/bin/python3

import os
import sys
import tempfile
import linuxcnc
import hal
import gcode
import math
import customtkinter as ctk
import tkinter as tk
from tkinter.filedialog import askopenfilename
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from shutil import copy as COPY
from importlib import reload

APPDIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(APPDIR, 'lib'))
print(f"CWD: {os.getcwd()}")
print(f"CFD: {APPDIR}")
#configPath = os.getcwd()
#p2Path = os.path.join(configPath, 'plasmac2')
#if os.path.isdir(os.path.join(p2Path, 'lib')):
#    extHalPins = {}
#    import sys
#    libPath = os.path.join(p2Path, 'lib')
#    sys.path.append(libPath)

import conv_settings as CONVSET
import conv_line as CONVLINE
import conv_circle as CONVCIRC
import conv_ellipse as CONVELLI
import conv_triangle as CONVTRIA
import conv_rectangle as CONVRECT
import conv_polygon as CONVPOLY
import conv_bolt as CONVBOLT
import conv_slot as CONVSLOT
import conv_star as CONVSTAR
import conv_gusset as CONVGUST
import conv_sector as CONVSECT
import conv_block as CONVBLCK


TMPPATH = '/tmp/plasmactk'
IMGPATH = os.path.join(APPDIR, 'lib/images')

INI = os.path.join(os.path.expanduser('~'), 'linuxcnc/configs/0_ctk_metric/metric.ini')

class App(ctk.CTk):
    ''' the application'''
    def __init__(self):
        super().__init__()
        ctk.set_default_color_theme('dark-blue')  # Themes: blue (default), dark-blue, green
        ctk.set_appearance_mode('dark')  # Modes: system (default), light, dark
        self.title('Phill\'s UI Test')
        self.geometry(f'{800}x{600}+{200}+{200}')
        self.after(100, self.periodic)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        try:
            self.comp = hal.component('ctk-ui')
            self.create_hal_pins(self.comp)
            self.comp.ready()
        except:
            pass
#FIXME   this is just for testing purposes and needs to be removed when completed
        try:
            hal.set_p('plasmac.cut-feed-rate', '1')
        except:
            pass

        # self.initialDir = os.path.join(os.path.expanduser('~'), 'linuxcnc/nc_files')
        self.initialDir = os.path.join(os.path.expanduser('~'), 'Downloads/gcode_plot')
        self.borderColor = '#808080'
        self.userButtons = {}
        self.userButtonCodes = {}
        self.showRapids = False
        self.rapidArrowLen = 5
        self.zoomLimits = ()
        self.convFirstRun = True
        self.loadedFile = None
        self.preConvFile = os.path.join(TMPPATH, 'pre_conv.ngc')
        if not os.path.isdir(TMPPATH):
            os.mkdir(TMPPATH)

        # create the gui
        self.create_gui()

        self.mainloop()

##############################################################################
# testing
##############################################################################
    def open_input_dialog_event(self):
        dialog = ctk.CTkInputDialog(text='Type in a number:', title='CTkInputDialog')
#        print('CTkInputDialog:', dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace('%', '')) / 100
        ctk.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print('sidebar_button click')

    def set_tab_state(self, tabview, tab, state):
        ''' set a tab state to either normal or disabled '''
        stat = 'normal' if state else 'disabled'
        tabview._segmented_button._buttons_dict[tab].configure(state = stat)


##############################################################################
# overrides
##############################################################################
    def ovr_feed_changed(self, value):
        self.ovrFeedLbl.configure(text=f'Feed {value:.0f}%')

    def ovr_feed_reset(self, event, default=100):
        self.ovrFeed.set(default)
        self.ovrFeedLbl.configure(text=f'Feed {default:.0f}%')

    def ovr_rapid_changed(self, value):
        self.ovrRapidLbl.configure(text=f'Rapid {value:.0f}%')

    def ovr_rapid_reset(self, event, default=100):
        self.ovrRapid.set(default)
        self.ovrRapidLbl.configure(text=f'Rapid {default:.0f}%')

    def ovr_jog_changed(self, value):
        print(value)
        self.ovrJogLbl.configure(text=f'Jog {value:.0f}%')

    def ovr_jog_reset(self, event, default=100):
        self.ovrJog.set(default)
        self.ovrJogLbl.configure(text=f'Jog {default:.0f}%')


##############################################################################
# main control buttons
##############################################################################

    def run_clicked(self):
        print('Run clicked')

    def stop_clicked(self):
        print('Stop clicked')

    def pause_clicked(self):
        print('Pause clicked')

    def dry_run_clicked(self):
        print('Dry Run clicked')


##############################################################################
# user buttons
##############################################################################


    def torch_enable_clicked(self):
        print('Torch Enable clicked')

    def user_button_setup(self):
        r = 1
        for button in range(21):
            self.userButtons[button] = ctk.CTkButton(self.mainButtonFrame, text = f'User Button {button}', height=40)
            self.userButtons[button].grid(row=r, column=0, padx=2, pady=3, sticky='ew')
            self.userButtonCodes[button] = f'blah {button}'
            self.userButtons[button].bind('<ButtonPress-1>', lambda event: self.user_button_pressed(int(event.widget.cget('text').rsplit(' ', 1)[1])))
            self.userButtons[button].bind('<ButtonRelease-1>', lambda event: self.user_button_released(int(event.widget.cget('text').rsplit(' ', 1)[1])))
            r += 1

    def user_button_pressed(self, button):
        print(f'User Button #{button:0>{2}}  pressed, code is {self.userButtonCodes[button]}')

    def user_button_released(self, button):
        print(f'User Button #{button:0>{2}} released, code is {self.userButtonCodes[button]}')


##############################################################################
# hal pin setup
##############################################################################
    def create_hal_pins(self, component):
        component.newpin("development", hal.HAL_BIT, hal.HAL_IN)
        component.newpin("in", hal.HAL_FLOAT, hal.HAL_IN)
        component.newpin("out", hal.HAL_FLOAT, hal.HAL_OUT)

##############################################################################
# periodic
##############################################################################
    def periodic(self):
        #print('+100mS')

        self.after(100, self.periodic)

##############################################################################
# general
##############################################################################
    def rgb_to_hex(self, r, g, b):
        return f'#{r:02x}{g:02x}{b:02x}'

##############################################################################
# conversational
##############################################################################
    # def get_plot_file(self):
    #     filename = askopenfilename(title = 'File To Plot',
    #                                initialdir = self.initialDir,
    #                                filetypes = (('gcode file', '.ngc .tap .nc'), ('all files', '.*')))
    #     if not filename:
    #         return
    #     self.initialDir = os.path.dirname(filename)
    #     self.plot(filename)

    # def plot(self, filename):
    #     #clear existing plot
    #     self.ax.clear()
    #     # parse the gcode file
    #     unitcode = 'G21'
    #     initcode = 'G21 G40 G49 G80 G90 G92.1 G94 G97 M52P1'
    #     self.canon = Canon()
    #     parameter = tempfile.NamedTemporaryFile()
    #     self.canon.parameter_file = parameter.name
    #     result, seq = gcode.parse(filename, self.canon, unitcode, initcode)
    #     if result > gcode.MIN_ERROR:
    #         self.ax.set_title(f"\nG-code error in line {seq - 1}:\n{gcode.strerror(result)}")
    #         plt.show()
    #         self.canvas.draw()
    #         return
    #     # iterate through the points
    #     for point in self.canon.points:
    #         shape = None
    #         linestyle = ':' if point['shape'] == 'rapid' else '-'
    #         color = '#c0c0c0'
    #         if point['shape'] == 'arc': # arcs
    #             shape = patches.Arc((point['centerX'],
    #                                  point['centerY']),
    #                                  width=point['radius'] * 2,
    #                                  height=point['radius'] * 2,
    #                                  theta1=point['startAngle'],
    #                                  theta2=point['endAngle'],
    #                                  edgecolor=color,
    #                                  facecolor='none',
    #                                  lw=1,
    #                                  linestyle=linestyle)
    #         elif point['shape'] == 'line': # lines
    #             closed = True if point['points'][0] == point['points'][-1] else False
    #             shape = patches.Polygon(point['points'],
    #                                     closed=closed,
    #                                     edgecolor=color,
    #                                     facecolor='none',
    #                                     lw=1,
    #                                     linestyle=linestyle)
    #         elif point['shape'] == 'rapid' and self.showRapids: # rapids
    #             if math.sqrt((point['points'][1][0] - point['points'][0][0]) ** 2 + (point['points'][1][1] - point['points'][0][1]) ** 2) > self.rapidArrowLen * 2:
    #                 closed = True if point['points'][0] == point['points'][-1] else False
    #                 centerX = (point['points'][0][0] + point['points'][1][0]) / 2
    #                 centerY = (point['points'][0][1] + point['points'][1][1]) / 2
    #                 angle = math.atan2(point['points'][1][1] - centerY, point['points'][1][0] - centerX)
    #                 startX = centerX - self.rapidArrowLen / 2 * math.cos(angle)
    #                 startY = centerY - self.rapidArrowLen / 2 * math.sin(angle)
    #                 endX = self.rapidArrowLen * math.cos(angle)
    #                 endY = self.rapidArrowLen * math.sin(angle)
    #                 arrow = patches.FancyArrow(startX, startY,
    #                                         endX, endY,
    #                                         head_width=3,
    #                                         head_length=5,
    #                                         edgecolor=color,
    #                                         facecolor=color,
    #                                         linestyle='-',
    #                                         length_includes_head=True,
    #                                         overhang=1)
    #                 self.ax.add_patch(arrow)
    #             closed = True if point['points'][0] == point['points'][-1] else False
    #             shape = patches.Polygon(point['points'],
    #                                     closed=closed,
    #                                     edgecolor=color,
    #                                     facecolor='none',
    #                                     lw=1,
    #                                     linestyle=linestyle)
    #         # add the new shape
    #         if shape:
    #             self.ax.add_patch(shape)
    #     # plot the shapes
    #     self.ax.plot()
    #     self.ax.set_title(os.path.basename(filename), color='#c0c0c0')
    #     plt.show()
    #     self.canvas.draw()
    #     self.zoomLimits = (self.ax.get_xlim(), self.ax.get_ylim())

##############################################################################
# gui build
##############################################################################
    def create_gui(self):
        self.create_tabs()# = Tabs(self)
        self.create_main_button_frame()
        self.create_main_control_frame()
        self.create_main_1_frame()
        self.create_main_2_frame()
        self.create_main_3_frame()
        self.create_main_4_frame()
        self.create_main_5_frame()
        self.create_conversational_toolbar_frame()
        self.create_conversational_preview_frame()
        self.create_conversational_input_frame()

        ''' CONV = conversational.Conv(convFirstRun, root_window, widgets.toolFrame, \
                   widgets.convFrame, bwidget.ComboBox, imagePath, tmpPath, pVars, \
                   unitsPerMm, comp, PREF, getPrefs, putPrefs, open_file_guts, \
                   wcs_rotation, conv_toggle, color_change, plasmacPopUp, o) '''
#        Conv.create_widgets(self, self)
#        Conv.show_common_widgets(self, self)
        print(f"self.rapidArrowLen 1: {self.rapidArrowLen}")
        self.conv = Conv(self)
        self.convFirstRun = False
#        self.conv.create_widgets()#, self)
#        self.conv.show_common_widgets()#, self)

        self.create_parameters_1_frame()
        self.create_parameters_2_frame()
        self.create_parameters_3_frame()
        self.create_settings_1_frame()
        self.create_settings_2_frame()
        self.create_settings_3_frame()
        self.create_status_1_frame()
        self.create_status_2_frame()
        self.create_status_3_frame()

    def create_tabs(self):
        ''' tabview as the main window '''

        def tab_changed(tab):
            print(f"{tab} is active")

            if tab == 'Conversational':
                materialFileDictTmp = {1: {'name': 'Mat #1', 'kerf_width': 1.1, 'pierce_height': 3.1, 'pierce_delay': 0.0, 'puddle_jump_height': 0, 'puddle_jump_delay': 0.0, 'cut_height': 1.1, 'cut_speed': 4000, 'cut_amps': 41, 'cut_volts': 101, 'pause_at_end': 0.0, 'gas_pressure': 0.0, 'cut_mode': 1}, 2: {'name': 'Mat #2 is the longest by a very long shot', 'kerf_width': 1.2, 'pierce_height': 3.2, 'pierce_delay': 0.0, 'puddle_jump_height': 0, 'puddle_jump_delay': 0.0, 'cut_height': 1.6, 'cut_speed': 2002, 'cut_amps': 42, 'cut_volts': 102, 'pause_at_end': 0.0, 'gas_pressure': 0.0, 'cut_mode': 1}, 3: {'name': 'Mat #3', 'kerf_width': 1.3, 'pierce_height': 3.3, 'pierce_delay': 0.0, 'puddle_jump_height': 0, 'puddle_jump_delay': 0.0, 'cut_height': 1.3, 'cut_speed': 2003, 'cut_amps': 43, 'cut_volts': 103, 'pause_at_end': 0.0, 'gas_pressure': 0.0, 'cut_mode': 1}, 4: {'name': 'Mat #4', 'kerf_width': 1.4, 'pierce_height': 3.4, 'pierce_delay': 0.4, 'puddle_jump_height': 0, 'puddle_jump_delay': 0.0, 'cut_height': 1.4, 'cut_speed': 2004, 'cut_amps': 44, 'cut_volts': 104, 'pause_at_end': 0.0, 'gas_pressure': 0.0, 'cut_mode': 1}, 5: {'name': 'Mat #5', 'kerf_width': 1.5, 'pierce_height': 3.5, 'pierce_delay': 0.0, 'puddle_jump_height': 0, 'puddle_jump_delay': 0.0, 'cut_height': 1.5, 'cut_speed': 2005, 'cut_amps': 45, 'cut_volts': 105, 'pause_at_end': 0.5, 'gas_pressure': 0.0, 'cut_mode': 1}, 6: {'name': 'Mat #6', 'kerf_width': 1.6, 'pierce_height': 3.0, 'pierce_delay': 0.0, 'puddle_jump_height': 0, 'puddle_jump_delay': 0.0, 'cut_height': 1.6, 'cut_speed': 2006, 'cut_amps': 46, 'cut_volts': 106, 'pause_at_end': 0.0, 'gas_pressure': 0.0, 'cut_mode': 1}}
                if self.loadedFile:
                    COPY(self.loadedFile, self.preConvFile)
                #self.conv.start(materialFileDict, matIndex, vars.taskfile.get(), s.g5x_index, commands.set_view_z)
                self.conv.start(materialFileDictTmp, 1)#, vars.taskfile.get(), s.g5x_index, commands.set_view_z)


        self.tabs = ctk.CTkTabview(self, height=1, anchor='sw', command=lambda: tab_changed(self.tabs.get()))
        self.tabs.add('Main')
        self.tabs.tab('Main').grid_rowconfigure((0, 1), weight=1)
        self.tabs.tab('Main').grid_columnconfigure((1, 2, 3), weight=1)
        self.tabs.add('Conversational')
        self.tabs.tab('Conversational').grid_rowconfigure(1, weight=1)
        self.tabs.tab('Conversational').grid_columnconfigure(1, weight=1)
        self.tabs.add('Parameters')
        self.tabs.tab('Parameters').grid_rowconfigure(0, weight=1)
        self.tabs.tab('Parameters').grid_columnconfigure((0, 1, 2), weight=1)
        self.tabs.add('Settings')
        self.tabs.tab('Settings').grid_rowconfigure(0, weight=1)
        self.tabs.tab('Settings').grid_columnconfigure((0, 1, 2), weight=1)
        self.tabs.add('Status')
        self.tabs.tab('Status').grid_rowconfigure(0, weight=1)
        self.tabs.tab('Status').grid_columnconfigure((0, 1, 2), weight=1)
        # large width is a kludge to make buttons appear homogeneous
        for button in self.tabs._segmented_button._buttons_dict:
            self.tabs._segmented_button._buttons_dict[button].configure(width=1000)
        self.tabs.grid(row=1, column=1, padx=0, sticky='nsew')

    def create_main_button_frame(self):
        ''' main tab button frame '''
        self.mainButtons = ctk.CTkFrame(self.tabs.tab('Main'), border_width=1, border_color=self.borderColor, width=146)
        self.mainButtons.grid(row=0, column=0, rowspan=2, padx=1, pady = 1, sticky='nsew')
        self.mainButtons.grid_rowconfigure((1, 2), weight=1)
        self.mainButtonLbl = ctk.CTkLabel(self.mainButtons, text='Button Panel', height=16, anchor='n')#, fg_color='gray', corner_radius=1, height=18, text_color='#404040')
        self.mainButtonLbl.grid(row=0, column=0, padx=4, pady=(1, 0), sticky='new')
        self.mainButtonFrame = ctk.CTkScrollableFrame(self.mainButtons, width=144, fg_color='transparent')
        self.mainButtonFrame.grid(row=1, column=0, rowspan=2, padx=2, pady=(0, 2), sticky='nsew')
        self.torchEnableBtn = ctk.CTkButton(self.mainButtonFrame, text = 'Torch Enable', command=self.torch_enable_clicked, height=40)
        self.torchEnableBtn.grid(row=0, column=0, padx=2, pady=(0, 2), sticky='new')
        self.user_button_setup()

    def create_main_control_frame(self):
        ''' main tab control frame '''
        self.mainControl = ctk.CTkFrame(self.tabs.tab('Main'), border_width=1, border_color=self.borderColor)
        self.mainControl.grid(row=0, column=1, padx=1, pady = 1, sticky='nsew')
        self.mainControl.grid_rowconfigure((1, 2, 3, 4), weight=6)
        self.mainControl.grid_rowconfigure((5, 6, 7), weight=1)
        self.mainControl.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.mainControlLbl = ctk.CTkLabel(self.mainControl, text='Cycle Panel', height=16, anchor='n')#, fg_color='gray', corner_radius=1, height=18, text_color='#404040')
        self.mainControlLbl.grid(row=0, column=0, columnspan=4, padx=4, pady=(1, 0), sticky='new')
        self.cycleStart = ctk.CTkButton(self.mainControl, text='Cycle Start', command = self.run_clicked)
        self.cycleStart.grid(row=1, column=0, rowspan=2, columnspan=2, padx=(3, 1), pady=(3,0), sticky='nsew')
        self.cycleStop = ctk.CTkButton(self.mainControl, text='Cycle Stop', command = self.stop_clicked)
        self.cycleStop.grid(row=1, column=2, rowspan=2, columnspan=2, padx=(1, 3), pady=(3,0), sticky='nsew')
        self.cyclePause = ctk.CTkButton(self.mainControl, text='Cycle Pause', command = self.pause_clicked)
        self.cyclePause.grid(row=3, column=0, rowspan=2, columnspan=2, padx=(3, 1), pady = (3, 0), sticky='nsew')
        self.dryRunBtn = ctk.CTkButton(self.mainControl, text = 'Dry Run', command=self.dry_run_clicked)
        self.dryRunBtn.grid(row=3, column=2, rowspan=2, columnspan=2, padx=(1, 3), pady=(3, 0), sticky='nsew')
        self.ovrFeed = ctk.CTkSlider(self.mainControl, from_=50, to=120, number_of_steps=120-50, command=self.ovr_feed_changed)
        self.ovrFeed.set(100)
        self.ovrFeed.grid(row=5, column=0, columnspan=3, padx=(1, 3), pady=(12, 0), sticky='ew')
        self.ovrFeedLbl = ctk.CTkLabel(self.mainControl, text=f'Feed {self.ovrFeed.get():.0f}%', anchor='e')
        self.ovrFeedLbl.grid(row=5, column=3, padx=(0,2), pady=(12, 0), sticky='ew')
        self.ovrFeedLbl.bind('<ButtonPress-1>', self.ovr_feed_reset)
        self.ovrRapid = ctk.CTkSlider(self.mainControl, from_=50, to=100, number_of_steps=50, command=self.ovr_rapid_changed)
        self.ovrRapid.set(100)
        self.ovrRapid.grid(row=6, column=0, columnspan=3, padx=(1, 3), pady=(12, 0), sticky='ew')
        self.ovrRapidLbl = ctk.CTkLabel(self.mainControl, text=f'Rapid {self.ovrRapid.get():.0f}%', anchor='e')
        self.ovrRapidLbl.grid(row=6, column=3, padx=(0,2), pady=(12, 0), sticky='ew')
        self.ovrRapidLbl.bind('<ButtonPress-1>', self.ovr_rapid_reset)
        self.ovrJog = ctk.CTkSlider(self.mainControl, from_=50, to=100, number_of_steps=50, command=self.ovr_jog_changed)
        self.ovrJog.set(100)
        self.ovrJog.grid(row=7, column=0, columnspan=3, padx=(1, 3), pady=(12, 6), sticky='ew')
        self.ovrJogLbl = ctk.CTkLabel(self.mainControl, text=f'Jog {self.ovrJog.get():.0f}%', anchor='e')
        self.ovrJogLbl.grid(row=7, column=3, padx=(0,2), pady=(12, 6), sticky='ew')
        self.ovrJogLbl.bind('<ButtonPress-1>', self.ovr_jog_reset)

    def create_main_1_frame(self):
        ''' main tab ??? frame '''
        self.main1Frame = ctk.CTkFrame(self.tabs.tab('Main'), border_width=1, border_color=self.borderColor)
        self.main1Frame.grid(row=1, column=1, padx=1, pady = 1, sticky='nsew')

    def create_main_2_frame(self):
        ''' main tab ??? frame '''
        self.main2Frame = ctk.CTkFrame(self.tabs.tab('Main'), border_width=1, border_color=self.borderColor)
        self.main2Frame.grid(row=0, column=2, padx=1, pady = 1, sticky='nsew')

    def create_main_3_frame(self):
        ''' main tab ??? frame '''
        self.main3Frame = ctk.CTkFrame(self.tabs.tab('Main'), border_width=1, border_color=self.borderColor)
        self.main3Frame.grid(row=1, column=2, padx=1, pady = 1, sticky='nsew')

    def create_main_4_frame(self):
        ''' main tab ??? frame '''
        self.main4Frame = ctk.CTkFrame(self.tabs.tab('Main'), border_width=1, border_color=self.borderColor)
        self.main4Frame.grid(row=0, column=3, padx=1, pady = 1, sticky='nsew')

    def create_main_5_frame(self):
        ''' main tab ??? frame '''
        self.main5Frame = ctk.CTkFrame(self.tabs.tab('Main'), border_width=1, border_color=self.borderColor)
        self.main5Frame.grid(row=1, column=3, padx=1, pady = 1, sticky='nsew')

    def create_conversational_toolbar_frame(self):
        ''' conversational button frame '''
        self.convTools = ctk.CTkFrame(self.tabs.tab("Conversational"), border_width=1, border_color=self.borderColor, height=40)
        self.convTools.grid(row=0, column=0, columnspan=2, padx=1, pady = 1, sticky='nsew')

    def create_conversational_input_frame(self):
        ''' conversational input frame '''

        def get_plot_file():
            filename = askopenfilename(title = 'File To Plot',
                                    initialdir = self.initialDir,
                                    filetypes = (('gcode file', '.ngc .tap .nc'), ('all files', '.*')))
            if not filename:
                return
            print(self.initialDir)
            self.initialDir = os.path.dirname(filename)
            self.plot(filename)

        self.convInput = ctk.CTkFrame(self.tabs.tab("Conversational"), border_width=1, border_color=self.borderColor, width=120)
        self.convInput.grid(row=1, column=0, padx=1, pady = 1, sticky='nsew')

        # temp button for loading file into plotter
#        plot_button = ctk.CTkButton(master = self.convInput, text = 'Plot', command = get_plot_file)
#        plot_button.pack(side=tk.TOP, fill=tk.X, expand=True, padx=3, pady=3, anchor=tk.N)

    def create_conversational_preview_frame(self):
        ''' conversational preview frame '''

        def pan_left():
            xMin,xMax = self.ax.get_xlim()
            pan = (xMax - xMin) /10
            self.ax.set_xlim(xMin - pan, xMax - pan)
            self.canvas.draw()

        def pan_right():
            xMin,xMax = self.ax.get_xlim()
            pan = (xMax - xMin) /10
            self.ax.set_xlim(xMin + pan, xMax + pan)
            self.canvas.draw()

        def pan_up():
            yMin,yMax = self.ax.get_ylim()
            pan = (yMax - yMin) / 10
            self.ax.set_ylim(yMin + pan, yMax + pan)
            self.canvas.draw()

        def pan_down():
            yMin,yMax = self.ax.get_ylim()
            pan = (yMax - yMin) / 10
            self.ax.set_ylim(yMin - pan, yMax - pan)
            self.canvas.draw()

        def zoom_in():
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

        def zoom_out():
            x = (self.zoomLimits[0][1] - self.zoomLimits[0][0]) / 10
            y = (self.zoomLimits[1][1] - self.zoomLimits[1][0]) / 10
            self.ax.set_xlim(self.ax.get_xlim()[0] - x, self.ax.get_xlim()[1] + x)
            self.ax.set_ylim(self.ax.get_ylim()[0] - y, self.ax.get_ylim()[1] + y)
            self.canvas.draw()

        def zoom_all():
            self.ax.set_xlim(self.zoomLimits[0])
            self.ax.set_ylim(self.zoomLimits[1])
            self.canvas.draw()

        convPreview = ctk.CTkFrame(self.tabs.tab("Conversational"), border_width=1, border_color=self.borderColor)
        convPreview.grid(row=1, column=1, padx=1, pady = 1, sticky='nsew')
        convPreview.grid_rowconfigure(0, weight=1)
        convPreview.grid_columnconfigure(1, weight=1)
        previewButtons = ctk.CTkFrame(convPreview, fg_color='transparent', width=20)#, border_width=1, border_color=self.borderColor)
        previewButtons.grid(row=0, column=0, padx=3, pady=3, sticky='nsew')
        previewButtons.grid_rowconfigure((0, 10), weight=1)
        zoomIn = ctk.CTkButton(master = previewButtons, text = '+', command = zoom_in, width=40, height=40, font=('', 24))
        zoomIn.grid(row=1, column=0, padx=3, pady=3, sticky='ew')
        zoomOut = ctk.CTkButton(master = previewButtons, text = '-', command = zoom_out, width=40, height=40, font=('', 24))
        zoomOut.grid(row=2, column=0, padx=3, pady=3, sticky='ew')
        zoomAll = ctk.CTkButton(master = previewButtons, text = '\u25cb', command = zoom_all, width=40, height=40, font=('', 24))
        zoomAll.grid(row=4, column=0, padx=3, pady=23, sticky='ew')
        panLeft = ctk.CTkButton(master = previewButtons, text = '\u2190', command = pan_left, width=40, height=40, font=('', 24))
        panLeft.grid(row=6, column=0, padx=3, pady=3, sticky='ew')
        panRight = ctk.CTkButton(master = previewButtons, text = '\u2192', command = pan_right, width=40, height=40, font=('', 24))
        panRight.grid(row=7, column=0, padx=3, pady=3, sticky='ew')
        panUp = ctk.CTkButton(master = previewButtons, text = '\u2191', command = pan_up, width=40, height=40, font=('', 24))
        panUp.grid(row=8, column=0, padx=3, pady=3, sticky='ew')
        panDown = ctk.CTkButton(master = previewButtons, text = '\u2192', command = pan_down, width=40, height=40, font=('', 24))
        panDown.grid(row=9, column=0, padx=3, pady=3, sticky='ew')
        # set style for matplot widgets
        plt.style.use("dark_background")
        # create the matplot toplevel
        fig = plt.Figure(figsize=(1,1))
        fig.set_facecolor(self.rgb_to_hex(33, 33, 33))
        fig.subplots_adjust(bottom=0.06, left=0.08, top=0.95, right=0.99)
        # add the subplot to the figure
        self.ax = fig.add_subplot(111)
        self.ax.set_facecolor(self.rgb_to_hex(33, 33, 33))
        self.ax.axis('equal')
        self.ax.margins(0.05)
        self.ax.use_sticky_edges = False
        self.ax.tick_params(colors=self.rgb_to_hex(233, 233, 233), which='both')
        self.ax.spines['left'].set_color(self.rgb_to_hex(233, 233, 233))
        self.ax.spines['left'].set_lw(1)
        self.ax.spines['bottom'].set_color(self.rgb_to_hex(233, 233, 233))
        self.ax.spines['bottom'].set_lw(1)
        self.ax.spines['top'].set_lw(0)
        self.ax.spines['right'].set_lw(0)
        self.ax.set_title('No File', color='orange')
        # embed the figure into tkinter
        self.canvas = FigureCanvasTkAgg(fig, master=convPreview)
        self.canvas.get_tk_widget().grid(row=0, column=1, padx=3, pady=3, sticky='nsew')
        # render the figure
        self.canvas.draw()
        self.zoomLimits = (self.ax.get_xlim(), self.ax.get_ylim())

    def create_parameters_1_frame(self):
        ''' parameters ??? frame '''
        self.parameters1 = ctk.CTkFrame(self.tabs.tab("Parameters"), border_width=1, border_color=self.borderColor)
        self.parameters1.grid(row=0, column=0, padx=1, pady = 1, sticky='nsew')

    def create_parameters_2_frame(self):
        ''' parameters ??? frame '''
        self.parameters2 = ctk.CTkFrame(self.tabs.tab("Parameters"), border_width=1, border_color=self.borderColor)
        self.parameters2.grid(row=0, column=1, padx=1, pady = 1, sticky='nsew')

    def create_parameters_3_frame(self):
        ''' parameters ??? frame '''
        self.parameters3 = ctk.CTkFrame(self.tabs.tab("Parameters"), border_width=1, border_color=self.borderColor)
        self.parameters3.grid(row=0, column=2, padx=1, pady = 1, sticky='nsew')

    def create_settings_1_frame(self):
        ''' settings ??? frame '''
        self.settings1 = ctk.CTkFrame(self.tabs.tab("Settings"), border_width=1, border_color=self.borderColor)
        self.settings1.grid(row=0, column=0, padx=1, pady = 1, sticky='nsew')

    def create_settings_2_frame(self):
        ''' settings ??? frame '''
        self.settings2 = ctk.CTkFrame(self.tabs.tab("Settings"), border_width=1, border_color=self.borderColor)
        self.settings2.grid(row=0, column=1, padx=1, pady = 1, sticky='nsew')

    def create_settings_3_frame(self):
        ''' settings ??? frame '''
        self.settings3 = ctk.CTkFrame(self.tabs.tab("Settings"), border_width=1, border_color=self.borderColor)
        self.settings3.grid(row=0, column=2, padx=1, pady = 1, sticky='nsew')

    def create_status_1_frame(self):
        ''' status ??? frame '''
        self.status1 = ctk.CTkFrame(self.tabs.tab("Status"), border_width=1, border_color=self.borderColor)
        self.status1.grid(row=0, column=0, padx=1, pady = 1, sticky='nsew')

    def create_status_2_frame(self):
        ''' status ??? frame '''
        self.status2 = ctk.CTkFrame(self.tabs.tab("Status"), border_width=1, border_color=self.borderColor)
        self.status2.grid(row=0, column=1, padx=1, pady = 1, sticky='nsew')

    def create_status_3_frame(self):
        ''' status ??? frame '''
        self.status3 = ctk.CTkFrame(self.tabs.tab("Status"), border_width=1, border_color=self.borderColor)
        self.status3.grid(row=0, column=2, padx=1, pady = 1, sticky='nsew')

#class Conv(tk.Tk):
class Conv():
    # def __init__(self, convFirstRun, root, toolFrame, convFrame, combobox, \
    #              imagePath, tmpPath, pVars, unitsPerMm, comp, prefs, getprefs, \
    #              putprefs, file_loader, wcs_rotation, conv_toggle, color_change, \
    #              plasmacPopUp, o):
    def __init__(self, parent):
        self.parent = parent#        self.r = root '.'
        self.rE = parent.tk.eval#        self.rE = root.tk.eval
##        parent.convTools = toolFrame
##        parent.convInput = convFrame
        self.unitsPerMm = 1#        self.unitsPerMm = unitsPerMm
#        self.prefs = prefs
#        self.getPrefs = getprefs
#        self.putPrefs = putprefs
##        self.comp = comp
#        self.file_loader = file_loader
#        self.wcs_rotation = wcs_rotation
#        self.pVars = pVars
#        self.conv_toggle = conv_toggle
#        self.plasmacPopUp = plasmacPopUp
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
        self.oldConvButton = False
        self.module = None
        self.oldModule = None
        if self.unitsPerMm == 1:
            smallHole = 32
            leadin = 5
            preAmble = 'G21 G64P0.25'
        else:
            smallHole = 1.25
            leadin = 0.2
            preAmble = 'G20 G64P0.01'
        preAmble = f"{preAmble} G40 G49 G80 G90 G92.1 G94 G97"
        self.xOrigin = 0.000
        self.yOrigin = 0.000
        if self.parent.comp['development']:
            reload(CONVSET)
        CONVSET.load(self, preAmble, leadin, smallHole, preAmble)
        if self.parent.convFirstRun or self.parent.comp['development']:
            self.create_widgets()
            self.show_common_widgets()
#            color_change()
        self.polyCombo.configure(values=[_('CIRCUMSCRIBED'), _('INSCRIBED'), _('SIDE LENGTH')])
        self.lineCombo.configure(values=[_('LINE POINT ~ POINT'), _('LINE BY ANGLE'), _('ARC 3P'),\
                               _('ARC 2P +RADIUS'), _('ARC ANGLE +RADIUS')])
        self.addC.configure(command = lambda:self.add_shape_to_file())
        self.undoC.configure(command = lambda:self.undo_shape())
        self.newC.configure(command = lambda:self.new_pressed(True))
        self.saveC.configure(command = lambda:self.save_pressed())
        self.settingsC.configure(command = lambda:self.settings_pressed())
        self.sendC.configure(command = lambda:self.send_pressed())
        for entry in self.entries:
            #entry.bind('<KeyRelease>', self.auto_preview) # plays havoc with good error detection
            #entry.bind('<Return>', self.auto_preview, add='+')
            #entry.bind('<KP_Enter>', self.auto_preview, add='+')
            entry.bind('<Return>', self.preview, add='+')
            entry.bind('<KP_Enter>', self.preview, add='+')
        for entry in self.buttons: entry.bind('<space>', self.button_key_pressed)
        self.entry_validation()

#    def start(self, materialFileDict, matIndex, existingFile, g5xIndex, setViewZ):
    def start(self, materialFileDict, matIndex):
        # sDiff = 40 + int(self.pVars.fontSize.get()) - 7
        # for i in range(len(self.convShapes)):
        #     self.toolButton[i]['width'] = sDiff
        #     self.toolButton[i]['height'] = sDiff
        self.materials = materialFileDict
        self.matIndex = matIndex
#        self.existingFile = existingFile
#        self.g5xIndex = g5xIndex
#        self.setViewZ = setViewZ
        self.previewActive = False
        self.settingsExited = False
        self.validShape = False
        self.invalidLeads = 0
        self.ocEntry.configure(state = 'disabled')
        self.undoC.configure(text = _('RELOAD'))
        self.addC.configure(state = 'disabled')
        self.newC.configure(state = 'normal')
        self.saveC.configure(state = 'disabled')
        self.sendC.configure(state = 'disabled')
        self.settingsC.configure(state = 'normal')
        self.polyCombo.set(self.polyCombo.cget('values')[0])
        self.lineCombo.set(self.lineCombo.cget('values')[0])
        self.convLine = {}
        self.convBlock = [False, False]
        for m in self.materials:
            #values = [str(m) + ': ' + self.materials[m]['name'] for m in self.materials]
            values = [f"{m}:{self.materials[m]['name']}" for m in self.materials]
            self.matCombo.configure(values=values)
        self.matCombo.set(values[matIndex])#        self.matCombo.setvalue(f"@{self.matIndex}")
#        longest = max(values, key=len)
#        tmpLabel = tk.Label(text=longest)
#        self.matCombo['listboxwidth'] = tmpLabel.winfo_reqwidth() + 200
        if self.oldConvButton:
            self.toolButton[self.convShapes.index(self.oldConvButton)].select()
            self.shape_request(self.oldConvButton)
        else:
            self.toolButton[0].select()
            self.shape_request('line')
        # if self.existingFile:
        #     if 'shape.ngc' not in self.existingFile:
        #         COPY(self.filteredBkp, self.fNgc)
        #         COPY(self.filteredBkp, self.fNgcBkp)
        # else:
        #     self.new_pressed(False)
        #     self.l3Entry.focus()
        self.new_pressed(False)
        self.l3Entry.focus()

    def file_loader(self, file, a, b):
        print(f"file_loader   file{file}   a:{a}   b:{b}")
        self.plot(file)

    def plot(self, filename):
        #clear existing plot
        self.parent.ax.clear()
        # parse the gcode file
        unitcode = 'G21'
        initcode = 'G21 G40 G49 G80 G90 G92.1 G94 G97 M52P1'
        self.canon = Canon()
        parameter = tempfile.NamedTemporaryFile()
        self.canon.parameter_file = parameter.name
        result, seq = gcode.parse(filename, self.canon, unitcode, initcode)
        if result > gcode.MIN_ERROR:
            self.parent.ax.set_title(f"\nG-code error in line {seq - 1}:\n{gcode.strerror(result)}")
            plt.show()
            self.parent.canvas.draw()
            return
        # iterate through the points
        for point in self.canon.points:
            shape = None
            linestyle = ':' if point['shape'] == 'rapid' else '-'
            color = '#c0c0c0'
            if point['shape'] == 'arc': # arcs
                shape = patches.Arc((point['centerX'],
                                     point['centerY']),
                                     width=point['radius'] * 2,
                                     height=point['radius'] * 2,
                                     theta1=point['startAngle'],
                                     theta2=point['endAngle'],
                                     edgecolor=color,
                                     facecolor='none',
                                     lw=1,
                                     linestyle=linestyle)
            elif point['shape'] == 'line': # lines
                closed = True if point['points'][0] == point['points'][-1] else False
                shape = patches.Polygon(point['points'],
                                        closed=closed,
                                        edgecolor=color,
                                        facecolor='none',
                                        lw=1,
                                        linestyle=linestyle)
            elif point['shape'] == 'rapid' and self.parent.showRapids: # rapids
                if math.sqrt((point['points'][1][0] - point['points'][0][0]) ** 2 + (point['points'][1][1] - point['points'][0][1]) ** 2) > self.parent.rapidArrowLen * 2:
                    closed = True if point['points'][0] == point['points'][-1] else False
                    centerX = (point['points'][0][0] + point['points'][1][0]) / 2
                    centerY = (point['points'][0][1] + point['points'][1][1]) / 2
                    angle = math.atan2(point['points'][1][1] - centerY, point['points'][1][0] - centerX)
                    startX = centerX - self.parent.rapidArrowLen / 2 * math.cos(angle)
                    startY = centerY - self.parent.rapidArrowLen / 2 * math.sin(angle)
                    endX = self.parent.rapidArrowLen * math.cos(angle)
                    endY = self.parent.rapidArrowLen * math.sin(angle)
                    arrow = patches.FancyArrow(startX, startY,
                                            endX, endY,
                                            head_width=3,
                                            head_length=5,
                                            edgecolor=color,
                                            facecolor=color,
                                            linestyle='-',
                                            length_includes_head=True,
                                            overhang=1)
                    self.parent.ax.add_patch(arrow)
                closed = True if point['points'][0] == point['points'][-1] else False
                shape = patches.Polygon(point['points'],
                                        closed=closed,
                                        edgecolor=color,
                                        facecolor='none',
                                        lw=1,
                                        linestyle=linestyle)
            # add the new shape
            if shape:
                self.parent.ax.add_patch(shape)
        # plot the shapes
        self.parent.ax.plot()
        self.parent.ax.set_title(os.path.basename(filename), color='#c0c0c0')
        plt.show()
        self.parent.canvas.draw()
        self.zoomLimits = (self.parent.ax.get_xlim(), self.parent.ax.get_ylim())

    def entry_validation(self):
#        self.vcmd = (self.r.register(self.validate_entries))
        self.vcmd = (self.parent.register(self.validate_entries))
        for w in self.uInts:
            w.configure(validate='key', validatecommand=(self.vcmd, 'int', '%P', '%W'))
        for w in self.sFloats:
            w.configure(validate='key', validatecommand=(self.vcmd, 'flt', '%P', '%W'))
        for w in self.uFloats:
            w.configure(validate='key', validatecommand=(self.vcmd, 'pos', '%P', '%W'))

    def validate_entries(self, style, value, widget):
#        widget = self.r.nametowidget(widget)
        widget = self.parent.nametowidget(widget)
        # determine the type of circle
        if self.convButton.get() == 'circle' and (widget == self.dEntry or widget == self.shEntry):
            circleType = 'circle'
        elif self.convButton.get() == 'boltcircle' and (widget == self.hdEntry or widget == self.shEntry):
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
        if self.previewC.cget('state') == 'normal' and self.convButton.get() != 'settings':
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
    def dialog_show_ok(self, title, text):
        # reply = self.plasmacPopUp('error', title, text).reply
        # return reply
        print(title, text)

    def new_pressed(self, buttonPressed):
        if buttonPressed and (self.saveC.cget('state') or self.sendC.cget('state') or self.previewActive):
            title = _('Unsaved Shape')
            msg0 = _('You have an unsaved, unsent, or active previewed shape')
            msg1 = _('If you continue it will be deleted')
            # if not self.plasmacPopUp('yesno', title, f"{msg0}\n\n{msg1}\n").reply:
            #     return
            print(title, f"{msg0}\n\n{msg1}\n")
        if self.oldConvButton == 'line':
            if self.lineCombo.get() == _('LINE POINT ~ POINT'):
                CONVLINE.set_line_point_to_point(self)
            elif self.lineCombo.get() == _('LINE BY ANGLE'):
                CONVLINE.set_line_by_angle(self)
            elif self.lineCombo.get() == _('ARC 3P'):
                CONVLINE.set_arc_3_points(self)
            elif self.lineCombo.get() == _('ARC 2P +RADIUS'):
                CONVLINE.set_arc_2_points_radius(self)
            elif self.lineCombo.get() == _('ARC ANGLE +RADIUS'):
                CONVLINE.set_arc_by_angle_radius(self)
        with open(self.fNgc, 'w') as outNgc:
            outNgc.write('(new conversational file)\nM2\n')
        COPY(self.fNgc, self.fTmp)
        COPY(self.fNgc, self.fNgcBkp)
        self.file_loader(self.fNgc, True, False)
        self.saveC.configure(state = 'disabled')
        self.sendC.configure(state = 'disabled')
        self.validShape = False
        self.convLine['xLineStart'] = self.convLine['xLineEnd'] = 0
        self.convLine['yLineStart'] = self.convLine['yLineEnd'] = 0
        self.coValue.set('')
        self.roValue.set('')
        self.preview_button_pressed(False)

    def save_pressed(self):
        self.parent.convInput.unbind_all('<KeyRelease>')
        self.parent.convInput.unbind_all('<Return>')
        title = _('Save Error')
        with open(self.fNgc, 'r') as inFile:
            for line in inFile:
                if '(new conversational file)' in line:
                    msg0 = _('An empty file cannot be saved')
                    # self.plasmacPopUp('error', title, msg0)
                    print(title, msg0)
                    return
#        self.vkb_show() if we add a virtual keyboard ??????????????????????????
        fileTypes = [('G-Code Files', '*.ngc *.nc *.tap'),
                 ('All Files', '*.*')]
        defaultExt = '.ngc'
        file = asksaveasfilename(filetypes=fileTypes, defaultextension=defaultExt)
        if file:
             COPY(self.fNgc, file)
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
        COPY(self.fNgc, self.fNgcSent)
        #COPY(self.fNgc, self.filteredBkp)
        self.existingFile = self.fNgc
        self.saveC.configure(state = 'disabled')
        self.sendC.configure(state = 'disabled')
#FIXME we need to load the file here
        print('we need to load the file here', self.fNgc)
        #self.file_loader(self.fNgc, False, False)
#        self.conv_toggle(0, True)

    def block_request(self):
#       may need to add this halpin for wcs rotation on abort etc.
#       self.convBlockLoaded = self.h.newpin('conv_block_loaded', hal.HAL_BIT, hal.HAL_IN)
        if not self.settingsExited:
            if self.previewActive and self.active_shape():
                return True
            title = _('Array Error')
            with open(self.fNgc) as inFile:
                for line in inFile:
                    if '(new conversational file)' in line:
                        msg0 = _('An empty file cannot be arrayed, rotated, or scaled')
                        # self.plasmacPopUp('error', title, msg0)
                        print(msg0)
#                        return True
                    # see if we can do something about NURBS blocks down the track
                    elif 'g5.2' in line.lower() or 'g5.3' in line.lower():
                        msg0 = _('Cannot scale a GCode NURBS block')
                        # self.plasmacPopUp('error', title, msg0)
                        print(msg0)
                        return True
                    elif 'M3' in line or 'm3' in line:
                        break
        return

    def shape_request(self, shape): #, material):
        if shape == 'closer':
#            self.conv_toggle(0)
            return
        self.oldModule = self.module
        if shape == 'block':
            # if self.o.canon is not None:
            #     unitsMultiplier = 25.4 if self.unitsPerMm == 1 else 1
            #     self.shapeLen['x'] = (self.o.canon.max_extents[0] - self.o.canon.min_extents[0]) * unitsMultiplier
            #     self.shapeLen['y'] = (self.o.canon.max_extents[1] - self.o.canon.min_extents[1]) * unitsMultiplier
            self.module = CONVBLCK
            if self.block_request():
                self.toolButton[self.convShapes.index(self.oldConvButton)].invoke()
                return
        elif shape == 'line': self.module = CONVLINE
        elif shape == 'circle': self.module = CONVCIRC
        elif shape == 'ellipse': self.module = CONVELLI
        elif shape == 'triangle': self.module = CONVTRIA
        elif shape == 'rectangle': self.module = CONVRECT
        elif shape == 'polygon': self.module = CONVPOLY
        elif shape == 'boltcircle': self.module = CONVBOLT
        elif shape == 'slot': self.module = CONVSLOT
        elif shape == 'star': self.module = CONVSTAR
        elif shape == 'gusset': self.module = CONVGUST
        elif shape == 'sector': self.module = CONVSECT
        else: return
        if self.parent.comp['development']:
            reload(self.module)
        if not self.settingsExited:
            if self.previewActive and self.active_shape():
                return
            self.preview_button_pressed(False)
        self.oldConvButton = shape
        self.settingsC.configure(state = 'normal')
        self.previewC.configure(state = 'normal')
        self.loLabel.configure(state = 'normal')
        self.loEntry.configure(state = 'normal')
        if self.validShape:
            self.undoC.configure(state = 'normal')
        self.addC.configure(state = 'disabled')
        self.clear_widgets()
        self.ocButton.configure(fg_color = self.bBackColor)#relief="raised", bg=self.bBackColor)
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
 #       self.setViewZ()

    def active_shape(self):
        for child in self.parent.convTools.winfo_children():
            child.deselect()
        title = _('Active Preview')
        msg0 = _('Cannot continue with an active previewed shape')
        # reply = self.plasmacPopUp('warn', title, f"{msg0}\n").reply
        print(title, msg0)
        reply = None
        if self.oldConvButton:
            self.toolButton[self.convShapes.index(self.oldConvButton)].select()
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
                # if not self.plasmacPopUp('yesno', title, f"{msg0}:\n\n{name}\n\n{msg1}\n").reply:
                #     return(True)
                print(title, f"{msg0}:\n\n{name}\n\n{msg1}\n")
            else:
                msg0 = _('An empty file will be loaded')
                msg1 = _('If you continue all changes will be deleted')
                # if not self.plasmacPopUp('yesno', title, f"{msg0}\n\n{msg1}\n").reply:
                #     return(True)
                print(title, f"{msg0}\n\n{msg1}\n")
            if self.existingFile:
                COPY(self.existingFile, self.fNgcBkp)
            else:
                with open(self.fNgcBkp, 'w') as outNgc:
                    outNgc.write('(new conversational file)\nM2\n')
            self.validShape = False
            self.previewC.configure(state = 'normal')
            self.undoC.configure(state = 'disabled')
            self.saveC.configure(state = 'disabled')
            self.sendC.configure(state = 'disabled')
        if self.convButton.get() == 'line':
            if self.previewActive:
                if self.convLine['addSegment'] > 1:
                    self.convLine['addSegment'] = 1
                self.module.line_type_changed(self, True)
            else:
                self.convLine['addSegment'] = 0
                self.module.line_type_changed(self, False)
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
            COPY(self.fNgcBkp, self.fNgc)
            self.file_loader(self.fNgc, True, False)
            self.addC.configure(state = 'disabled')
            if not self.validShape:
                self.undoC.configure(state = 'disabled')
            if not self.convBlock[1]:
                self.convBlock[0] = False
            self.preview_button_pressed(False)

    def add_shape_to_file(self):
        COPY(self.fNgc, self.fNgcBkp)
        self.validShape = True
        self.addC.configure(state = 'disabled')
        self.saveC.configure(state = 'normal')
        self.sendC.configure(state = 'normal')
        self.preview_button_pressed(False)
        if self.convButton.get() == 'line':
            self.convLine['convAddSegment'] = self.convLine['gcodeLine']
            self.convLine['xLineStart'] = self.convLine['xLineEnd']
            self.convLine['yLineStart'] = self.convLine['yLineEnd']
            self.l1Value.set(f"{self.convLine['xLineEnd']:0.3f}")
            self.l2Value.set(f"{self.convLine['yLineEnd']:0.3f}")
            self.convLine['addSegment'] = 1
            self.module.line_type_changed(self, True)
            self.addC.configure(state = 'disabled')
            self.previewActive = False

    def clear_widgets(self):
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

    def material_changed(self):#, event):
#        self.matCombo.selection_clear()
        self.module.auto_preview(self)

    def show_common_widgets(self):#, parent):
        self.parent.convInput.rowconfigure(10, weight=1)
        self.spacer.grid(column=0, row=11, sticky='ns')
        self.previewC.grid(column=0, row=12, padx=(3,0))
        self.addC.grid(column=1, row=12, columnspan=2)
        self.undoC.grid(column=3, row=12, padx=(0,3))
        self.sepline.grid(column=0, row=13, columnspan=4, sticky='ew', pady=8, padx=8)
        self.newC.grid(column=0, row=14, padx=(3,0), pady=(0,3))
        self.saveC.grid(column=1, row=14, padx=(3,0), pady=(0,3))
        self.settingsC.grid(column=2, row=14, padx=(4,0), pady=(0,3))
        self.sendC.grid(column=3, row=14, padx=(3,3), pady=(0,3))

    def create_widgets(self):#, parent):
        for s in self.parent.convTools.pack_slaves():
            s.destroy()
        for s in self.parent.convInput.grid_slaves():
            s.destroy()
        self.convShapes = ['line','circle','ellipse','triangle','rectangle','polygon',\
                           'boltcircle','slot','star','gusset','sector','block','closer']
        self.convButton = tk.StringVar()
        self.toolButton = []
        self.images = []
        # toolbar buttons
#FIXME - radiobutton may not be the best for ctk
        for i in range(len(self.convShapes)):
            self.toolButton.append(tk.Radiobutton(self.parent.convTools, text=self.convShapes[i], \
                    command=lambda i=i: self.shape_request(self.convShapes[i]), anchor='center', \
                    indicatoron=0, selectcolor='gray60', highlightthickness=0, bd=2, \
                    variable=self.convButton, value=self.convShapes[i], takefocus=0))
            self.images.append(tk.PhotoImage(file = os.path.join(IMGPATH, self.convShapes[i]) + '.png'))
            self.toolButton[i]['image'] = self.images[i]
            self.toolButton[i]['width'] = 40
            self.toolButton[i]['height'] = 40
            if self.convShapes[i] == 'line':
                self.toolButton[i].pack(side='left', padx=(2,0), pady=1)
            elif self.convShapes[i] == 'closer':
                self.toolButton[i].pack(side='right', padx=(0,2), pady=1)
            else:
                self.toolButton[i].pack(side='left', padx=(4,0), pady=1)
        labelLen = 80 # label length
        entryLen = 80 # entry and button length
        self.matLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('MATERIAL'))
        self.matCombo = ctk.CTkComboBox(self.parent.convInput, width=252, justify='left', border_width=1)#, bd=1, editable=False)
#        self.matCombo['modifycmd'] = self.material_changed
        self.spLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('START'))
#        self.spbValue = tk.StringVar()
        self.spButton = ctk.CTkButton(self.parent.convInput, width=entryLen)#, textvariable=self.spbValue)#, padx=1, pady=1)
        self.ctLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('CUT TYPE'))
#        self.ctbValue = tk.StringVar()
        self.ctButton = ctk.CTkButton(self.parent.convInput, width=entryLen)#, textvariable=self.ctbValue)#, padx=1, pady=1)
        self.xsLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('X ORIGIN'))
        self.xsValue = tk.StringVar()
        self.xsEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.xsValue)#bd=1)
        self.ysLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('Y ORIGIN'))
        self.ysValue = tk.StringVar()
        self.ysEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.ysValue)#bd=1)
        self.liLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('LEAD IN'))
        self.liValue = tk.StringVar()
        self.liEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.liValue)#bd=1)
        self.loLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('LEAD OUT'))
        self.loValue = tk.StringVar()
        self.loEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.loValue)#bd=1)
        self.polyLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('TYPE'))
        self.polyCombo = ctk.CTkComboBox(self.parent.convInput, justify='left', border_width=1)#bd=1, editable=False)
        self.sLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('SIDES'))
        self.sValue = tk.StringVar()
        self.sEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.sValue)#bd=1)
        self.dLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('DIAMETER'))
        self.dValue = tk.StringVar()
        self.dEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.dValue)#bd=1)
        self.lLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('LENGTH'))
        self.lValue = tk.StringVar()
        self.lEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.lValue)#bd=1)
        self.wLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('WIDTH'))
        self.wValue = tk.StringVar()
        self.wEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.wValue)#bd=1)
        self.hLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('HEIGHT'))
        self.hValue = tk.StringVar()
        self.aaLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('A ANGLE'))
        self.aaValue = tk.StringVar()
        self.aaEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.aaValue)#bd=1)
        self.alLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('a LENGTH'))
        self.alValue = tk.StringVar()
        self.alEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.alValue)#bd=1)
        self.baLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('B ANGLE'))
        self.baValue = tk.StringVar()
        self.baEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.baValue)#bd=1)
        self.blLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('b LENGTH'))
        self.blValue = tk.StringVar()
        self.blEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.blValue)#bd=1)
        self.caLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('C ANGLE'))
        self.caValue = tk.StringVar()
        self.caEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.caValue)#bd=1)
        self.clLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('c LENGTH'))
        self.clValue = tk.StringVar()
        self.clEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.clValue)#bd=1)
        self.hEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.hValue)#bd=1)
        self.hdLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('HOLE DIA'))
        self.hdValue = tk.StringVar()
        self.hdEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.hdValue)#bd=1)
        self.hoLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('# HOLES'))
        self.hoValue = tk.StringVar()
        self.hoEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.hoValue)#bd=1)
        self.bcaLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('CIRCLE ANG'))
        self.bcaValue = tk.StringVar()
        self.bcaEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.bcaValue)#bd=1)
        self.ocLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('OVERCUT'))
        self.ocValue = tk.StringVar()
        self.ocEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.ocValue)#bd=1)
#        self.ocbValue = tk.StringVar(self.r, _('OFF'))
#        self.ocbValue = tk.StringVar()
        self.ocButton = ctk.CTkButton(self.parent.convInput, width=entryLen, text=_('OFF'))#, textvariable=self.ocbValue)#, padx=1, pady=1)
        self.pLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('POINTS'))
        self.pValue = tk.StringVar()
        self.pEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.pValue)#bd=1)
        self.odLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('OUTER DIA'))
        self.odValue = tk.StringVar()
        self.odEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.odValue)#bd=1)
        self.idLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('INNER DIA'))
        self.idValue = tk.StringVar()
        self.idEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.idValue)#bd=1)

        self.rLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('RADIUS'))
#        self.rbValue = tk.StringVar(self.r, _('RADIUS'))
        self.rbValue = tk.StringVar()
        self.rButton = ctk.CTkButton(self.parent.convInput, width=entryLen, text=_('RADIUS'))#, textvariable=self.rbValue)#, padx=1, pady=1)
        self.rValue = tk.StringVar()
        self.rEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.rValue)#bd=1)

        self.saLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('SEC ANGLE'))
        self.saValue = tk.StringVar()
        self.saEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.saValue)#bd=1)

        self.aLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('ANGLE'))
        self.aValue = tk.StringVar()
        self.aEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.aValue)#bd=1)

#        self.r1bValue = tk.StringVar()
        self.r1Button = ctk.CTkButton(self.parent.convInput, width=entryLen)#, textvariable=self.r1bValue)#, padx=1, pady=1)
        self.r1Value = tk.StringVar()
        self.r1Entry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.r1Value)#bd=1)

#        self.r2bValue = tk.StringVar()
        self.r2Button = ctk.CTkButton(self.parent.convInput, width=entryLen)#, textvariable=self.r2bValue)#, padx=1, pady=1)
        self.r2Value = tk.StringVar()
        self.r2Entry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.r2Value)#bd=1)

#        self.r3bValue = tk.StringVar()
        self.r3Button = ctk.CTkButton(self.parent.convInput, width=entryLen)#, textvariable=self.r3bValue)#, padx=1, pady=1)
        self.r3Value = tk.StringVar()
        self.r3Entry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.r3Value)#bd=1)

#        self.r4bValue = tk.StringVar()
        self.r4Button = ctk.CTkButton(self.parent.convInput, width=entryLen)#, textvariable=self.r4bValue)#, padx=1, pady=1)
        self.r4Value = tk.StringVar()
        self.r4Entry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.r4Value)#bd=1)

        # block
        self.ccLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, text=_('COLUMNS'))
        self.cnLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('NUMBER'))
        self.cnValue = tk.StringVar()
        self.cnEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.cnValue)#bd=1)
        self.coLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('OFFSET'))
        self.coValue = tk.StringVar()
        self.coEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.coValue)#bd=1)

        self.rrLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, text=_('ROWS'))
        self.rnLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('NUMBER'))
        self.rnValue = tk.StringVar()
        self.rnEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.rnValue)#bd=1)
        self.roLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('OFFSET'))
        self.roValue = tk.StringVar()
        self.roEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.roValue)#bd=1)

        self.bsLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, text=_('SHAPE'))
        self.scLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('SCALE'))
        self.scValue = tk.StringVar()
        self.scEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.scValue)#bd=1)
        self.rtLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('ROTATION'))
        self.rtValue = tk.StringVar()
        self.rtEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.rtValue)#bd=1)
        self.mirror = ctk.CTkButton(self.parent.convInput, width=entryLen, text=_('MIRROR'))#, padx=1, pady=1
        self.flip = ctk.CTkButton(self.parent.convInput, width=entryLen, text=_('FLIP'))#, padx=1, pady=1
        self.oLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, text=_('ORIGIN OFFSET'))
        # lines and arcs
        self.lnLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('TYPE'))
        self.lineCombo = ctk.CTkComboBox(self.parent.convInput, justify='left', border_width=1)#bd=1, editable=False)
        self.l1Label = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text='')
        self.l1Value = tk.StringVar()
        self.l1Entry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.l1Value)#bd=1)
        self.l2Label = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text='')
        self.l2Value = tk.StringVar()
        self.l2Entry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.l2Value)#bd=1)
        self.l3Label = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text='')
        self.l3Value = tk.StringVar()
        self.l3Entry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.l3Value)#bd=1)
        self.l4Label = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text='')
        self.l4Value = tk.StringVar()
        self.l4Entry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.l4Value)#bd=1)
        self.l5Label = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text='')
        self.l5Value = tk.StringVar()
        self.l5Entry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.l5Value)#bd=1)
        self.l6Label = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text='')
        self.l6Value = tk.StringVar()
        self.l6Entry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.l6Value)#bd=1)
#        self.g23bValue = tk.StringVar()
        self.g23Arc = ctk.CTkButton(self.parent.convInput, width=entryLen, text='CW - G2')#, textvariable=self.g23bValue)#, padx=1, pady=1)
        # settings
        self.preLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('PREAMBLE'))
        self.preValue = tk.StringVar()
        self.preEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, border_width=1, textvariable=self.preValue)#bd=1)
        self.pstLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('POSTAMBLE'))
        self.pstValue = tk.StringVar()
        self.pstEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, border_width=1, textvariable=self.pstValue)#bd=1)
        self.llLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, text=_('LEAD LENGTHS'))
        self.shLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, text=_('SMALL HOLES'))
        self.shValue = tk.StringVar()
        self.shEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.shValue)#bd=1)
        self.hsValue = tk.StringVar()
        self.hsEntry = ctk.CTkEntry(self.parent.convInput, width=entryLen, justify='right', border_width=1, textvariable=self.hsValue)#bd=1)
        self.hsLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, anchor='e', text=_('SPEED %'))
        self.pvLabel = ctk.CTkLabel(self.parent.convInput, width=labelLen, text=_('PREVIEW'))
        self.saveS = ctk.CTkButton(self.parent.convInput, width=entryLen, text=_('SAVE'))#, padx=1, pady=1
        self.reloadS = ctk.CTkButton(self.parent.convInput, width=entryLen, text=_('RELOAD'))#, padx=1, pady=1
        self.exitS = ctk.CTkButton(self.parent.convInput, width=entryLen, text=_('EXIT'))#, padx=1, pady=1
        # bottom
        self.previewC = ctk.CTkButton(self.parent.convInput, width=entryLen, text=_('PREVIEW'))#, padx=1, pady=1
        self.addC = ctk.CTkButton(self.parent.convInput, width=entryLen, text=_('ADD'))#, padx=1, pady=1
        self.undoC = ctk.CTkButton(self.parent.convInput, width=entryLen, text=_('UNDO'))#, padx=1, pady=1
        self.newC = ctk.CTkButton(self.parent.convInput, width=entryLen, text=_('NEW'))#, padx=1, pady=1
        self.saveC = ctk.CTkButton(self.parent.convInput, width=entryLen, text=_('SAVE'))#, padx=1, pady=1
        self.settingsC = ctk.CTkButton(self.parent.convInput, width=entryLen, text=_('SETTINGS'))#, padx=1, pady=1
        self.sendC = ctk.CTkButton(self.parent.convInput, width=entryLen, text=_('SEND'))#, padx=1, pady=1
        # spacer and separator
        self.spacer = ctk.CTkLabel(self.parent.convInput, text='')
#        self.sepline = ttk.Separator(self.parent.convInput, orient='horizontal')
        self.sepline = hSeparator(self.parent.convInput)#, orient='horizontal')
        # get default background color
        self.bBackColor = self.sendC.cget('fg_color')#'bg')
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
                          self.g23Arc, self.saveS, self.reloadS, self.exitS, self.previewC, \
                          self.addC, self.undoC, self.newC, self.saveC, self.settingsC, self.sendC]
        # for button in self.buttons:
        #     button.configure(takefocus=0)
        self.combos = [self.matCombo, self.polyCombo, self.lineCombo]
#        for combo in self.combos:
#            combo.configure(takefocus=0)

class hSeparator(ctk.CTkFrame):
    ''' horizontal separator '''
    def __init__(self, *args,
                 width: int = 120,
                 height: int = 2,
                 fg_color: str = '#808080',
                 **kwargs):
        super().__init__(*args, width=width, height=height, fg_color=fg_color, **kwargs)

class vSeparator(ctk.CTkFrame):
    ''' horizontal separator '''
    def __init__(self, *args,
                 width: int = 2,
                 height: int = 120,
                 fg_color: str = '#808080',
                 **kwargs):
        super().__init__(*args, width=width, height=height, fg_color=fg_color, **kwargs)

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

    def __getattr__(self, attr):

        def set_units(f):
            #FIXME we need to set units properly here
            if isinstance(f, float):
                return round(f * 25.4, 4)
            return f

        def inner(*args):
            ''' adds shapes to the points list '''
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
            startX = self.offsetX + ((originX - self.offsetX) * math.cos(self.angle) - (originY - self.offsetY) * math.sin(self.angle))
            startY = self.offsetY + ((originX - self.offsetX) * math.sin(self.angle) + (originY - self.offsetY) * math.cos(self.angle))
            # set end coordinates
            endX = self.offsetX + (args[0] * math.cos(self.angle) - args[1] * math.sin(self.angle))
            endY = self.offsetY + (args[0] * math.sin(self.angle) + args[1] * math.cos(self.angle))
            if attr == 'arc_feed': # arcs
                # set arc parameters
                if len(self.points): # if start point exists
                    # set arc center coordinates
                    centerX = self.offsetX + (args[2] * math.cos(self.angle) - args[3] * math.sin(self.angle))
                    centerY = self.offsetY + (args[2] * math.sin(self.angle) + args[3] * math.cos(self.angle))
                    # set arc radius
                    radius = round(math.sqrt((centerX - endX)**2 + (centerY - endY)**2), 4)
                    if args[4] > 0: # cw arc 
                        dir = args[4] * 1
                        startAngle = round(math.degrees(math.atan2(startY - centerY, startX - centerX)) * dir, 4)
                        endAngle = round(math.degrees(math.atan2(endY - centerY, endX - centerX)) * dir, 4)
                    else:  # ccw arc
                        dir = args[4] * -1
                        startAngle = round(math.degrees(math.atan2(endY - centerY, endX - centerX)) * dir, 4)
                        endAngle = round(math.degrees(math.atan2(startY - centerY, startX - centerX)) * dir, 4)
                    # circles need to be 360 deg, not 0 deg
                    if endX == startX and endY == startY:
                        endAngle += 360
                    # add new arc to points list
                    self.points.append({'shape': 'arc',
                                        'endX': endX,
                                        'endY': endY,
                                        'centerX': centerX,
                                        'centerY': centerY,
                                        'radius': radius,
                                        'startAngle': startAngle,
                                        'endAngle': endAngle,
                                        'lastX': args[0],
                                        'lastY': args[1]})
                # arcs cannot start from nowhere
                else:
                    print(f'arc without a previous move: {args}')
            else: # lines and rapids
                shape = 'line' if attr == 'straight_feed' else 'rapid'
                # add point to last line/rapid in  points list
                if len(self.points) and self.points[-1]['shape'] == shape:
                    self.points[-1]['points'].append((endX, endY))
                    self.points[-1]['lastX'] = args[0]
                    self.points[-1]['lastY'] = args[1]
                    # delete extra rapid points if required
                    if self.points[-1]['shape'] == 'rapid' and len(self.points[-1]['points']) > 2:
                        if self.points[-1]['points'][1] == self.points[-1]['points'][2]:
                            del self.points[-1]['points'][2]
                        elif self.points[-1]['shape'] == 'rapid' and len(self.points[-1]['points']) > 2:
                                if (self.points[-1]['points'][0][0], self.points[-1]['points'][0][1]) == self.g5x_offset:
                                    del self.points[-1]['points'][1]
                                else:
                                    del self.points[-1]['points'][0]
                # create new line/rapid in points list
                self.points.append({'shape': shape,
                                        'points': [(startX, startY), (endX, endY)],
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

App()
