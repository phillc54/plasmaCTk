import customtkinter as ctk

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

class Ui():
    def __init__(self, root):

        # configure grid layout (3x3)
        root.grid_columnconfigure(1, weight=1)
#        root.grid_columnconfigure((0, 2), weight=0)
        root.grid_rowconfigure(1, weight=1)
#        root.grid_rowconfigure((0, 2), weight=0)

        # main tabview
        root.mTab = ctk.CTkTabview(root, anchor='sw')
        root.mTab.grid(row=1, column=1, padx=0, sticky="nsew")
        root.mTab.add("Main")
        root.mTab.add("Conversational")
        root.mTab.add("Parameters")
        root.mTab.add("Settings")
        root.mTab.add("Status")
        # large width is kludge to make buttons appear homogeneous
        for b in root.mTab._segmented_button._buttons_dict:
            root.mTab._segmented_button._buttons_dict[b].configure(width=1000)

        # main tab
        root.mTab.tab('Main').grid_rowconfigure((0, 1), weight=1)
        root.mTab.tab('Main').grid_columnconfigure((1, 2, 3), weight=1)
        root.mbFrame = ctk.CTkFrame(root.mTab.tab('Main'), border_width=1, border_color=root.borderColor)
        root.mbFrame.grid(row=0, column=0, rowspan=2, padx=1, pady = 1, sticky="nsew")
        root.mgFrame = ctk.CTkFrame(root.mTab.tab('Main'), border_width=1, border_color=root.borderColor)
        root.mgFrame.grid(row=0, column=1, padx=1, pady = 1, sticky="nsew")
        root.mcFrame = ctk.CTkFrame(root.mTab.tab('Main'), border_width=1, border_color=root.borderColor)
        root.mcFrame.grid(row=1, column=1, padx=1, pady = 1, sticky="nsew")
        root.m1Frame = ctk.CTkFrame(root.mTab.tab('Main'), border_width=1, border_color=root.borderColor)
        root.m1Frame.grid(row=0, column=2, padx=1, pady = 1, sticky="nsew")
        root.m2Frame = ctk.CTkFrame(root.mTab.tab('Main'), border_width=1, border_color=root.borderColor)
        root.m2Frame.grid(row=1, column=2, padx=1, pady = 1, sticky="nsew")
        root.m3Frame = ctk.CTkFrame(root.mTab.tab('Main'), border_width=1, border_color=root.borderColor)
        root.m3Frame.grid(row=0, column=3, padx=1, pady = 1, sticky="nsew")
        root.m4Frame = ctk.CTkFrame(root.mTab.tab('Main'), border_width=1, border_color=root.borderColor)
        root.m4Frame.grid(row=1, column=3, padx=1, pady = 1, sticky="nsew")

        # conversational tab
        root.mTab.tab('Conversational').grid_rowconfigure(1, weight=1)
        root.mTab.tab('Conversational').grid_columnconfigure(1, weight=1)
        root.cbFrame = ctk.CTkFrame(root.mTab.tab('Conversational'), border_width=1, border_color=root.borderColor)
        root.cbFrame.grid(row=0, column=0, columnspan=2, padx=1, pady = 1, sticky="nsew")
        root.ciFrame = ctk.CTkFrame(root.mTab.tab('Conversational'), border_width=1, border_color=root.borderColor)
        root.ciFrame.grid(row=1, column=0, padx=1, pady = 1, sticky="nsew")
        root.cpFrame = ctk.CTkFrame(root.mTab.tab('Conversational'), border_width=1, border_color=root.borderColor)
        root.cpFrame.grid(row=1, column=1, padx=1, pady = 1, sticky="nsew")

        # parameters tab
        root.mTab.tab('Parameters').grid_rowconfigure(0, weight=1)
        root.mTab.tab('Parameters').grid_columnconfigure((0, 1, 2), weight=1)
        root.p1Frame = ctk.CTkFrame(root.mTab.tab('Parameters'), border_width=1, border_color=root.borderColor)
        root.p1Frame.grid(row=0, column=0, padx=1, pady = 1, sticky="nsew")
        root.p2Frame = ctk.CTkFrame(root.mTab.tab('Parameters'), border_width=1, border_color=root.borderColor)
        root.p2Frame.grid(row=0, column=1, padx=1, pady = 1, sticky="nsew")
        root.p3Frame = ctk.CTkFrame(root.mTab.tab('Parameters'), border_width=1, border_color=root.borderColor)
        root.p3Frame.grid(row=0, column=2, padx=1, pady = 1, sticky="nsew")

        # settings tab
        root.mTab.tab('Settings').grid_rowconfigure(0, weight=1)
        root.mTab.tab('Settings').grid_columnconfigure((0, 1, 2), weight=1)
        root.s1Frame = ctk.CTkFrame(root.mTab.tab('Settings'), border_width=1, border_color=root.borderColor)
        root.s1Frame.grid(row=0, column=0, padx=1, pady = 1, sticky="nsew")
        root.s2Frame = ctk.CTkFrame(root.mTab.tab('Settings'), border_width=1, border_color=root.borderColor)
        root.s2Frame.grid(row=0, column=1, padx=1, pady = 1, sticky="nsew")
        root.s3Frame = ctk.CTkFrame(root.mTab.tab('Settings'), border_width=1, border_color=root.borderColor)
        root.s3Frame.grid(row=0, column=2, padx=1, pady = 1, sticky="nsew")

        # status tab
        root.mTab.tab('Status').grid_rowconfigure(0, weight=1)
        root.mTab.tab('Status').grid_columnconfigure((0, 1, 2), weight=1)
        root.st1Frame = ctk.CTkFrame(root.mTab.tab('Status'), border_width=1, border_color=root.borderColor)
        root.st1Frame.grid(row=0, column=0, padx=1, pady = 1, sticky="nsew")
        root.st2Frame = ctk.CTkFrame(root.mTab.tab('Status'), border_width=1, border_color=root.borderColor)
        root.st2Frame.grid(row=0, column=1, padx=1, pady = 1, sticky="nsew")
        root.st3Frame = ctk.CTkFrame(root.mTab.tab('Status'), border_width=1, border_color=root.borderColor)
        root.st3Frame.grid(row=0, column=2, padx=1, pady = 1, sticky="nsew")




        print(dir(root.mTab.cget))






# class Gui():
# #def make_gui(self):

#     def __init__(self, root):
#         print(f"root={root}")
#     # configure window
#     # root.title("CustomTkinter complex_example.py")
#     # root.geometry(f"{1100}x{580}")

# #        self = boss

#         # configure grid layout (4x4)
#         root.grid_columnconfigure(1, weight=1)
#         root.grid_columnconfigure((2, 3), weight=0)
#         root.grid_rowconfigure((0, 1, 2), weight=1)

#         # create sidebar frame with widgets
#         root.sidebar_frame = ctk.CTkFrame(root, width=140, corner_radius=0)
#         root.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
#         root.sidebar_frame.grid_rowconfigure(4, weight=1)
#         root.logo_label = ctk.CTkLabel(root.sidebar_frame, text="CustomTkinter", font=ctk.CTkFont(size=20, weight="bold"))
#         root.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
#         root.sidebar_button_1 = ctk.CTkButton(root.sidebar_frame, command=root.sidebar_button_event)
#         root.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
#         root.sidebar_button_2 = ctk.CTkButton(root.sidebar_frame, command=root.sidebar_button_event)
#         root.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
#         root.sidebar_button_3 = ctk.CTkButton(root.sidebar_frame, command=root.sidebar_button_event)
#         root.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)

#     #    root.separator = ctk.CTkFrame(root.sidebar_frame, width=120, height=2, fg_color='gray')#, border_width=1, border_color="red", corner_radius=0)
#         root.separator = hSeparator(root.sidebar_frame)#root.sidebar_frame, width=120, height=2, fg_color='gray')#, border_width=1, border_color="red", corner_radius=0)
#         root.separator.grid(row=4, column=0)
#         root.separator.configure(width=60)

#         root.appearance_mode_label = ctk.CTkLabel(root.sidebar_frame, text="Appearance Mode:", anchor="w")
#         root.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
#         root.appearance_mode_optionemenu = ctk.CTkOptionMenu(root.sidebar_frame, values=["Light", "Dark", "System"],
#                                                                         command=root.change_appearance_mode_event)
#         root.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
#         root.scaling_label = ctk.CTkLabel(root.sidebar_frame, text="UI Scaling:", anchor="w")
#         root.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
#         root.scaling_optionemenu = ctk.CTkOptionMenu(root.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
#                                                                 command=root.change_scaling_event)
#         root.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

#         # create main entry and button
#         root.entry = ctk.CTkEntry(root, placeholder_text="CTkEntry")
#         root.entry.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")

#         root.main_button_1 = ctk.CTkButton(master=root, fg_color="transroot", border_width=2, text_color=("gray10", "#DCE4EE"))
#         root.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

#         # create textbox
#         root.textbox = ctk.CTkTextbox(root, width=250)
#         root.textbox.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

#         # create tabview
#         root.tabview = ctk.CTkTabview(root, width=250)
#         root.tabview.grid(row=0, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
#         root.tabview.add("CTkTabview")
#         bob = root.tabview.add("Tab 2")
#         root.tabview.add("Tab 3")
#         root.tabview.tab("CTkTabview").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
#         root.tabview.tab("Tab 2").grid_columnconfigure(0, weight=1)
#     #    root.tabview.tab("Tab 2").configure(state='disabled')
#     #    root.tabview._segmented_button._buttons_dict["Tab 2"].configure(state="disabled")
#     #    bob.configure(state='disabled')

#     #    print(dir(root.tabview))


#         root.optionmenu_1 = ctk.CTkOptionMenu(root.tabview.tab("CTkTabview"), dynamic_resizing=False,
#                                                         values=["Value 1", "Value 2", "Value Long Long Long"])
#         root.optionmenu_1.grid(row=0, column=0, padx=20, pady=(20, 10))
#         root.combobox_1 = ctk.CTkComboBox(root.tabview.tab("CTkTabview"),
#                                                     values=["Value 1", "Value 2", "Value Long....."])
#         root.combobox_1.grid(row=1, column=0, padx=20, pady=(10, 10))
#         root.string_input_button = ctk.CTkButton(root.tabview.tab("CTkTabview"), text="Open CTkInputDialog",
#                                                             command=root.open_input_dialog_event)
#         root.string_input_button.grid(row=2, column=0, padx=20, pady=(10, 10))
#         root.label_tab_2 = ctk.CTkLabel(root.tabview.tab("Tab 2"), text="CTkLabel on Tab 2")
#         root.label_tab_2.grid(row=0, column=0, padx=20, pady=20)

#         # create radiobutton frame
#         root.radiobutton_frame = ctk.CTkFrame(root)
#         root.radiobutton_frame.grid(row=0, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
#         root.radio_var = tkinter.IntVar(value=0)
#         root.label_radio_group = ctk.CTkLabel(master=root.radiobutton_frame, text="CTkRadioButton Group:")
#         root.label_radio_group.grid(row=0, column=2, columnspan=1, padx=10, pady=10, sticky="")
#         root.radio_button_1 = ctk.CTkRadioButton(master=root.radiobutton_frame, variable=root.radio_var, value=0)
#         root.radio_button_1.grid(row=1, column=2, pady=10, padx=20, sticky="n")
#         root.radio_button_2 = ctk.CTkRadioButton(master=root.radiobutton_frame, variable=root.radio_var, value=1)
#         root.radio_button_2.grid(row=2, column=2, pady=10, padx=20, sticky="n")
#         root.radio_button_3 = ctk.CTkRadioButton(master=root.radiobutton_frame, variable=root.radio_var, value=2)
#         root.radio_button_3.grid(row=3, column=2, pady=10, padx=20, sticky="n")

#         # create slider and progressbar frame
#         root.slider_progressbar_frame = ctk.CTkFrame(root, fg_color="transroot")
#         root.slider_progressbar_frame.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
#         root.slider_progressbar_frame.grid_columnconfigure(0, weight=1)
#         root.slider_progressbar_frame.grid_rowconfigure(4, weight=1)
#         root.seg_button_1 = ctk.CTkSegmentedButton(root.slider_progressbar_frame)
#         root.seg_button_1.grid(row=0, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
#         root.progressbar_1 = ctk.CTkProgressBar(root.slider_progressbar_frame)
#         root.progressbar_1.grid(row=1, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
#         root.progressbar_2 = ctk.CTkProgressBar(root.slider_progressbar_frame)
#         root.progressbar_2.grid(row=2, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
#         root.slider_1 = ctk.CTkSlider(root.slider_progressbar_frame, from_=0, to=1, number_of_steps=4)
#         root.slider_1.grid(row=3, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
#         root.slider_2 = ctk.CTkSlider(root.slider_progressbar_frame, orientation="vertical")
#         root.slider_2.grid(row=0, column=1, rowspan=5, padx=(10, 10), pady=(10, 10), sticky="ns")
#         root.progressbar_3 = ctk.CTkProgressBar(root.slider_progressbar_frame, orientation="vertical")
#         root.progressbar_3.grid(row=0, column=2, rowspan=5, padx=(10, 20), pady=(10, 10), sticky="ns")

#         # create scrollable frame
#         root.scrollable_frame = ctk.CTkScrollableFrame(root, label_text="CTkScrollableFrame")
#         root.scrollable_frame.grid(row=1, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
#         root.scrollable_frame.grid_columnconfigure(0, weight=1)
#         root.scrollable_frame_switches = []
#         for i in range(100):
#             switch = ctk.CTkSwitch(master=root.scrollable_frame, text=f"CTkSwitch {i}")
#             switch.grid(row=i, column=0, padx=10, pady=(0, 20))
#             root.scrollable_frame_switches.append(switch)

#         # create checkbox and switch frame
#         root.checkbox_slider_frame = ctk.CTkFrame(root)
#         root.checkbox_slider_frame.grid(row=1, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
#         root.checkbox_1 = ctk.CTkCheckBox(master=root.checkbox_slider_frame)
#         root.checkbox_1.grid(row=1, column=0, pady=(20, 0), padx=20, sticky="n")
#         root.checkbox_2 = ctk.CTkCheckBox(master=root.checkbox_slider_frame)
#         root.checkbox_2.grid(row=2, column=0, pady=(20, 0), padx=20, sticky="n")
#         root.checkbox_3 = ctk.CTkCheckBox(master=root.checkbox_slider_frame)
#         root.checkbox_3.grid(row=3, column=0, pady=20, padx=20, sticky="n")

#         # set default values
#         root.sidebar_button_3.configure(state="disabled", text="Disabled CTkButton")
#         root.checkbox_3.configure(state="disabled")
#         root.checkbox_1.select()
#         root.scrollable_frame_switches[0].select()
#         root.scrollable_frame_switches[4].select()
#         root.radio_button_3.configure(state="disabled")
#         root.appearance_mode_optionemenu.set("Dark")
#         root.scaling_optionemenu.set("100%")
#         root.optionmenu_1.set("CTkOptionmenu")
#         root.combobox_1.set("CTkComboBox")
#         root.slider_1.configure(command=root.progressbar_2.set)
#         root.slider_2.configure(command=root.progressbar_3.set)
#         root.progressbar_1.configure(mode="indeterminnate")
#         root.progressbar_1.start()
#         root.textbox.insert("0.0", "CTkTextbox\n\n" + "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\n" * 20)
#         root.seg_button_1.configure(values=["CTkSegmentedButton", "Value 2", "Value 3"])
#         root.seg_button_1.set("Value 2")

# #        return(self)
# #        return dir(root)


