#!/bin/python3

import customtkinter as ctk
from types import SimpleNamespace

# widget namespace
W = SimpleNamespace()

class App(ctk.CTk):
    ''' the application'''
    def __init__(self):
        super().__init__()
        ctk.set_default_color_theme('blue')  # Themes: blue (default), dark-blue, green
        ctk.set_appearance_mode('system')  # Modes: system (default), light, dark
        self.borderColor = '#808080'
        W.userButtons = {}
        self.userButtonCodes = {}

        self.title('Phill\'s UI Test')
        self.geometry(f'{800}x{600}')
        self.after(100, self.periodic)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        W.tabs = Tabs(self)
        W.mainButtonFrame = MainButtons(self, W.tabs.tab("Main"))
        W.mainControl = MainControl(self, W.tabs.tab("Main"))
        W.main1 = Main1Frame(self, W.tabs.tab("Main"))
        W.main2 = Main2Frame(self, W.tabs.tab("Main"))
        W.main3 = Main3Frame(self, W.tabs.tab("Main"))
        W.main4 = Main4Frame(self, W.tabs.tab("Main"))
        W.main5 = Main5Frame(self, W.tabs.tab("Main"))
        W.convButtons = ConvButtons(self, W.tabs.tab("Conversational"))
        W.convInput = ConvInput(self, W.tabs.tab("Conversational"))
        W.convPreview = ConvPreview(self, W.tabs.tab("Conversational"))
        W.parameters1 = Parameters1(self, W.tabs.tab("Parameters"))
        W.parameters2 = Parameters2(self, W.tabs.tab("Parameters"))
        W.parameters3 = Parameters3(self, W.tabs.tab("Parameters"))
        W.settings1 = Settings1(self, W.tabs.tab("Settings"))
        W.settings2 = Settings2(self, W.tabs.tab("Settings"))
        W.settings3 = Settings3(self, W.tabs.tab("Settings"))
        W.status1 = Status1(self, W.tabs.tab("Status"))
        W.status2 = Status2(self, W.tabs.tab("Status"))
        W.status3 = Status3(self, W.tabs.tab("Status"))

        print(dir(W))

        self.mainloop()

##############################################################################
# testing
##############################################################################
    def open_input_dialog_event(self):
        dialog = ctk.CTkInputDialog(text='Type in a number:', title='CTkInputDialog')
        print('CTkInputDialog:', dialog.get_input())

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
        W.ovrFeedLbl.configure(text=f'Feed {value:.0f}%')

    def ovr_feed_reset(self, event, default=100):
        W.ovrFeed.set(default)
        W.ovrFeedLbl.configure(text=f'Feed {default:.0f}%')

    def ovr_rapid_changed(self, value):
        W.ovrRapidLbl.configure(text=f'Rapid {value:.0f}%')

    def ovr_rapid_reset(self, event, default=100):
        W.ovrRapid.set(default)
        W.ovrRapidLbl.configure(text=f'Rapid {default:.0f}%')

    def ovr_jog_changed(self, value):
        print(value)
        W.ovrJogLbl.configure(text=f'Jog {value:.0f}%')

    def ovr_jog_reset(self, event, default=100):
        W.ovrJog.set(default)
        W.ovrJogLbl.configure(text=f'Jog {default:.0f}%')


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
            W.userButtons[button] = ctk.CTkButton(W.mainButtonFrame, text = f'User Button {button}')
            W.userButtons[button].grid(row=r, column=0, padx=2, pady=2, sticky='ew')
            self.userButtonCodes[button] = f'blah {button}'
            W.userButtons[button].bind('<ButtonPress-1>', lambda event: self.user_button_pressed(int(event.widget.cget('text').rsplit(' ', 1)[1])))
            W.userButtons[button].bind('<ButtonRelease-1>', lambda event: self.user_button_released(int(event.widget.cget('text').rsplit(' ', 1)[1])))
            r += 1

    def user_button_pressed(self, button):
        print(f'User Button #{button:0>{2}}  pressed, code is {self.userButtonCodes[button]}')

    def user_button_released(self, button):
        print(f'User Button #{button:0>{2}} released, code is {self.userButtonCodes[button]}')



##############################################################################
# periodic
##############################################################################
    def periodic(self):
        #print('+100mS')

        self.after(100, self.periodic)

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

class Tabs(ctk.CTkTabview):
    ''' tabview as the main window '''
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(height=1, anchor='sw')
        self.add('Main')
        self.tab('Main').grid_rowconfigure((0, 1), weight=1)
        self.tab('Main').grid_columnconfigure((1, 2, 3), weight=1)
        self.add('Conversational')
        self.tab('Conversational').grid_rowconfigure(1, weight=1)
        self.tab('Conversational').grid_columnconfigure(1, weight=1)
        self.add('Parameters')
        self.tab('Parameters').grid_rowconfigure(0, weight=1)
        self.tab('Parameters').grid_columnconfigure((0, 1, 2), weight=1)
        self.add('Settings')
        self.tab('Settings').grid_rowconfigure(0, weight=1)
        self.tab('Settings').grid_columnconfigure((0, 1, 2), weight=1)
        self.add('Status')
        self.tab('Status').grid_rowconfigure(0, weight=1)
        self.tab('Status').grid_columnconfigure((0, 1, 2), weight=1)
        # large width is a kludge to make buttons appear homogeneous
        for button in self._segmented_button._buttons_dict:
            self._segmented_button._buttons_dict[button].configure(width=1000)
        self.grid(row=1, column=1, padx=0, sticky='nsew')

class MainButtons(ctk.CTkFrame):
    ''' main tab button frame '''
    def __init__(self, root, parent):
        super().__init__(parent)
        self.configure(border_width=1, border_color=root.borderColor, width=146)
        self.grid(row=0, column=0, rowspan=2, padx=1, pady = 1, sticky='nsew')
        self.grid_rowconfigure((1, 2), weight=1)
        W.mainButtonLbl = ctk.CTkLabel(self, text='Button Panel', height=16, anchor='n')#, fg_color='gray', corner_radius=1, height=18, text_color='#404040')
        W.mainButtonLbl.grid(row=0, column=0, padx=4, pady=(1, 0), sticky='new')
        W.mainButtonFrame = ctk.CTkScrollableFrame(self, width=144, fg_color='transparent')
        W.mainButtonFrame.grid(row=1, column=0, rowspan=2, padx=2, pady=(0, 2), sticky='nsew')
        W.torchEnableBtn = ctk.CTkButton(W.mainButtonFrame, text = 'Torch Enable', command=App.torch_enable_clicked)
        W.torchEnableBtn.grid(row=0, column=0, padx=2, pady=(0, 2), sticky='new')
        # root.dryRunBtn = ctk.CTkButton(root.mainButtonFrame, text = 'Dry Run', command=root.dry_run_clicked)
        # root.dryRunBtn.grid(row=1, column=0, padx=2, pady=2, sticky='ew')
        App.user_button_setup(root)

class MainControl(ctk.CTkFrame):
    ''' main tab control frame '''
    def __init__(self, root, parent):
        super().__init__(parent)
        self.configure(border_width=1, border_color=root.borderColor)
        self.grid(row=0, column=1, padx=1, pady = 1, sticky='nsew')
        self.grid_rowconfigure((1, 2, 3, 4), weight=6)
        self.grid_rowconfigure((5, 6, 7), weight=1)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        W.mainControlLbl = ctk.CTkLabel(self, text='Cycle Panel', height=16, anchor='n')#, fg_color='gray', corner_radius=1, height=18, text_color='#404040')
        W.mainControlLbl.grid(row=0, column=0, columnspan=4, padx=4, pady=(1, 0), sticky='new')
        W.cycleStart = ctk.CTkButton(self, text='Cycle Start', command = root.run_clicked)
        W.cycleStart.grid(row=1, column=0, rowspan=2, columnspan=2, padx=(3, 1), pady=0, sticky='nsew')
        W.cycleStop = ctk.CTkButton(self, text='Cycle Stop', command = root.stop_clicked)
        W.cycleStop.grid(row=1, column=2, rowspan=2, columnspan=2, padx=(1, 3), pady=0, sticky='nsew')
        W.cyclePause = ctk.CTkButton(self, text='Cycle Pause', command = root.pause_clicked)
        W.cyclePause.grid(row=3, column=0, rowspan=2, columnspan=2, padx=(3, 1), pady = (2, 0), sticky='nsew')
        W.dryRunBtn = ctk.CTkButton(self, text = 'Dry Run', command=root.dry_run_clicked)
        W.dryRunBtn.grid(row=3, column=2, rowspan=2, columnspan=2, padx=(1, 3), pady=(2, 0), sticky='nsew')
        W.ovrFeed = ctk.CTkSlider(self, from_=50, to=120, number_of_steps=120-50, command=root.ovr_feed_changed)
        W.ovrFeed.set(100)
        W.ovrFeed.grid(row=5, column=0, columnspan=3, padx=(1, 3), pady=(12, 0), sticky='ew')
        W.ovrFeedLbl = ctk.CTkLabel(self, text=f'Feed {W.ovrFeed.get():.0f}%', anchor='e')
        W.ovrFeedLbl.grid(row=5, column=3, padx=(0,2), pady=(12, 0), sticky='ew')
        W.ovrFeedLbl.bind('<ButtonPress-1>', root.ovr_feed_reset)
        W.ovrRapid = ctk.CTkSlider(self, from_=50, to=100, number_of_steps=50, command=root.ovr_rapid_changed)
        W.ovrRapid.set(100)
        W.ovrRapid.grid(row=6, column=0, columnspan=3, padx=(1, 3), pady=(12, 0), sticky='ew')
        W.ovrRapidLbl = ctk.CTkLabel(self, text=f'Rapid {W.ovrRapid.get():.0f}%', anchor='e')
        W.ovrRapidLbl.grid(row=6, column=3, padx=(0,2), pady=(12, 0), sticky='ew')
        W.ovrRapidLbl.bind('<ButtonPress-1>', root.ovr_rapid_reset)
        W.ovrJog = ctk.CTkSlider(self, from_=50, to=100, number_of_steps=50, command=root.ovr_jog_changed)
        W.ovrJog.set(100)
        W.ovrJog.grid(row=7, column=0, columnspan=3, padx=(1, 3), pady=(12, 6), sticky='ew')
        W.ovrJogLbl = ctk.CTkLabel(self, text=f'Jog {W.ovrJog.get():.0f}%', anchor='e')
        W.ovrJogLbl.grid(row=7, column=3, padx=(0,2), pady=(12, 6), sticky='ew')
        W.ovrJogLbl.bind('<ButtonPress-1>', root.ovr_jog_reset)

class Main1Frame(ctk.CTkFrame):
    ''' main tab ??? frame '''
    def __init__(self, root, parent):
        super().__init__(parent)
        self.configure(border_width=1, border_color=root.borderColor)
        self.grid(row=1, column=1, padx=1, pady = 1, sticky='nsew')

class Main2Frame(ctk.CTkFrame):
    ''' main tab ??? frame '''
    def __init__(self, root, parent):
        super().__init__(parent)
        self.configure(border_width=1, border_color=root.borderColor)
        self.grid(row=0, column=2, padx=1, pady = 1, sticky='nsew')

class Main3Frame(ctk.CTkFrame):
    ''' main tab ??? frame '''
    def __init__(self, root, parent):
        super().__init__(parent)
        self.configure(border_width=1, border_color=root.borderColor)
        self.grid(row=1, column=2, padx=1, pady = 1, sticky='nsew')

class Main4Frame(ctk.CTkFrame):
    ''' main tab ??? frame '''
    def __init__(self, root, parent):
        super().__init__(parent)
        self.configure(border_width=1, border_color=root.borderColor)
        self.grid(row=0, column=3, padx=1, pady = 1, sticky='nsew')

class Main5Frame(ctk.CTkFrame):
    ''' main tab ??? frame '''
    def __init__(self, root, parent):
        super().__init__(parent)
        self.configure(border_width=1, border_color=root.borderColor)
        self.grid(row=1, column=3, padx=1, pady = 1, sticky='nsew')

class ConvButtons(ctk.CTkFrame):
    ''' conversational button frame '''
    def __init__(self, root, parent):
        super().__init__(parent)
        self.configure(border_width=1, border_color=root.borderColor)
        self.grid(row=0, column=0, columnspan=2, padx=1, pady = 1, sticky='nsew')

class ConvInput(ctk.CTkFrame):
    ''' conversational input frame '''
    def __init__(self, root, parent):
        super().__init__(parent)
        self.configure(border_width=1, border_color=root.borderColor)
        self.grid(row=1, column=0, padx=1, pady = 1, sticky='nsew')

class ConvPreview(ctk.CTkFrame):
    ''' conversational preview frame '''
    def __init__(self, root, parent):
        super().__init__(parent)
        self.configure(border_width=1, border_color=root.borderColor)
        self.grid(row=1, column=1, padx=1, pady = 1, sticky='nsew')

class Parameters1(ctk.CTkFrame):
    ''' parameters ??? frame '''
    def __init__(self, root, parent):
        super().__init__(parent)
        self.configure(border_width=1, border_color=root.borderColor)
        self.grid(row=0, column=0, padx=1, pady = 1, sticky='nsew')

class Parameters2(ctk.CTkFrame):
    ''' parameters ??? frame '''
    def __init__(self, root, parent):
        super().__init__(parent)
        self.configure(border_width=1, border_color=root.borderColor)
        self.grid(row=0, column=1, padx=1, pady = 1, sticky='nsew')

class Parameters3(ctk.CTkFrame):
    ''' parameters ??? frame '''
    def __init__(self, root, parent):
        super().__init__(parent)
        self.configure(border_width=1, border_color=root.borderColor)
        self.grid(row=0, column=2, padx=1, pady = 1, sticky='nsew')

class Settings1(ctk.CTkFrame):
    ''' settings ??? frame '''
    def __init__(self, root, parent):
        super().__init__(parent)
        self.configure(border_width=1, border_color=root.borderColor)
        self.grid(row=0, column=0, padx=1, pady = 1, sticky='nsew')

class Settings2(ctk.CTkFrame):
    ''' settings ??? frame '''
    def __init__(self, root, parent):
        super().__init__(parent)
        self.configure(border_width=1, border_color=root.borderColor)
        self.grid(row=0, column=1, padx=1, pady = 1, sticky='nsew')

class Settings3(ctk.CTkFrame):
    ''' settings ??? frame '''
    def __init__(self, root, parent):
        super().__init__(parent)
        self.configure(border_width=1, border_color=root.borderColor)
        self.grid(row=0, column=2, padx=1, pady = 1, sticky='nsew')

class Status1(ctk.CTkFrame):
    ''' status ??? frame '''
    def __init__(self, root, parent):
        super().__init__(parent)
        self.configure(border_width=1, border_color=root.borderColor)
        self.grid(row=0, column=0, padx=1, pady = 1, sticky='nsew')

class Status2(ctk.CTkFrame):
    ''' status ??? frame '''
    def __init__(self, root, parent):
        super().__init__(parent)
        self.configure(border_width=1, border_color=root.borderColor)
        self.grid(row=0, column=1, padx=1, pady = 1, sticky='nsew')

class Status3(ctk.CTkFrame):
    ''' status ??? frame '''
    def __init__(self, root, parent):
        super().__init__(parent)
        self.configure(border_width=1, border_color=root.borderColor)
        self.grid(row=0, column=2, padx=1, pady = 1, sticky='nsew')

App()
