#!/bin/python3

#import tkinter
#import tkinter.messagebox
import customtkinter as ctk

from ui import Ui

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_default_color_theme('blue')  # Themes: blue (default), dark-blue, green
        ctk.set_appearance_mode('system')  # Modes: system (default), light, dark
        self.borderColor = '#808080'

        self.userButtons = {}
        self.userButtonCodes = {}
        # self.ovrFeedValue = 
        # self.ovrRapidValue
        # self.ovrJogValue

        Ui(self)
        self.title('Phill\'s UI Test')
        self.geometry(f'{800}x{600}')
        self.after(100, self.periodic)

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
# user buttons
##############################################################################


    def torch_enable_clicked(self):
        print('Torch Enable clicked')

    def dry_run_clicked(self):
        print('Dry Run clicked')

    def user_button_setup(self):
        r = 2
        for button in range(21):
            self.userButtons[button] = ctk.CTkButton(self.mainButtons, text = f'User Button {button}')
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
# periodic
##############################################################################
    def periodic(self):
        #print('+100mS')

        self.after(100, self.periodic)



app = App()
app.mainloop()

