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
        Ui(self)
        self.title('Phill\'s UI Test')
        self.geometry(f'{600}x{580}')

#        print(dir(self))


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
        ''' set a tab state to either notmal or disabled '''
        stat = 'normal' if state else 'disabled'
        tabview._segmented_button._buttons_dict[tab].configure(state=stat)

app = App()
app.mainloop()

