#!/bin/python3

import os
import sys
import linuxcnc
import hal
import customtkinter as ctk
from customtkinter import filedialog

APPDIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(APPDIR, 'lib'))
print(f"   CWD: {os.getcwd()}")
print(f"APPDIR: {APPDIR}")
#configPath = os.getcwd()
#p2Path = os.path.join(configPath, 'plasmac2')
#if os.path.isdir(os.path.join(p2Path, 'lib')):
#    extHalPins = {}
#    import sys
#    libPath = os.path.join(p2Path, 'lib')
#    sys.path.append(libPath)
import conversational

IMGPATH = os.path.join(APPDIR, 'lib/images')
INI = os.path.join(os.path.expanduser('~'), 'linuxcnc/configs/0_ctk_metric/metric.ini')
TMPPATH = '/tmp/plasmactk'
if not os.path.isdir(TMPPATH):
    os.mkdir(TMPPATH)

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
        self.C = linuxcnc.command()
        self.S = linuxcnc.stat()
        self.E = linuxcnc.error()
        try:
            self.comp = hal.component('plasmactk-ui')
            self.create_hal_pins(self.comp)
            self.comp.ready()
            self.S.poll()
#FIXME   this is just for testing purposes and needs to be removed when completed
            hal.set_p('plasmac.cut-feed-rate', '1')
        except:
            print('\nCannot create hal component\nIs LinuxCNC running?\nRunning in development mode...\n')
            self.comp = {'development': True}

        self.borderColor = '#808080'
        self.userButtons = {}
        self.userButtonCodes = {}
        self.fileLoaded = None
        self.fileTypes = [('G-Code Files', '*.ngc *.nc *.tap'), ('All Files', '*.*')]
        self.initialDir = os.path.expanduser('~/linuxcnc/nc_files/plasmac')
        self.defaultExtension = '.ngc'
        # create the gui
        self.create_gui()


##############################################################################
# testing
##############################################################################
    def open_input_dialog_event(self):
        dialog = ctk.CTkInputDialog(text='Type in a number:', title='CTkInputDialog')
        # print('CTkInputDialog:', dialog.get_input())

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
# main 1 buttons
##############################################################################

    def open_clicked(self):
        file = filedialog.askopenfile(initialdir=self.initialDir, filetypes=self.fileTypes)
        if not file:
            return
        print('load file into LinuxCNC here')
        self.fileLoaded = file
        self.conv.load_file(file)

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
        #print('+100mS')

        self.after(100, self.periodic)

##############################################################################
# general
##############################################################################
    # def rgb_to_hex(self, r, g, b):
    #     return f'#{r:02x}{g:02x}{b:02x}'

##############################################################################
# gui build
##############################################################################
    def create_gui(self):

        # temporary for conversational testing
        self.materialFileDict = {1: {'name': 'Mat #1', 'kerf_width': 1.1, 'pierce_height': 3.1, 'pierce_delay': 0.0, 'puddle_jump_height': 0, 'puddle_jump_delay': 0.0, 'cut_height': 1.1, 'cut_speed': 4000, 'cut_amps': 41, 'cut_volts': 101, 'pause_at_end': 0.0, 'gas_pressure': 0.0, 'cut_mode': 1}, 2: {'name': 'Mat #2 is the longest by a very long shot', 'kerf_width': 1.2, 'pierce_height': 3.2, 'pierce_delay': 0.0, 'puddle_jump_height': 0, 'puddle_jump_delay': 0.0, 'cut_height': 1.6, 'cut_speed': 2002, 'cut_amps': 42, 'cut_volts': 102, 'pause_at_end': 0.0, 'gas_pressure': 0.0, 'cut_mode': 1}, 3: {'name': 'Mat #3', 'kerf_width': 1.3, 'pierce_height': 3.3, 'pierce_delay': 0.0, 'puddle_jump_height': 0, 'puddle_jump_delay': 0.0, 'cut_height': 1.3, 'cut_speed': 2003, 'cut_amps': 43, 'cut_volts': 103, 'pause_at_end': 0.0, 'gas_pressure': 0.0, 'cut_mode': 1}, 4: {'name': 'Mat #4', 'kerf_width': 1.4, 'pierce_height': 3.4, 'pierce_delay': 0.4, 'puddle_jump_height': 0, 'puddle_jump_delay': 0.0, 'cut_height': 1.4, 'cut_speed': 2004, 'cut_amps': 44, 'cut_volts': 104, 'pause_at_end': 0.0, 'gas_pressure': 0.0, 'cut_mode': 1}, 5: {'name': 'Mat #5', 'kerf_width': 1.5, 'pierce_height': 3.5, 'pierce_delay': 0.0, 'puddle_jump_height': 0, 'puddle_jump_delay': 0.0, 'cut_height': 1.5, 'cut_speed': 2005, 'cut_amps': 45, 'cut_volts': 105, 'pause_at_end': 0.5, 'gas_pressure': 0.0, 'cut_mode': 1}, 6: {'name': 'Mat #6', 'kerf_width': 1.6, 'pierce_height': 3.0, 'pierce_delay': 0.0, 'puddle_jump_height': 0, 'puddle_jump_delay': 0.0, 'cut_height': 1.6, 'cut_speed': 2006, 'cut_amps': 46, 'cut_volts': 106, 'pause_at_end': 0.0, 'gas_pressure': 0.0, 'cut_mode': 1}}
        self.unitsPerMm = 1
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
        self.conv = conversational.Conversational(self, False)
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

        self.open = ctk.CTkButton(self.main1Frame, text='Open', command=self.open_clicked)
        self.open.grid(row=0, column=0, padx=(3,1), pady=(3,0), sticky='nsew')

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
        self.convTools = ctk.CTkFrame(self.tabs.tab('Conversational'), border_width=1, border_color=self.borderColor, height=40)
        self.convTools.grid(row=0, column=0, columnspan=2, padx=1, pady = 1, sticky='nsew')

    def create_conversational_input_frame(self):
        ''' conversational input frame '''
        self.convInput = ctk.CTkFrame(self.tabs.tab('Conversational'), border_width=1, border_color=self.borderColor, width=120)
        self.convInput.grid(row=1, column=0, padx=1, pady = 1, sticky='nsew')
        self.convInput.grid_rowconfigure(10, weight=1)

    def create_conversational_preview_frame(self):
        ''' conversational preview frame '''
        self.convPreview = ctk.CTkFrame(self.tabs.tab('Conversational'), border_width=1, border_color=self.borderColor)
        self.convPreview.grid(row=1, column=1, padx=1, pady = 1, sticky='nsew')
        self.convPreview.grid_rowconfigure(0, weight=1)
        self.convPreview.grid_columnconfigure(1, weight=1)

    def create_parameters_1_frame(self):
        ''' parameters ??? frame '''
        self.parameters1 = ctk.CTkFrame(self.tabs.tab('Parameters'), border_width=1, border_color=self.borderColor)
        self.parameters1.grid(row=0, column=0, padx=1, pady = 1, sticky='nsew')

    def create_parameters_2_frame(self):
        ''' parameters ??? frame '''
        self.parameters2 = ctk.CTkFrame(self.tabs.tab('Parameters'), border_width=1, border_color=self.borderColor)
        self.parameters2.grid(row=0, column=1, padx=1, pady = 1, sticky='nsew')

    def create_parameters_3_frame(self):
        ''' parameters ??? frame '''
        self.parameters3 = ctk.CTkFrame(self.tabs.tab('Parameters'), border_width=1, border_color=self.borderColor)
        self.parameters3.grid(row=0, column=2, padx=1, pady = 1, sticky='nsew')

    def create_settings_1_frame(self):
        ''' settings ??? frame '''
        self.settings1 = ctk.CTkFrame(self.tabs.tab('Settings'), border_width=1, border_color=self.borderColor)
        self.settings1.grid(row=0, column=0, padx=1, pady = 1, sticky='nsew')

    def create_settings_2_frame(self):
        ''' settings ??? frame '''
        self.settings2 = ctk.CTkFrame(self.tabs.tab('Settings'), border_width=1, border_color=self.borderColor)
        self.settings2.grid(row=0, column=1, padx=1, pady = 1, sticky='nsew')

    def create_settings_3_frame(self):
        ''' settings ??? frame '''
        self.settings3 = ctk.CTkFrame(self.tabs.tab('Settings'), border_width=1, border_color=self.borderColor)
        self.settings3.grid(row=0, column=2, padx=1, pady = 1, sticky='nsew')

    def create_status_1_frame(self):
        ''' status ??? frame '''
        self.status1 = ctk.CTkFrame(self.tabs.tab('Status'), border_width=1, border_color=self.borderColor)
        self.status1.grid(row=0, column=0, padx=1, pady = 1, sticky='nsew')

    def create_status_2_frame(self):
        ''' status ??? frame '''
        self.status2 = ctk.CTkFrame(self.tabs.tab('Status'), border_width=1, border_color=self.borderColor)
        self.status2.grid(row=0, column=1, padx=1, pady = 1, sticky='nsew')

    def create_status_3_frame(self):
        ''' status ??? frame '''
        self.status3 = ctk.CTkFrame(self.tabs.tab('Status'), border_width=1, border_color=self.borderColor)
        self.status3.grid(row=0, column=2, padx=1, pady = 1, sticky='nsew')

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

app = App()
app.mainloop()
