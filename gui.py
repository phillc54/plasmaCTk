import customtkinter as ctk
import tkinter

# ctk.set_appearance_mode("light")  # Modes: system (default), light, dark
# ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
#ctk.set_default_color_theme("green")  # Themes: blue (default), dark-blue, green

class hSeparator(ctk.CTkFrame):
    def __init__(self, *args,
                 width: int = 120,
                 height: int = 2,
                 fg_color: str = '#808080',
                 **kwargs):
        super().__init__(*args, width=width, height=height, fg_color=fg_color, **kwargs)

class vSeparator(ctk.CTkFrame):
    def __init__(self, *args,
                 width: int = 2,
                 height: int = 120,
                 fg_color: str = '#808080',
                 **kwargs):
        super().__init__(*args, width=width, height=height, fg_color=fg_color, **kwargs)

class Gui():
#def make_gui(self):

    def __init__(self, parent):
        print(f"parent={parent}")
    # configure window
    # parent.title("CustomTkinter complex_example.py")
    # parent.geometry(f"{1100}x{580}")

#        self = boss

        # configure grid layout (4x4)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_columnconfigure((2, 3), weight=0)
        parent.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        parent.sidebar_frame = ctk.CTkFrame(parent, width=140, corner_radius=0)
        parent.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        parent.sidebar_frame.grid_rowconfigure(4, weight=1)
        parent.logo_label = ctk.CTkLabel(parent.sidebar_frame, text="CustomTkinter", font=ctk.CTkFont(size=20, weight="bold"))
        parent.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        parent.sidebar_button_1 = ctk.CTkButton(parent.sidebar_frame, command=parent.sidebar_button_event)
        parent.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        parent.sidebar_button_2 = ctk.CTkButton(parent.sidebar_frame, command=parent.sidebar_button_event)
        parent.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        parent.sidebar_button_3 = ctk.CTkButton(parent.sidebar_frame, command=parent.sidebar_button_event)
        parent.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)

    #    parent.separator = ctk.CTkFrame(parent.sidebar_frame, width=120, height=2, fg_color='gray')#, border_width=1, border_color="red", corner_radius=0)
        parent.separator = hSeparator(parent.sidebar_frame)#parent.sidebar_frame, width=120, height=2, fg_color='gray')#, border_width=1, border_color="red", corner_radius=0)
        parent.separator.grid(row=4, column=0)
        parent.separator.configure(width=60)

        parent.appearance_mode_label = ctk.CTkLabel(parent.sidebar_frame, text="Appearance Mode:", anchor="w")
        parent.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        parent.appearance_mode_optionemenu = ctk.CTkOptionMenu(parent.sidebar_frame, values=["Light", "Dark", "System"],
                                                                        command=parent.change_appearance_mode_event)
        parent.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        parent.scaling_label = ctk.CTkLabel(parent.sidebar_frame, text="UI Scaling:", anchor="w")
        parent.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        parent.scaling_optionemenu = ctk.CTkOptionMenu(parent.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                                command=parent.change_scaling_event)
        parent.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # create main entry and button
        parent.entry = ctk.CTkEntry(parent, placeholder_text="CTkEntry")
        parent.entry.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")

        parent.main_button_1 = ctk.CTkButton(master=parent, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        parent.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # create textbox
        parent.textbox = ctk.CTkTextbox(parent, width=250)
        parent.textbox.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        # create tabview
        parent.tabview = ctk.CTkTabview(parent, width=250)
        parent.tabview.grid(row=0, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        parent.tabview.add("CTkTabview")
        bob = parent.tabview.add("Tab 2")
        parent.tabview.add("Tab 3")
        parent.tabview.tab("CTkTabview").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        parent.tabview.tab("Tab 2").grid_columnconfigure(0, weight=1)
    #    parent.tabview.tab("Tab 2").configure(state='disabled')
    #    parent.tabview._segmented_button._buttons_dict["Tab 2"].configure(state="disabled")
    #    bob.configure(state='disabled')

    #    print(dir(parent.tabview))


        parent.optionmenu_1 = ctk.CTkOptionMenu(parent.tabview.tab("CTkTabview"), dynamic_resizing=False,
                                                        values=["Value 1", "Value 2", "Value Long Long Long"])
        parent.optionmenu_1.grid(row=0, column=0, padx=20, pady=(20, 10))
        parent.combobox_1 = ctk.CTkComboBox(parent.tabview.tab("CTkTabview"),
                                                    values=["Value 1", "Value 2", "Value Long....."])
        parent.combobox_1.grid(row=1, column=0, padx=20, pady=(10, 10))
        parent.string_input_button = ctk.CTkButton(parent.tabview.tab("CTkTabview"), text="Open CTkInputDialog",
                                                            command=parent.open_input_dialog_event)
        parent.string_input_button.grid(row=2, column=0, padx=20, pady=(10, 10))
        parent.label_tab_2 = ctk.CTkLabel(parent.tabview.tab("Tab 2"), text="CTkLabel on Tab 2")
        parent.label_tab_2.grid(row=0, column=0, padx=20, pady=20)

        # create radiobutton frame
        parent.radiobutton_frame = ctk.CTkFrame(parent)
        parent.radiobutton_frame.grid(row=0, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        parent.radio_var = tkinter.IntVar(value=0)
        parent.label_radio_group = ctk.CTkLabel(master=parent.radiobutton_frame, text="CTkRadioButton Group:")
        parent.label_radio_group.grid(row=0, column=2, columnspan=1, padx=10, pady=10, sticky="")
        parent.radio_button_1 = ctk.CTkRadioButton(master=parent.radiobutton_frame, variable=parent.radio_var, value=0)
        parent.radio_button_1.grid(row=1, column=2, pady=10, padx=20, sticky="n")
        parent.radio_button_2 = ctk.CTkRadioButton(master=parent.radiobutton_frame, variable=parent.radio_var, value=1)
        parent.radio_button_2.grid(row=2, column=2, pady=10, padx=20, sticky="n")
        parent.radio_button_3 = ctk.CTkRadioButton(master=parent.radiobutton_frame, variable=parent.radio_var, value=2)
        parent.radio_button_3.grid(row=3, column=2, pady=10, padx=20, sticky="n")

        # create slider and progressbar frame
        parent.slider_progressbar_frame = ctk.CTkFrame(parent, fg_color="transparent")
        parent.slider_progressbar_frame.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        parent.slider_progressbar_frame.grid_columnconfigure(0, weight=1)
        parent.slider_progressbar_frame.grid_rowconfigure(4, weight=1)
        parent.seg_button_1 = ctk.CTkSegmentedButton(parent.slider_progressbar_frame)
        parent.seg_button_1.grid(row=0, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        parent.progressbar_1 = ctk.CTkProgressBar(parent.slider_progressbar_frame)
        parent.progressbar_1.grid(row=1, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        parent.progressbar_2 = ctk.CTkProgressBar(parent.slider_progressbar_frame)
        parent.progressbar_2.grid(row=2, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        parent.slider_1 = ctk.CTkSlider(parent.slider_progressbar_frame, from_=0, to=1, number_of_steps=4)
        parent.slider_1.grid(row=3, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        parent.slider_2 = ctk.CTkSlider(parent.slider_progressbar_frame, orientation="vertical")
        parent.slider_2.grid(row=0, column=1, rowspan=5, padx=(10, 10), pady=(10, 10), sticky="ns")
        parent.progressbar_3 = ctk.CTkProgressBar(parent.slider_progressbar_frame, orientation="vertical")
        parent.progressbar_3.grid(row=0, column=2, rowspan=5, padx=(10, 20), pady=(10, 10), sticky="ns")

        # create scrollable frame
        parent.scrollable_frame = ctk.CTkScrollableFrame(parent, label_text="CTkScrollableFrame")
        parent.scrollable_frame.grid(row=1, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        parent.scrollable_frame.grid_columnconfigure(0, weight=1)
        parent.scrollable_frame_switches = []
        for i in range(100):
            switch = ctk.CTkSwitch(master=parent.scrollable_frame, text=f"CTkSwitch {i}")
            switch.grid(row=i, column=0, padx=10, pady=(0, 20))
            parent.scrollable_frame_switches.append(switch)

        # create checkbox and switch frame
        parent.checkbox_slider_frame = ctk.CTkFrame(parent)
        parent.checkbox_slider_frame.grid(row=1, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        parent.checkbox_1 = ctk.CTkCheckBox(master=parent.checkbox_slider_frame)
        parent.checkbox_1.grid(row=1, column=0, pady=(20, 0), padx=20, sticky="n")
        parent.checkbox_2 = ctk.CTkCheckBox(master=parent.checkbox_slider_frame)
        parent.checkbox_2.grid(row=2, column=0, pady=(20, 0), padx=20, sticky="n")
        parent.checkbox_3 = ctk.CTkCheckBox(master=parent.checkbox_slider_frame)
        parent.checkbox_3.grid(row=3, column=0, pady=20, padx=20, sticky="n")

        # set default values
        parent.sidebar_button_3.configure(state="disabled", text="Disabled CTkButton")
        parent.checkbox_3.configure(state="disabled")
        parent.checkbox_1.select()
        parent.scrollable_frame_switches[0].select()
        parent.scrollable_frame_switches[4].select()
        parent.radio_button_3.configure(state="disabled")
        parent.appearance_mode_optionemenu.set("Dark")
        parent.scaling_optionemenu.set("100%")
        parent.optionmenu_1.set("CTkOptionmenu")
        parent.combobox_1.set("CTkComboBox")
        parent.slider_1.configure(command=parent.progressbar_2.set)
        parent.slider_2.configure(command=parent.progressbar_3.set)
        parent.progressbar_1.configure(mode="indeterminnate")
        parent.progressbar_1.start()
        parent.textbox.insert("0.0", "CTkTextbox\n\n" + "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\n" * 20)
        parent.seg_button_1.configure(values=["CTkSegmentedButton", "Value 2", "Value 3"])
        parent.seg_button_1.set("Value 2")

#        return(self)
