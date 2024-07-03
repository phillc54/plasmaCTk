#!/bin/python3

import os
import sys
import linuxcnc
import hal
import customtkinter as ctk
from customtkinter import filedialog
from configparser import RawConfigParser, NoSectionError, NoOptionError

class PlasmaCTk(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_default_color_theme('dark-blue')
        ctk.set_appearance_mode('dark')
        self.title('plasma-ctk')
        self.geometry(f'{800}x{600}+{200}+{200}')
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.ini = linuxcnc.ini(sys.argv[2])
        self.appDir = os.path.dirname(os.path.realpath(__file__))
        self.configDir = os.path.dirname(sys.argv[2])
        self.imgDir = os.path.join(self.appDir, 'lib/images')
        self.tmpDir = '/tmp/plasmactk'
        if not os.path.isdir(self.tmpDir):
            os.mkdir(self.tmpDir)
        sys.path.append(os.path.join(self.appDir, 'lib'))
        self.C = linuxcnc.command()
        self.S = linuxcnc.stat()
        self.E = linuxcnc.error()
        self.comp = hal.component('plasmactk')
        self.create_hal_pins(self.comp)
        # self.S.poll()
        # get some settings from the ini file
        self.machine = self.ini.find('EMC', 'MACHINE')
        self.unitsPerMm = 1 if self.ini.find('TRAJ', 'LINEAR_UNITS') == 'mm' else 1 / 25.4
        self.thcFeedRate = float(self.ini.find('AXIS_Z', 'MAX_VELOCITY')) * float(self.ini.find('AXIS_Z', 'OFFSET_AV_RATIO')) * 60
        self.offsetFeedRate = min(float(self.ini.find('AXIS_X', 'MAX_VELOCITY')) * 30,
                                  float(self.ini.find('AXIS_Y', 'MAX_VELOCITY')) * 30,
                                  float(self.ini.find('TRAJ', 'MAX_LINEAR_VELOCITYs') or 100000))
        # read the prefs file
        self.prefs = Prefs(allow_no_value=True)
        self.prefsFile = os.path.join(self.configDir, f"{self.machine}.prefs")
        self.prefs.read(self.prefsFile)
        # dummy button to get some colors
        blah = ctk.CTkButton(self)
        self.buttonOffColor = blah.cget('fg_color')
        self.buttonOnColor = blah.cget('hover_color')
        self.backgroundColor = blah.cget('bg_color')
        self.borderColor = blah.cget('border_color')
        self.textColor = blah.cget('text_color')
        self.disabledColor = blah.cget('text_color_disabled')

        self.userButtons = {}
        self.userButtonCodes = {}
        self.fileLoaded = None
        self.fileTypes = [('G-Code Files', '*.ngc *.nc *.tap'), ('All Files', '*.*')]
        self.initialDir = os.path.expanduser('~/linuxcnc/nc_files/plasmac')
        self.defaultExtension = '.ngc'
        self.create_gui()
        self.comp.ready()
        self.parameter_load()

        self.tmp1 = None # temp for testing

        self.after(100, self.periodic)


##############################################################################
# testing
##############################################################################
    def open_input_dialog_event(self):
        dialog = ctk.CTkInputDialog(text='Type in a number:', title='CTkInputDialog')
        print('CTkInputDialog:', dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        print('change appearance to', new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace('%', '')) / 100
        ctk.set_widget_scaling(new_scaling_float)
        print('cahnge scaling to', new_scaling_float)

    def sidebar_button_event(self):
        print('sidebar button clicked')

    def set_tab_state(self, tabview, tab, state):
        ''' set a tab state to either normal or disabled '''
        stat = 'normal' if state else 'disabled'
        tabview._segmented_button._buttons_dict[tab].configure(state = stat)
        print('set tab', tab, 'state to', stat)


##############################################################################
# overrides
##############################################################################
    def ovr_feed_changed(self, value):
        print(value)
        self.ovrFeedLbl.configure(text=f'Feed {value:.0f}%')

    def ovr_feed_reset(self, event, default=100):
        self.ovrFeed.set(default)
        self.ovrFeedLbl.configure(text=f'Feed {default:.0f}%')

    def ovr_rapid_changed(self, value):
        print(value)
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
# main 1 buttons
##############################################################################

    def open_clicked(self):
        file = filedialog.askopenfile(initialdir=self.initialDir, filetypes=self.fileTypes)
        if not file:
            return
        print('load file into LinuxCNC here', file.name)
        self.initialDir = os.path.dirname(file.name)
        self.fileLoaded = file.name
        self.conv.plot_file(file.name, True)

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
        component.newpin('development', hal.HAL_BIT, hal.HAL_IN)
        component.newpin('in', hal.HAL_FLOAT, hal.HAL_IN)
        component.newpin('out', hal.HAL_FLOAT, hal.HAL_OUT)

##############################################################################
# periodic
##############################################################################
    def periodic(self):

        # bob = hal.get_value('plasmactk.arc-fail-delay')
        # if bob != self.tmp1:
        #     self.tmp1 = bob
        #     print(f"pin changed to {bob}")

        self.after(100, self.periodic)

##############################################################################
# general
##############################################################################
    # def rgb_to_hex(self, r, g, b):
    #     return f'#{r:02x}{g:02x}{b:02x}'

##############################################################################
# parameters
##############################################################################
    def parameter_write(self):
        with open(self.prefsFile, 'w') as prefsFile:
            self.prefs.write(prefsFile)

    def parameter_load(self):
        ''' section, option, default '''
        # parameter column 1
        self.startFailBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Arc Fail Timeout', 3))
        self.maxStartsBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Arc Maximum Starts', 3))
        self.retryDelayBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Arc Restart Delay', 1))
        self.voltageScaleBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Arc Voltage Scale', 1))
        self.voltageOffsetBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Arc Voltage Offset', 0))
        self.heightPerVoltBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Height Per Volt', 0.1 * self.unitsPerMm))
        self.okHighBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Arc OK High', 250))
        self.okLowBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Arc OK Low', 60))
        self.xPierceBox.set(self.prefs.get('PLASMA_PARAMETERS', 'X Pierce Offset', 1.6 * self.unitsPerMm))
        self.yPierceBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Y Pierce Offset', 0))
        # parameter column 2
        self.floatTravelBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Float Switch Travel', 1.5 * self.unitsPerMm))
        self.probeSpeedBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Probe Feed Rate', 300 * self.unitsPerMm))
        self.probeHeightBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Probe Start Height', 25 * self.unitsPerMm))
        self.ohmicOffsetBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Ohmic Probe Offset', 0))
        self.ohmicRetriesBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Ohmic Maximum Attempts', 0))
        self.skipIhsBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Skip IHS Distance', 0))
        self.offsetSpeedBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Offset Feed Rate', self.offsetFeedRate * 0.8))
        self.scribeArmBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Scribe Arming Delay', 0))
        self.scribeOnBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Scribe On Delay', 0))
        self.spotThresholdBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Spotting Threshold', 1))
        self.spotTimeBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Spotting Time', 0))
        # parameter column 3
        if self.prefs.get('ENABLE_OPTIONS', 'THC auto', 'False') == 'True':
            self.thcAutoCheck.select()
        else:
            self.thcAutoCheck.deselect()
        self.thcDelayBox.set(self.prefs.get('PLASMA_PARAMETERS', 'THC Delay', 0.5))
        self.thcSampleCountsBox.set(self.prefs.get('PLASMA_PARAMETERS', 'THC Sample Counts', 50))
        self.thcSampleThresholdBox.set(self.prefs.get('PLASMA_PARAMETERS', 'THC Sample Threshold', 1))
        self.thcThresholdBox.set(self.prefs.get('PLASMA_PARAMETERS', 'THC Threshold', 1))
        self.thcSpeedBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Pid P Gain', 10))
        self.thcVADthresholdBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Velocity Anti Dive Threshold', 90))
        self.thcVoidSlopeBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Void Sense Slope', 500))
        self.thcPidIBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Pid I Gain', 0))
        self.thcPidDBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Pid D Gain', 0))
        self.safeHeightBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Safe Height', 25 * self.unitsPerMm))
        self.setupSpeedBox.set(self.prefs.get('PLASMA_PARAMETERS', 'Setup Feed Rate', self.thcFeedRate * 0.8))
        self.parameter_write()

    def parameter_save(self):
        # parameter column 1
        self.prefs.set('PLASMA_PARAMETERS', 'Arc Fail Timeout', self.startFailBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Arc Maximum Starts', self.maxStartsBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Arc Restart Delay', self.retryDelayBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Arc Voltage Scale', self.voltageScaleBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Arc Voltage Offset', self.voltageOffsetBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Height Per Volt', self.heightPerVoltBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Arc OK High', self.okHighBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Arc OK Low', self.okLowBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'X Pierce Offset', self.xPierceBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Y Pierce Offset', self.yPierceBox.get())
        # parameter column 2
        self.prefs.set('PLASMA_PARAMETERS', 'Float Switch Travel', self.floatTravelBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Probe Feed Rate', self.probeSpeedBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Probe Start Height', self.probeHeightBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Ohmic Probe Offset', self.ohmicOffsetBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Ohmic Maximum Attempts', self.ohmicRetriesBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Skip IHS Distance', self.skipIhsBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Offset Feed Rate', self.offsetSpeedBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Scribe Arming Delay', self.scribeArmBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Scribe On Delay', self.scribeOnBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Spotting Threshold', self.spotThresholdBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Spotting Time', self.spotTimeBox.get())
        # parameter column 3
        self.prefs.set('ENABLE_OPTIONS', 'THC auto', bool(self.thcAutoCheck.get()))
        self.prefs.set('PLASMA_PARAMETERS', 'THC Delay', self.thcDelayBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'THC Sample Counts', self.thcSampleCountsBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'THC Sample Threshold', self.thcSampleThresholdBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'THC Threshold', self.thcThresholdBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Pid P Gain', self.thcSpeedBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Velocity Anti Dive Threshold', self.thcVADthresholdBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Void Sense Slope', self.thcVoidSlopeBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Pid I Gain', self.thcPidIBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Pid D Gain', self.thcPidDBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Safe Height', self.safeHeightBox.get())
        self.prefs.set('PLASMA_PARAMETERS', 'Setup Feed Rate', self.setupSpeedBox.get())
        self.parameter_write()

##############################################################################
# gui build
##############################################################################
    def create_gui(self):
        # temporary for conversational testing
        self.materialFileDict = {1: {'name': 'Mat #1', 'kerf_width': 1.1, 'pierce_height': 3.1, 'pierce_delay': 0.0, 'puddle_jump_height': 0, 'puddle_jump_delay': 0.0, 'cut_height': 1.1, 'cut_speed': 4000, 'cut_amps': 41, 'cut_volts': 101, 'pause_at_end': 0.0, 'gas_pressure': 0.0, 'cut_mode': 1}, 2: {'name': 'Mat #2 is the longest by a very long shot', 'kerf_width': 1.2, 'pierce_height': 3.2, 'pierce_delay': 0.0, 'puddle_jump_height': 0, 'puddle_jump_delay': 0.0, 'cut_height': 1.6, 'cut_speed': 2002, 'cut_amps': 42, 'cut_volts': 102, 'pause_at_end': 0.0, 'gas_pressure': 0.0, 'cut_mode': 1}, 3: {'name': 'Mat #3', 'kerf_width': 1.3, 'pierce_height': 3.3, 'pierce_delay': 0.0, 'puddle_jump_height': 0, 'puddle_jump_delay': 0.0, 'cut_height': 1.3, 'cut_speed': 2003, 'cut_amps': 43, 'cut_volts': 103, 'pause_at_end': 0.0, 'gas_pressure': 0.0, 'cut_mode': 1}, 4: {'name': 'Mat #4', 'kerf_width': 1.4, 'pierce_height': 3.4, 'pierce_delay': 0.4, 'puddle_jump_height': 0, 'puddle_jump_delay': 0.0, 'cut_height': 1.4, 'cut_speed': 2004, 'cut_amps': 44, 'cut_volts': 104, 'pause_at_end': 0.0, 'gas_pressure': 0.0, 'cut_mode': 1}, 5: {'name': 'Mat #5', 'kerf_width': 1.5, 'pierce_height': 3.5, 'pierce_delay': 0.0, 'puddle_jump_height': 0, 'puddle_jump_delay': 0.0, 'cut_height': 1.5, 'cut_speed': 2005, 'cut_amps': 45, 'cut_volts': 105, 'pause_at_end': 0.5, 'gas_pressure': 0.0, 'cut_mode': 1}, 6: {'name': 'Mat #6', 'kerf_width': 1.6, 'pierce_height': 3.0, 'pierce_delay': 0.0, 'puddle_jump_height': 0, 'puddle_jump_delay': 0.0, 'cut_height': 1.6, 'cut_speed': 2006, 'cut_amps': 46, 'cut_volts': 106, 'pause_at_end': 0.0, 'gas_pressure': 0.0, 'cut_mode': 1}}
        self.matNum = 0

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
        import conversational
        self.conv = conversational.Conversational(self)
        self.create_parameters_1_frame()
        self.create_parameters_2_frame()
        self.create_parameters_3_frame()
        self.create_parameters_buttons()
        self.create_settings_1_frame()
        self.create_settings_2_frame()
        self.create_settings_3_frame()
        self.create_status_1_frame()
        self.create_status_2_frame()
        self.create_status_3_frame()

    def create_tabs(self):
        ''' tabview as the main window '''

        def tab_changed(tab):
            if tab == 'Conversational':
                self.conv.canvas.update()
                self.conv.zoom_all()

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
        self.mainButtons.grid(row=0, column=0, rowspan=2, padx=1, pady=1, sticky='nsew')
        self.mainButtons.grid_rowconfigure((1, 2), weight=1)
        self.mainButtonLbl = ctk.CTkLabel(self.mainButtons, text='Button Panel', height=16, anchor='n')
        self.mainButtonLbl.grid(row=0, column=0, padx=4, pady=(1, 0), sticky='new')
        self.mainButtonFrame = ctk.CTkScrollableFrame(self.mainButtons, width=144, fg_color='transparent')
        self.mainButtonFrame.grid(row=1, column=0, rowspan=2, padx=2, pady=(0, 2), sticky='nsew')
        self.torchEnableBtn = ctk.CTkButton(self.mainButtonFrame, text = 'Torch Enable', command=self.torch_enable_clicked, height=40)
        self.torchEnableBtn.grid(row=0, column=0, padx=2, pady=(0, 2), sticky='new')
        self.user_button_setup()

    def create_main_control_frame(self):
        ''' main tab control frame '''
        self.mainControl = ctk.CTkFrame(self.tabs.tab('Main'), border_width=1, border_color=self.borderColor)
        self.mainControl.grid(row=0, column=1, padx=1, pady=1, sticky='nsew')
        self.mainControl.grid_rowconfigure((1, 2, 3, 4), weight=6)
        self.mainControl.grid_rowconfigure((5, 6, 7), weight=1)
        self.mainControl.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.mainControlLbl = ctk.CTkLabel(self.mainControl, text='Cycle Panel', height=16, anchor='n')
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
        self.main1Frame.grid(row=1, column=1, padx=1, pady=1, sticky='nsew')

        self.open = ctk.CTkButton(self.main1Frame, text='Open', command=self.open_clicked)
        self.open.grid(row=0, column=0, padx=(3,1), pady=(3,0), sticky='nsew')

    def create_main_2_frame(self):
        ''' main tab ??? frame '''
        self.main2Frame = ctk.CTkFrame(self.tabs.tab('Main'), border_width=1, border_color=self.borderColor)
        self.main2Frame.grid(row=0, column=2, padx=1, pady=1, sticky='nsew')

    def create_main_3_frame(self):
        ''' main tab ??? frame '''
        self.main3Frame = ctk.CTkFrame(self.tabs.tab('Main'), border_width=1, border_color=self.borderColor)
        self.main3Frame.grid(row=1, column=2, padx=1, pady=1, sticky='nsew')

    def create_main_4_frame(self):
        ''' main tab ??? frame '''
        self.main4Frame = ctk.CTkFrame(self.tabs.tab('Main'), border_width=1, border_color=self.borderColor)
        self.main4Frame.grid(row=0, column=3, padx=1, pady=1, sticky='nsew')

    def create_main_5_frame(self):
        ''' main tab ??? frame '''
        self.main5Frame = ctk.CTkFrame(self.tabs.tab('Main'), border_width=1, border_color=self.borderColor)
        self.main5Frame.grid(row=1, column=3, padx=1, pady=1, sticky='nsew')

    def create_conversational_toolbar_frame(self):
        ''' conversational button frame '''
        self.convTools = ctk.CTkFrame(self.tabs.tab('Conversational'), border_width=1, border_color=self.borderColor, height=40)
        self.convTools.grid(row=0, column=0, columnspan=2, padx=1, pady=1, sticky='nsew')

    def create_conversational_input_frame(self):
        ''' conversational input frame '''
        self.convInput = ctk.CTkFrame(self.tabs.tab('Conversational'), border_width=1, border_color=self.borderColor, width=120)
        self.convInput.grid(row=1, column=0, padx=1, pady=1, sticky='nsew')
        self.convInput.grid_rowconfigure(10, weight=1)

    def create_conversational_preview_frame(self):
        ''' conversational preview frame '''
        self.convPreview = ctk.CTkFrame(self.tabs.tab('Conversational'), border_width=1, border_color=self.borderColor)
        self.convPreview.grid(row=1, column=1, padx=1, pady=1, sticky='nsew')
        self.convPreview.grid_rowconfigure(0, weight=1)
        self.convPreview.grid_columnconfigure(1, weight=1)

    def create_parameters_1_frame(self):
        ''' arc and pierce only parameters '''
        params = ctk.CTkFrame(self.tabs.tab('Parameters'), border_width=1, border_color=self.borderColor)
        params.grid(row=0, column=0, padx=1, pady=1, sticky='nsew')
        params.grid_rowconfigure((1,2,3,4,5,6,7,8,9,10,11), weight=1)
        params.grid_rowconfigure((20), weight=50)
        params.grid_columnconfigure(1, weight=1)
        arcLabel = ctk.CTkLabel(params, text='ARC:')
        arcLabel.grid(row=0, column=0, columnspan=2, padx=(3,0), pady=(3,0), sticky='w')
        startFailLabel = ctk.CTkLabel(params, text='Start Fail Timer')
        startFailLabel.grid(row=1, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.startFailBox = HalSpinBox(params, min_value=0.1, max_value=60, decimals=1, step_size=0.1, pin_name='arc-fail-delay')
        self.startFailBox.grid(row=1, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        maxStartsLabel = ctk.CTkLabel(params, text='Max Starts')
        maxStartsLabel.grid(row=2, column=0, padx=(3,1), pady=(3,0), sticky='nse')
        self.maxStartsBox = HalSpinBox(params, min_value=1, max_value=5, pin_name='arc-max-starts')
        self.maxStartsBox.grid(row=2, column=1, padx=(1,3), pady=(3,0), sticky='nsew')
        retryDelayLabel = ctk.CTkLabel(params, text='Retry Delay')
        retryDelayLabel.grid(row=3, column=0, padx=(3,1), pady=(3,0), sticky='nse')
        self.retryDelayBox = HalSpinBox(params, min_value=1, max_value=60, pin_name='restart-delay')
        self.retryDelayBox.grid(row=3, column=1, padx=(1,3), pady=(3,0), sticky='nsew')
        voltageScaleLabel = ctk.CTkLabel(params, text='Voltage Scale')
        voltageScaleLabel.grid(row=4, column=0, padx=(3,1), pady=(3,0), sticky='nse')
        self.voltageScaleBox = HalSpinBox(params, min_value=-9999, max_value=9999, decimals=6, step_size=0.000001, pin_name='arc-voltage-scale')
        self.voltageScaleBox.grid(row=4, column=1, padx=(1,3), pady=(3,0), sticky='nsew')
        voltageOffsetLabel = ctk.CTkLabel(params, text='Voltage Offset')
        voltageOffsetLabel.grid(row=5, column=0, padx=(3,1), pady=(3,0), sticky='nse')
        self.voltageOffsetBox = HalSpinBox(params, min_value=-999999, max_value=999999, decimals=3, step_size=0.001, pin_name='arc-voltage-offset')
        self.voltageOffsetBox.grid(row=5, column=1, padx=(1,3), pady=(3,0), sticky='nsew')
        heightPerVoltLabel = ctk.CTkLabel(params, text='Height per Volt')
        heightPerVoltLabel.grid(row=6, column=0, padx=(3,1), pady=(3,0), sticky='nse')
        self.heightPerVoltBox = HalSpinBox(params, min_value=0.025, max_value=0.25, decimals=3, step_size=0.001, pin_name='height-per-volt')
        self.heightPerVoltBox.grid(row=6, column=1, padx=(1,3), pady=(3,0), sticky='nsew')
        okHighLabel = ctk.CTkLabel(params, text='OK High Volts')
        okHighLabel.grid(row=7, column=0, padx=(3,1), pady=(3,0), sticky='nse')
        self.okHighBox = HalSpinBox(params, max_value=99999, pin_name='arc-ok-high')
        self.okHighBox.grid(row=7, column=1, padx=(1,3), pady=(3,0), sticky='nsew')
        okLowLabel = ctk.CTkLabel(params, text='OK Low Volts')
        okLowLabel.grid(row=8, column=0, padx=(3,1), pady=(3,0), sticky='nse')
        self.okLowBox = HalSpinBox(params, pin_name='arc-ok-low')
        self.okLowBox.grid(row=8, column=1, padx=(1,3), pady=(3,0), sticky='nsew')
        pierceLabel = ctk.CTkLabel(params, text='PIERCE ONLY:')
        pierceLabel.grid(row=9, column=0, columnspan=2, padx=(3,0), pady=(3,0), sticky='w')
        xPierceLabel = ctk.CTkLabel(params, text='Threshold Volts')
        xPierceLabel.grid(row=10, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.xPierceBox = HalSpinBox(params, min_value=-5, max_value=5, decimals=1, step_size=0.1, pin_name='x_pierce_offset')
        self.xPierceBox.grid(row=10, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        yPierceLabel = ctk.CTkLabel(params, text='Time On (mS)')
        yPierceLabel.grid(row=11, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.yPierceBox = HalSpinBox(params, min_value=-5, max_value=5, decimals=1, step_size=0.1, pin_name='y_pierce_offset')
        self.yPierceBox.grid(row=11, column=1, padx=(1,3), pady=(1,0), sticky='nsew')

    def create_parameters_2_frame(self):
        ''' probing, scribing, and spotting parameters '''
        params = ctk.CTkFrame(self.tabs.tab('Parameters'), border_width=1, border_color=self.borderColor)
        params.grid(row=0, column=1, padx=1, pady=1, sticky='nsew')
        params.grid_rowconfigure((1,2,3,4,5,6,7,8,9,10,11,12,13), weight=1)
        params.grid_rowconfigure((20), weight=50)
        params.grid_columnconfigure(1, weight=1)
        probeLabel = ctk.CTkLabel(params, text='PROBING:')
        probeLabel.grid(row=0, column=0, columnspan=2, padx=(3,0), pady=(3,0), sticky='w')
        floatTravelLabel = ctk.CTkLabel(params, text='Float Travel')
        floatTravelLabel.grid(row=1, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.floatTravelBox = HalSpinBox(params, min_value=-25, max_value=25, decimals=2, step_size=0.01, pin_name='float-switch-travel')
        self.floatTravelBox.grid(row=1, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        probeSpeedLabel = ctk.CTkLabel(params, text='Probe Speed')
        probeSpeedLabel.grid(row=2, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.probeSpeedBox = HalSpinBox(params, pin_name='probe-feed-rate')
        self.probeSpeedBox.grid(row=2, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        probeHeightLabel = ctk.CTkLabel(params, text='Probe Height')
        probeHeightLabel.grid(row=3, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.probeHeightBox = HalSpinBox(params, min_value=1, pin_name='probe-start-height')
        self.probeHeightBox.grid(row=3, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        ohmicOffsetLabel = ctk.CTkLabel(params, text='Ohmic Offset')
        ohmicOffsetLabel.grid(row=4, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.ohmicOffsetBox = HalSpinBox(params, min_value=-25, max_value=25, decimals=2, step_size=0.01, pin_name='ohmic-probe-offset')
        self.ohmicOffsetBox.grid(row=4, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        ohmicRetriesLabel = ctk.CTkLabel(params, text='Ohmic Retries')
        ohmicRetriesLabel.grid(row=5, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.ohmicRetriesBox = HalSpinBox(params, max_value=10, pin_name='ohmic-max-attempts')
        self.ohmicRetriesBox.grid(row=5, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        skipIhsLabel = ctk.CTkLabel(params, text='Skip IHS')
        skipIhsLabel.grid(row=6, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.skipIhsBox = HalSpinBox(params, max_value=999, pin_name='skip-ihs-distance')
        self.skipIhsBox.grid(row=6, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        offsetSpeedLabel = ctk.CTkLabel(params, text='Offset Speed')
        offsetSpeedLabel.grid(row=7, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.offsetSpeedBox = HalSpinBox(params, max_value=self.offsetFeedRate, pin_name='offset-feed-rate')
        self.offsetSpeedBox.grid(row=7, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        scribeLabel = ctk.CTkLabel(params, text='SCRIBING:')
        scribeLabel.grid(row=8, column=0, columnspan=2, padx=(3,0), pady=(3,0), sticky='w')
        scribeArmLabel = ctk.CTkLabel(params, text='Arm Delay')
        scribeArmLabel.grid(row=9, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.scribeArmBox = HalSpinBox(params, max_value=10, decimals=1, step_size=0.1, pin_name='scribe-arm-delay')
        self.scribeArmBox.grid(row=9, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        scribeOnLabel = ctk.CTkLabel(params, text='On Delay')
        scribeOnLabel.grid(row=10, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.scribeOnBox = HalSpinBox(params, max_value=10, decimals=1, step_size=0.1, pin_name='scribe-on-delay')
        self.scribeOnBox.grid(row=10, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        spotLabel = ctk.CTkLabel(params, text='SPOTTING:')
        spotLabel.grid(row=11, column=0, columnspan=2, padx=(3,0), pady=(3,0), sticky='w')
        spotThresholdLabel = ctk.CTkLabel(params, text='Threshold Volts')
        spotThresholdLabel.grid(row=12, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.spotThresholdBox = HalSpinBox(params, max_value=200, pin_name='spotting-threshold')
        self.spotThresholdBox.grid(row=12, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        spotTimeLabel = ctk.CTkLabel(params, text='Time On (mS)')
        spotTimeLabel.grid(row=13, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.spotTimeBox = HalSpinBox(params, max_value=9999, pin_name='spotting-time')
        self.spotTimeBox.grid(row=13, column=1, padx=(1,3), pady=(1,0), sticky='nsew')

    def create_parameters_3_frame(self):
        ''' thc and motion parameters '''
        params = ctk.CTkFrame(self.tabs.tab('Parameters'), border_width=1, border_color=self.borderColor)
        params.grid(row=0, column=2, padx=1, pady=1, sticky='nsew')
        params.grid_rowconfigure((1,2,3,4,5,6,7,8,9,10), weight=1)
        params.grid_rowconfigure((20), weight=50)
        params.grid_columnconfigure(1, weight=1)
        thcLabel = ctk.CTkLabel(params, text='THC:')
        thcLabel.grid(row=0, column=0, columnspan=2, padx=(3,0), pady=(3,0), sticky='w')
        thcAutoLabel = ctk.CTkLabel(params, text='Auto Activate')
        thcAutoLabel.grid(row=1, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.thcAutoCheck = HalCheckBox(params, pin_name='thc-auto')
        self.thcAutoCheck.grid(row=1, column=1, padx=(3,3), pady=(1,0), sticky='nsw')
        thcDelayLabel = ctk.CTkLabel(params, text='Start Delay')
        thcDelayLabel.grid(row=2, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.thcDelayBox = HalSpinBox(params, max_value=9, decimals=2, step_size=0.01, pin_name='thc-delay')
        self.thcDelayBox.grid(row=2, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        thcSampleCountsLabel = ctk.CTkLabel(params, text='Sample Counts')
        thcSampleCountsLabel.grid(row=3, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.thcSampleCountsBox = HalSpinBox(params, max_value=1000, pin_name='thc-sample-counts')
        self.thcSampleCountsBox.grid(row=3, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        thcSampleThresholdLabel = ctk.CTkLabel(params, text='Sample Threshold')
        thcSampleThresholdLabel.grid(row=4, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.thcSampleThresholdBox = HalSpinBox(params, max_value=99, decimals=2, step_size=0.01, pin_name='thc-sample-threshold')
        self.thcSampleThresholdBox.grid(row=4, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        thcThresholdLabel = ctk.CTkLabel(params, text='Threshold')
        thcThresholdLabel.grid(row=5, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.thcThresholdBox = HalSpinBox(params, min_value=0.05, max_value=10, decimals=2, step_size=0.01, pin_name='thc-threshold')
        self.thcThresholdBox.grid(row=5, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        thcSpeedLabel = ctk.CTkLabel(params, text='Speed (PID-P)')
        thcSpeedLabel.grid(row=6, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.thcSpeedBox = HalSpinBox(params, max_value=1000, pin_name='pid-p-gain')
        self.thcSpeedBox.grid(row=6, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        thcVADthresholdLabel = ctk.CTkLabel(params, text='VAD Threshold')
        thcVADthresholdLabel.grid(row=7, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.thcVADthresholdBox = HalSpinBox(params, min_value=1, max_value=99, pin_name='cornerlock-threshold')
        self.thcVADthresholdBox.grid(row=7, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        thcVoidSlopeLabel = ctk.CTkLabel(params, text='Void Slope')
        thcVoidSlopeLabel.grid(row=8, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.thcVoidSlopeBox = HalSpinBox(params, min_value=1, max_value=10000, pin_name='voidlock-slope')
        self.thcVoidSlopeBox.grid(row=8, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        thcPidILabel= ctk.CTkLabel(params, text='PID-I')
        thcPidILabel.grid(row=9, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.thcPidIBox = HalSpinBox(params, max_value=1000, pin_name='pid-i-gain')
        self.thcPidIBox.grid(row=9, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        thcPidDLabel = ctk.CTkLabel(params, text='PID-P')
        thcPidDLabel.grid(row=10, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.thcPidDBox = HalSpinBox(params, max_value=1000, pin_name='pid-d-gain')
        self.thcPidDBox.grid(row=10, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        motionLabel = ctk.CTkLabel(params, text='MOTION:')
        motionLabel.grid(row=11, column=0, columnspan=2, padx=(3,0), pady=(3,0), sticky='w')
        safeHeightLabel = ctk.CTkLabel(params, text='Safe Height')
        safeHeightLabel.grid(row=12, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.safeHeightBox = HalSpinBox(params, min_value=1, pin_name='safe-height')
        self.safeHeightBox.grid(row=12, column=1, padx=(1,3), pady=(1,0), sticky='nsew')
        setupSpeedLabel = ctk.CTkLabel(params, text='Setup Speed')
        setupSpeedLabel.grid(row=13, column=0, padx=(3,1), pady=(1,0), sticky='nse')
        self.setupSpeedBox = HalSpinBox(params, max_value=self.thcFeedRate, pin_name='setup-feed-rate')
        self.setupSpeedBox.grid(row=13, column=1, padx=(1,3), pady=(1,0), sticky='nsew')

    def create_parameters_buttons(self):
        ''' parameters buttons'''
        paramButtons = ctk.CTkFrame(self.tabs.tab('Parameters'))#, border_width=1, border_color=self.borderColor)
        paramButtons.grid(row=1, column=0, columnspan=3, padx=1, pady=(3,0), sticky='nsew')
        paramButtons.grid_columnconfigure((0,3), weight=1)
        paramSave = ctk.CTkButton(paramButtons, text='Save', command=self.parameter_save)
        paramSave.grid(row=0, column=1, padx=3)
        paramLoad = ctk.CTkButton(paramButtons, text='Reload', command=self.parameter_load)
        paramLoad.grid(row=0, column=2, padx=3)

    def create_settings_1_frame(self):
        ''' settings ??? frame '''
        self.settings1 = ctk.CTkFrame(self.tabs.tab('Settings'), border_width=1, border_color=self.borderColor)
        self.settings1.grid(row=0, column=0, padx=1, pady=1, sticky='nsew')

    def create_settings_2_frame(self):
        ''' settings ??? frame '''
        self.settings2 = ctk.CTkFrame(self.tabs.tab('Settings'), border_width=1, border_color=self.borderColor)
        self.settings2.grid(row=0, column=1, padx=1, pady=1, sticky='nsew')

    def create_settings_3_frame(self):
        ''' settings ??? frame '''
        self.settings3 = ctk.CTkFrame(self.tabs.tab('Settings'), border_width=1, border_color=self.borderColor)
        self.settings3.grid(row=0, column=2, padx=1, pady=1, sticky='nsew')

    def create_status_1_frame(self):
        ''' status ??? frame '''
        self.status1 = ctk.CTkFrame(self.tabs.tab('Status'), border_width=1, border_color=self.borderColor)
        self.status1.grid(row=0, column=0, padx=1, pady=1, sticky='nsew')

    def create_status_2_frame(self):
        ''' status ??? frame '''
        self.status2 = ctk.CTkFrame(self.tabs.tab('Status'), border_width=1, border_color=self.borderColor)
        self.status2.grid(row=0, column=1, padx=1, pady=1, sticky='nsew')

    def create_status_3_frame(self):
        ''' status ??? frame '''
        self.status3 = ctk.CTkFrame(self.tabs.tab('Status'), border_width=1, border_color=self.borderColor)
        self.status3.grid(row=0, column=2, padx=1, pady=1, sticky='nsew')

class HalCheckBox(ctk.CTkCheckBox):
    ''' adds a hal pin to a CTkCheckBox'''
    def __init__(self,
                 master,
                 pin_name = None):
        super().__init__(master, text='', border_width=1)
        self.pin_name = pin_name
        self._variable = ctk.IntVar()
        if pin_name:
            self.winfo_toplevel().comp.newpin(pin_name, hal.HAL_BIT, hal.HAL_OUT)
            self._variable_callback_name = self._variable.trace_add('write', self.write_hal_pin)

    def write_hal_pin(self, *args):
        self.winfo_toplevel().comp[self.pin_name] = self.get()

class HalSpinBox(ctk.CTkFrame):
    ''' this is a hack of the tutorial from:
        https://customtkinter.tomschimansky.com/tutorial/spinbox '''
    def __init__(self,
                 master,
                 width=100,
                 height=30,
                 min_value=0,
                 max_value=100,
                 decimals=0,
                 step_size=1,
                 start_value=0,
                 wrap=True,
                 justify='right',
                 pin_name = None,
                 command=None):
        super().__init__(master)
        self.decimals = decimals
        self.num_type = int if not decimals else float
        self.start_value = self.num_type(start_value)
        self.min_value = self.num_type(min_value)
        self.max_value = self.num_type(max_value)
        self.step_size = self.num_type(step_size)
        self.wrap = wrap
        self.pin_name = pin_name
        self.command = command
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 2), weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.dec_button = ctk.CTkButton(self, text='-', width=height - 6, height=height - 6, command=lambda:self.spin(-1))
        self.dec_button.grid(row=0, column=0, padx=(3, 0), pady=3, sticky='nsew')
        self.entry = ctk.CTkEntry(self, width=width - (2 * height), height=height - 6, border_width=0, justify=justify)
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky='nsew')
        self.entry.bind('<KeyRelease>', self.entry_changed)
        self.inc_button = ctk.CTkButton(self, text='+', width=height - 6, height=height - 6, command=lambda:self.spin(1))
        self.inc_button.grid(row=0, column=2, padx=(0, 3), pady=3, sticky='nsew')
        # default value
        if self.start_value < self.min_value:
            value = self.min_value
        elif start_value > self.max_value:
            value = self.max_value
        else:
            value = self.start_value
        text = f"{value:.{self.decimals}f}"
        self.entry.insert(0, text)
        if pin_name:
            num = hal.HAL_S32 if not decimals else hal.HAL_FLOAT
            self.winfo_toplevel().comp.newpin(pin_name, num, hal.HAL_OUT)
            self.winfo_toplevel().comp[pin_name] = text

    def entry_changed(self, event):
        try:
            x = False
            value = self.num_type(self.entry.get())
            if value < self.min_value:
                value = self.min_value
                x = True
            elif value > self.max_value:
                value = self.max_value
                x = True
            text = f"{value:.{self.decimals}f}"
            if x:
                self.set(value)
            if self.pin_name:
                self.winfo_toplevel().comp[self.pin_name] = text
        except (TypeError, ValueError):
            return

    def spin(self, direction):
        if self.command is not None:
            self.command()
        try:
            value = self.num_type(self.entry.get()) + (self.step_size * direction)
            if value < self.min_value:
                if self.wrap:
                    value = self.max_value
                else:
                    value = self.min_value
            elif value > self.max_value:
                if self.wrap:
                    value = self.min_value
                else:
                    value = self.max_value
            self.entry.delete(0, 'end')
            text = f"{value:.{self.decimals}f}"
            self.entry.insert(0, text)
            if self.pin_name:
                self.winfo_toplevel().comp[self.pin_name] = text
        except ValueError:
            return

    def get(self):
        try:
            return self.num_type(self.entry.get())
        except ValueError:
            return None

    def set(self, value):
        self.entry.delete(0, 'end')
        text = f"{float(value):.{self.decimals}f}"
        self.entry.insert(0, text)
        if self.pin_name:
            self.winfo_toplevel().comp[self.pin_name] = text

class Prefs(RawConfigParser):
    optionxform = str # preserve case

    def get(self, section, option, default=None):
        try:
            return RawConfigParser.get(self, section, option)
        except NoOptionError:
            RawConfigParser.set(self, section, option, default)
            return default
        except Exception as e:
            print(f"configparser getter error:\n{e}")
            return None

    def set(self, section, option, value):
        try:
            return RawConfigParser.set(self, section, option, value)
        except NoSectionError:
            RawConfigParser.add_section(self, section)
            return RawConfigParser.set(self, section, option, value)
        except Exception as e:
            print(f"configparser setter error:\n{e}")
            return None

app = PlasmaCTk()
app.mainloop()
