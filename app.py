#!/bin/python3

import os
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
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


INI = os.path.join(os.path.expanduser('~'), 'linuxcnc/configs/0_ctk_metric/metric.ini')

class App(ctk.CTk):
    ''' the application'''
    def __init__(self):
        super().__init__()
#        print(root)
        ctk.set_default_color_theme('dark-blue')  # Themes: blue (default), dark-blue, green
        ctk.set_appearance_mode('dark')  # Modes: system (default), light, dark
        self.borderColor = '#808080'
        self.userButtons = {}
        self.userButtonCodes = {}

        self.title('Phill\'s UI Test')
        self.geometry(f'{800}x{600}+{200}+{200}')
        self.after(100, self.periodic)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        try:
            self.H = hal.component('ctk-ui')
            self.create_hal_pins(self.H)
            self.H.ready()
        except:
            pass
#FIXME   this is just for testing purposes and needs to be removed when completed
        try:
            hal.set_p('plasmac.cut-feed-rate', '1')
        except:
            pass

        self.initialDir = os.path.join(os.path.expanduser('~'), 'linuxcnc/nc_files')

        self.create_gui()
        self.create_tabs()# = Tabs(self)
        self.create_main_button_frame()
        self.create_main_control_frame()
        self.create_main_1_frame()
        self.create_main_2_frame()
        self.create_main_3_frame()
        self.create_main_4_frame()
        self.create_main_5_frame()
        self.create_conversational_buttons_frame()
        self.create_conversational_preview_frame()
        self.create_conversational_input_frame()
        self.create_parameters_1_frame()
        self.create_parameters_2_frame()
        self.create_parameters_3_frame()
        self.create_settings_1_frame()
        self.create_settings_2_frame()
        self.create_settings_3_frame()
        self.create_status_1_frame()
        self.create_status_2_frame()
        self.create_status_3_frame()

        filename = os.path.join(os.path.expanduser('~'), 'linuxcnc/nc_files/plasmac/metric_wrench.ngc')
#        self.convPreview.plot(filename, self)

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
        tabview._segmented_button._buttons_dict[tab].configure(state=stat)


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
            self.userButtons[button] = ctk.CTkButton(self.mainButtonFrame, text = f'User Button {button}')
            self.userButtons[button].grid(row=r, column=0, padx=2, pady=2, sticky='ew')
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
    def get_plot_file(self):
        filename = askopenfilename(title = 'File To Plot',
                                   initialdir = self.initialDir,
                                   filetypes = (('gcode file', '.ngc .tap .nc'), ('all files', '.*')))
        self.plot(filename)

    def plot(self, filename):
        self.ax.clear()
        self.initialDir = os.path.dirname(filename)
        print(f'filename:{filename}   self.initialDir:{self.initialDir}')
        self.pg.load(filename)
        for point in self.pg.canon.points:
            if point['shape'] == 'arc':
                color = '#00008f'
                linestyle = '-'
                patch = patches.Arc((point['centerX'],
                                     point['centerY']),
                                     width=point['radius'] * 2,
                                     height=point['radius'] * 2,
                                     theta1=point['startAngle'],
                                     theta2=point['endAngle'],
                                     edgecolor=color,
                                     facecolor='none',
                                     lw=1,
                                     linestyle=linestyle)
            else:
                linestyle = '-' if point['shape'] == 'line' else ':'
                color = '#0000ff' if point['shape'] == 'line' else '#00001f'
                closed = True if point['points'][0] == point['points'][-1] else False
                patch = patches.Polygon(point['points'],
                                        closed=closed,
                                        edgecolor=color,
                                        facecolor='none',
                                        lw=1,
                                        linestyle=linestyle)
            self.ax.add_patch(patch)
        self.ax.plot()
        self.ax.set_title(os.path.basename(filename), color='orange')
        plt.show()
        self.canvas.draw()


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
        self.create_conversational_buttons_frame()
        self.create_conversational_preview_frame()
        self.create_conversational_input_frame()
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
        self.tabs = ctk.CTkTabview(self, height=1, anchor='sw')
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
        self.torchEnableBtn = ctk.CTkButton(self.mainButtonFrame, text = 'Torch Enable', command=self.torch_enable_clicked)
        self.torchEnableBtn.grid(row=0, column=0, padx=2, pady=(0, 2), sticky='new')
        self.user_button_setup()

    def create_main_control_frame(self):
        ''' main tab control frame '''
        self.mainControl = ctk.CTkFrame(self.tabs.tab('Main'), border_width=1, border_color=self.borderColor)
        self.mainControl.grid(row=0, column=1, padx=1, pady = 1, sticky='nsew')
        self.mainControl.grid_rowconfigure((1, 2, 3, 4), weight=6)
        self.mainControl.grid_rowconfigure((5, 6, 7), weight=1)
        self.mainControl.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.mainControlLbl = ctk.CTkLabel(self, text='Cycle Panel', height=16, anchor='n')#, fg_color='gray', corner_radius=1, height=18, text_color='#404040')
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

    def create_conversational_buttons_frame(self):
        ''' conversational button frame '''
        self.convButtons = ctk.CTkFrame(self.tabs.tab("Conversational"), border_width=1, border_color=self.borderColor, height=40)
        self.convButtons.grid(row=0, column=0, columnspan=2, padx=1, pady = 1, sticky='nsew')

    def create_conversational_input_frame(self):
        ''' conversational input frame '''
        self.convInput = ctk.CTkFrame(self.tabs.tab("Conversational"), border_width=1, border_color=self.borderColor, width=120)
        self.convInput.grid(row=1, column=0, padx=1, pady = 1, sticky='nsew')
        plot_button = ctk.CTkButton(master = self.convInput,
                             text = 'Plot',
                             command = self.get_plot_file)
        plot_button.pack(side=tk.TOP, fill=tk.X, expand=True, padx=3, pady=3, anchor=tk.N)

    def create_conversational_preview_frame(self):
        ''' conversational preview frame '''
        self.convPreview = ctk.CTkFrame(self.tabs.tab("Conversational"), border_width=1, border_color=self.borderColor)
        self.convPreview.grid(row=1, column=1, padx=1, pady = 1, sticky='nsew')

        plt.style.use("dark_background")

        fig = plt.Figure(figsize=(1,1))
        fig.set_facecolor(self.rgb_to_hex(33, 33, 33))
        fig.subplots_adjust(bottom=0.06, left=0.08, top=0.95, right=0.99)

        self.ax = fig.add_subplot(111)
        self.ax.set_facecolor(self.rgb_to_hex(33, 33, 33))
        self.ax.axis('equal')
        self.ax.tick_params(colors=self.rgb_to_hex(233, 233, 233), which='both')
        self.ax.spines['left'].set_color(self.rgb_to_hex(233, 233, 233))
        self.ax.spines['left'].set_lw(1)
        self.ax.spines['bottom'].set_color(self.rgb_to_hex(233, 233, 233))
        self.ax.spines['bottom'].set_lw(1)
        self.ax.spines['top'].set_lw(0)
        self.ax.spines['right'].set_lw(0)
        self.ax.set_title('No File', color='orange')

        self.canvas = FigureCanvasTkAgg(fig, master=self.convPreview)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=3, pady=(3,0))#(3,10))

        toolbar = NavigationToolbar2Tk(self.canvas, self.convPreview)
        toolbar.pack(padx=3, pady=(0,4))
        toolbar.update()

        self.canvas.draw()
        self.plotted = False
        self.initialDir = os.path.join(os.path.expanduser('~'), 'linuxcnc/nc_files')
        self.pg = PlotGenerator(INI)

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
    ''' use this class instead of glcanon as we are only interested in points from:
        arc_feed
        straight_feed
        straight_traverse '''

    def __init__(self):
        self.points = []

    def __getattr__(self, attr):
#        print(f'attr: {attr}')

        def set_units(f):
            #FIXME we need to set units properly here
            if isinstance(f, float):
                return round(f * 25.4, 4)
            return f

        def inner(*args):
#            print(f'attr: {attr}   args: {args}')
            if attr not in ['arc_feed', 'straight_feed', 'straight_traverse']:
                return
            args = list(map(set_units, args))
            if len(self.points):
                if self.points[-1]['shape'] == 'rapid' or self.points[-1]['shape'] == 'line':
                    startX = self.points[-1]['points'][-1][0]
                    startY = self.points[-1]['points'][-1][1]
                else:
                    startX = self.points[-1]['endX']
                    startY = self.points[-1]['endY']
            else:
                startX = 0.0
                startY = 0.0
            endX = args[0]
            endY = args[1]
            if attr == 'arc_feed':
                if len(self.points):
                    centerX = args[2]
                    centerY = args[3]
                    radius = round(math.sqrt((centerX - endX)**2 + (centerY - endY)**2), 4)
                    if args[4] > 0:
                        dir = args[4]
                        startAngle = round(math.degrees(math.atan2(startY - centerY, startX - centerX)) * dir, 4)
                        endAngle = round(math.degrees(math.atan2(endY - centerY, endX - centerX)) * dir, 4)
                    else:
                        dir = args[4] * -1
                        startAngle = round(math.degrees(math.atan2(endY - centerY, endX - centerX)) * dir, 4)
                        endAngle = round(math.degrees(math.atan2(startY - centerY, startX - centerX)) * dir, 4)
#                    shape = 'circle' if args[0] == startX and args[1] == startY else 'arc'
                    if args[0] == startX and args[1] == startY:
#                    if shape == 'circle':
                        endAngle += 360
                    self.points.append({#'shape': shape,
                                        'shape': 'arc',
                                        'endX': endX,
                                        'endY': endY,
                                        'centerX': centerX,
                                        'centerY': centerY,
                                        'radius': radius,
                                        'startAngle': startAngle,
                                        'endAngle': endAngle})
                else:
                    print(f'arc without a previous move: {args}')
            else:
                shape = 'line' if attr == 'straight_feed' else 'rapid'
                if len(self.points) and self.points[-1]['shape'] == shape:
                        self.points[-1]['points'].append((args[0], args[1]))
                else:
                    self.points.append({'shape': shape,
                                        'points': [(startX, startY), (args[0], args[1])]})

        return inner

    def next_line(self, linecode):
        pass

    # These can't return None...
    def get_external_length_units(self):
        return 1.0

    def get_external_angular_units(self):
        return 1.0

#    def get_axis_mask(self):
#        return 7 # (x y z)

    def get_axis_mask(self):
        return 15 # (x y z a)

    def get_block_delete(self):
        return False

    def get_tool(self, pocket):
        return -1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0

class PlotGenerator:
    def __init__(self, inifile):
        self.inifile = linuxcnc.ini(inifile)
        self.inifile_path = os.path.split(inifile)[0]

    def load(self, filename = None):
#        linuxcnc.command().task_plan_synch()
#        s = linuxcnc.stat()
#        s.poll()
#        unitcode = 'G%d' % (20 + (s.linear_units == 1))
#        initcode = self.inifile.find('RS274NGC', 'RS274NGC_STARTUP_CODE') or ''
        unitcode = 'G21'
        initcode = 'G21 G40 G49 G80 G90 G92.1 G94 G97 M52P1'
        self.canon = Canon()
        parameter = tempfile.NamedTemporaryFile()
        self.canon.parameter_file = parameter.name
        result, seq = gcode.parse(filename, self.canon, unitcode, initcode)
        if result > gcode.MIN_ERROR:
            print(f'OOPS...\n{filename}\n{gcode.strerror(result)}')
            #raise SystemExit(gcode.strerror(result))


App()

