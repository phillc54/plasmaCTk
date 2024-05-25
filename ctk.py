#!/bin/python3

#import tkinter
#import tkinter.messagebox
import customtkinter as ctk
import math

import linuxcnc
import hal

from gui import Gui

ERROR = linuxcnc.error()
STATUS = linuxcnc.stat()
COMMAND = linuxcnc.command()

STATES = {linuxcnc.STATE_ESTOP:       'state-estop',
          linuxcnc.STATE_ESTOP_RESET: 'state-estop-reset',
          linuxcnc.STATE_ON:          'state-on',
          linuxcnc.STATE_OFF:         'state-off'}

MODES  = {linuxcnc.MODE_MANUAL: 'mode-manual',
          linuxcnc.MODE_AUTO:   'mode-auto',
          linuxcnc.MODE_MDI:    'mode-mdi'}

INTERP = {linuxcnc.INTERP_WAITING: 'interp-waiting',
          linuxcnc.INTERP_READING: 'interp-reading',
          linuxcnc.INTERP_PAUSED: 'interp-paused',
          linuxcnc.INTERP_IDLE: 'interp-idle'}

#ctk.set_appearance_mode('System')  # Modes: 'System' (standard), 'Dark', 'Light'
#ctk.set_default_color_theme('blue')  # Themes: 'blue' (standard), 'green', 'dark-blue'


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_default_color_theme('blue')  # Themes: blue (default), dark-blue, green
        ctk.set_appearance_mode('system')  # Modes: system (default), light, dark
        self.w = Gui(self)#gui.make_gui(self)
#        print(dir(ctk))
#        print(dir(bob.tabview))
#        print(bob.textbox)
        print(f"W:\n{dir(self.w)}\n")
        self.title('Phill\'s GUI Test')
#        self.w.geometry(f'{1100}x{580}')
        self.geometry(f'{1100}x{580}')
#        print(dir(STATUS.stat))
#        STATUS.connect('periodic', lambda w: self.periodic())

#        tId = GLib.timeout_add(1000, self.time_out)
#        print(tId)
        self._status_active = False
        self.status = {}
        STATUS.poll()
        self.set_current_status()
#        print(self.status)
        self.after(100, self.periodic)

    def set_current_status(self):
        self.status['command-state'] = STATUS.state
        self.status['state'] = STATUS.task_state
        self.status['mode']  = STATUS.task_mode
        self.status['interp']= STATUS.interp_state
        # Only update file if call level is 0, which
        # means we are not executing a subroutine/remap
        # This avoids emitting signals for bogus file names below
        if STATUS.call_level == 0:
            self.status['file']  = STATUS.file
        self.status['paused']= STATUS.paused
        self.status['line']  = STATUS.motion_line
        self.status['homed'] = STATUS.homed
        self.status['tool-in-spindle'] = STATUS.tool_in_spindle
        self.status['feed-rate'] = STATUS.current_vel * 60
#        print('set_current_status:', STATUS.current_vel, self.status['feed-rate'])
        try:
            if hal.get_value('iocontrol.0.tool-prepare'):
                self.status['tool-prep-number'] = hal.get_value('iocontrol.0.tool-prep-number')
        except RuntimeError:
             self.status['tool-prep-number'] = -1
        self.status['motion-mode'] = STATUS.motion_mode
        self.status['motion-type'] = STATUS.motion_type
        self.status['spindle-or'] = STATUS.spindle[0]['override']
        self.status['feed-or'] = STATUS.feedrate
        self.status['rapid-or'] = STATUS.rapidrate
        self.status['max-velocity-or'] = STATUS.max_velocity
        self.status['feed-hold']  = STATUS.feed_hold_enabled
        self.status['g5x-index']  = STATUS.g5x_index
        self.status['spindle-enabled']  = STATUS.spindle[0]['enabled']
        self.status['spindle-direction']  = STATUS.spindle[0]['direction']
        self.status['block-delete']= STATUS.block_delete
        self.status['optional-stop']= STATUS.optional_stop
        try:
            self.status['actual-spindle-speed'] = hal.get_value('spindle.0.speed-in') * 60
        except RuntimeError:
             self.status['actual-spindle-speed'] = 0
        try:
            self.status['spindle-at-speed'] = hal.get_value('spindle.0.at-speed')
        except RuntimeError:
            self.status['spindle-at-speed'] = False
        self.status['flood']= STATUS.flood
        self.status['mist']= STATUS.mist
        self.status['current-z-rotation'] = STATUS.rotation_xy
        self.status['current-tool-offset'] = STATUS.tool_offset

        # override limits / hard limits
        or_limit_list=[]
        hard_limit_list = []
        ferror = []
        hard_limit = False
        or_limit_set = False
        for j in range(0, STATUS.joints):
            or_limit_list.append( STATUS.joint[j]['override_limits'])
            or_limit_set = or_limit_set or STATUS.joint[j]['override_limits']
            min_hard_limit = STATUS.joint[j]['min_hard_limit']
            max_hard_limit = STATUS.joint[j]['max_hard_limit']
            hard_limit = hard_limit or min_hard_limit or max_hard_limit
            hard_limit_list.append([min_hard_limit,max_hard_limit])
            ferror.append(STATUS.joint[j]['ferror_current'])
        self.status['override-limits'] = or_limit_list
        self.status['override-limits-set'] = bool(or_limit_set)
        self.status['hard-limits-tripped'] = bool(hard_limit)
        self.status['hard-limits-list'] = hard_limit_list
        self.status['ferror-current'] = ferror
        # active g-codes
        active_gcodes = []
        codes =''
        for i in sorted(STATUS.gcodes[1:]):
            if i == -1: continue
            if i % 10 == 0:
                    active_gcodes.append('G%d' % (i/10))
            else:
                    active_gcodes.append('G%d.%d' % (i/10, i%10))
        for i in active_gcodes:
            codes = codes +('%s '%i)
        self.status['g-code'] = codes
        # extract specific G-code modes
        itime = fpm = fpr = css = rpm = metric = False
        radius = diameter = adm = idm = False
        for num, i in enumerate(active_gcodes):
#            print(num, i)
            del num
            if   i == 'G90': adm      = True
            elif i == 'G91': idm      = True
            elif i == 'G93': itime    = True
            elif i == 'G94': fpm      = True
            elif i == 'G95': fpr      = True
            elif i == 'G96': css      = True
            elif i == 'G97': rpm      = True
            elif i == 'G21': metric   = True
            elif i == 'G7' : diameter = True
            elif i == 'G8' : radius   = True
        self.status['g90']      = adm
        self.status['g91']      = idm
        self.status['itime']    = itime
        self.status['fpm']      = fpm
        self.status['fpr']      = fpr
        self.status['css']      = css
        self.status['rpm']      = rpm
        self.status['metric']   = metric
        self.status['radius']   = radius
        self.status['diameter'] = diameter
        if css:
            try:
                self.status['spindle-speed']= hal.get_value('spindle.0.speed-out')
            except RuntimeError:
                self.status['spindle-speed']= STATUS.spindle[0]['speed']
        else:
            self.status['spindle-speed']= STATUS.spindle[0]['speed']
        # active m-codes
        mcodes = ''
        for i in sorted(STATUS.mcodes[1:]):
            if i == -1: continue
            mcodes += f"M{i} "

        self.status['m-code'] = mcodes
        self.status['tool-info']  = STATUS.tool_table[0]
        self.status['f-code'] = STATUS.settings[1]
        self.status['s-code'] = STATUS.settings[2]
        self.status['blend-tolerance-code'] = STATUS.settings[3]
        self.status['naive-cam-tolerance-code'] = STATUS.settings[4]

    def periodic(self):
        # print('\nSTATUS:')
        # print(f"     is_all_homed = {STATUS.is_all_homed()}")
        # print(f"get_selected_axis = {STATUS.get_selected_axis()}")
        # print(f"  actual_position = {STATUS.stat.actual_position}")
        # print(f"       cycle_time = {STATUS.stat.cycle_time}")
        # print()

        # STATUS.poll()
        # print('\nSTATUS:')
        # print(f"            homed = {STATUS.homed}")
        # print(f"           joints = {STATUS.joints}")
        # print(f"  actual_position = {STATUS.actual_position}")
        # print(f"       cycle_time = {STATUS.cycle_time}")
        # print()

        try:
            STATUS.poll()
        except:
            self._status_active = False
            # some things might not need linuxcnc status but do need periodic
            #print('periodic')
            # Reschedule
            self.after(100, self.periodic)
        self._status_active = True
        old = dict(self.status)
        self.set_current_status()

#        print(old)
#        print
#        print(self.status)

        if self.status['command-state'] != old.get('command-state'):
            if self.status['command-state'] == linuxcnc.RCS_EXEC:
                print('command-running')
            elif self.status['command-state'] == linuxcnc.RCS_DONE:
                print('command-stopped')
            elif self.status['command-state'] == linuxcnc.RCS_ERROR:
                print('command-error')

        if self.status['state'] != old.get('state', 0):
            # set machine estop/clear
            if old.get('state', 0) == linuxcnc.STATE_ESTOP and self.status['state'] == linuxcnc.STATE_ESTOP_RESET:
                print('state-estop-reset')
                print('interp-idle')
            elif self.status['state'] == linuxcnc.STATE_ESTOP:
                print('state-estop')
                print('interp-idle')
            # set machine on/off
            if self.status['state'] == linuxcnc.STATE_ON:
                print('state-on')
            elif old.get('state', 0) == linuxcnc.STATE_ON and self.status['state'] < linuxcnc.STATE_ON:
                print('state-off')
            # reset modes/interpreter on machine on
            if self.status['state'] == linuxcnc.STATE_ON:
                old['mode'] = 0
                old['interp'] = 0

        if self.status['mode'] != old.get('mode', 0):
            self.previous_mode = old.get('mode', 0)
            print(MODES[self.status['mode']])

        if self.status['interp'] != old.get('interp', 0):
            if not old.get('interp', 0) or old.get('interp', 0) == linuxcnc.INTERP_IDLE:
                print('interp-run')
            print(INTERP[self.status['interp']])
        # paused
        if self.status['paused'] != old.get('paused', None):
            print('program-pause-changed', self.status['paused'])
        # block delete
        if self.status['block-delete'] != old.get('block-delete', None):
            print('block-delete-changed', self.status['block-delete'])
        # optional_stop
        if self.status['optional-stop'] != old.get('optional-stop', None):
            print('optional-stop-changed', self.status['optional-stop'])
        # file changed
        if self.status['file'] != old.get('file', None):
            # if interpreter is reading or waiting, the new file
            # is a remap procedure, with the following test we
            # partly avoid emitting a signal in that case, which would cause
            # a reload of the preview and sourceview widgets.  A signal could
            # still be emitted if aborting a program shortly after it ran an
            # external file subroutine, but that is fixed by not updating the
            # file name if call level != 0 in the merge() function above.
            # do avoid that a signal is emitted in that case, causing
            # a reload of the preview and sourceview widgets
            if self.status.interp_state == linuxcnc.INTERP_IDLE:
                print('file-loaded', self.status['file'])

        #ToDo : Find a way to avoid signal when the line changed due to
        #       a remap procedure, because the signal do highlight a wrong
        #       line in the code
        # current line
        if self.status['line'] != old.get('line', None):
            print('line-changed', self.status['line'])

        if self.status['tool-in-spindle'] != old.get('tool-in-spindle', None):
            print('tool-in-spindle-changed', self.status['tool-in-spindle'])
        if self.status['tool-prep-number'] != old.get('tool-prep-number'):
            print('tool-prep-changed', self.status['tool-prep-number'])

        if self.status['motion-mode'] != old.get('motion-mode', None):
            print('motion-mode-changed', self.status['motion-mode'])

        if self.status['motion-type'] != old.get('motion-type', None):
            print('motion-type-changed', self.status['motion-type'])

        # if the homed status has changed
        # check number of homed joints against number of available joints
        # if they are equal send the all-homed signal
        # else send the not-all-homed signal (with a string of unhomed joint numbers)
        # if a joint is homed send 'homed' (with a string of homed joint number)
        if self.status['homed'] != old.get('homed', None):
            homed_joints = 0
            unhomed_joints = ''
            for joint in range(0, STATUS.joints):
                if self.status['homed'][joint]:
                    homed_joints += 1
                    print('homed', joint)
                else:
                    print('unhomed', joint)
                    unhomed_joints += str(joint)
            if homed_joints == STATUS.joints:
                self._is_all_homed = True
                print('all-homed')
            else:
                self._is_all_homed = False
                print('not-all-homed', unhomed_joints)
        # override limits
        if self.status['override-limits'] != old.get('override-limits', None):
            print('override-limits-changed', self.status['override-limits-set'], self.status['override-limits'])
        # hard limits tripped
        if self.status['hard-limits-list'] != old.get('hard-limits-list'):
            print('hard-limits-tripped', self.status['hard-limits-tripped'], self.status['hard-limits-list'])
#         # current velocity
#         print('current-feed-rate', STATUS.current_vel * 60.0)
#         # current velocity
        if self.status['feed-rate'] != old.get('feed-rate', 0):
            print('current-feed-rate', self.status['feed-rate'])
#         # X relative position
#         position = STATUS.actual_position[0]
#         g5x_offset = STATUS.g5x_offset[0]
#         tool_offset = STATUS.tool_offset[0]
#         g92_offset = STATUS.g92_offset[0]
#         print('current-x-rel-position', position - g5x_offset - tool_offset - g92_offset)

#         # calculate position offsets (native units)
#        abs, rel, dtg = self.get_position()
#        print('current-position', abs, rel, dtg, STATUS.joint_actual_position)

#         # ferror
#         print('following-error', self.status['ferror-current'])
#         # spindle control
#         if self.status['spindle-at-speed'] != old.get('spindle-at-speed', None) or \
#             self.status['spindle-enabled'] != old.get('spindle-enabled', None) or \
#             self.status['spindle-direction'] != old.get('spindle-direction', None):
#                 print('spindle-control-changed', 0, self.status['spindle-enabled'], self.status['spindle-direction'], self.status['spindle-at-speed'])
#         # requested spindle speed
#         if self.status['spindle-speed'] != old.get('spindle-speed', None):
#             print('requested-spindle-speed-changed', self.status['spindle-speed'])
#         # actual spindle speed
#         if self.status['actual-spindle-speed'] != old.get('actual-spindle-speed', None):
#             print('actual-spindle-speed-changed', self.status['actual-spindle-speed'])
#         # spindle override
#         if self.status['spindle-or'] != old.get('spindle-or', None):
#             print('spindle-override-changed', self.status['spindle-or'] * 100)
#         # feed override
        if self.status['feed-or'] != old.get('feed-or', None):
            print('feed-override-changed', self.status['feed-or'] * 100)
        # rapid override
        if self.status['rapid-or'] != old.get('rapid-or', None):
            print('rapid-override-changed', self.status['rapid-or'] * 100)
        # max-velocity override
        if self.status['max-velocity-or'] != old.get('max-velocity-or', None):
            # work around misconfigured config (missing MAX_LINEAR_VELOCITY in TRAJ)
            if self.status['max-velocity-or'] != 1e99:
                print('max-velocity-override-changed', self.status['max-velocity-or'] * 60)
#         # feed hold
#         if self.status['feed-hold'] != old.get('feed-hold', None):
#             print('feed-hold-enabled-changed', self.status['feed-hold'])
#         # mist
#         if self.status['mist'] != old.get('mist', None):
#             print('mist-changed', self.status['mist'])
#         # flood
#         if self.status['flood'] != old.get('flood', None):
#             print('flood-changed', self.status['flood'])
        # rotation around Z
        if self.status['current-z-rotation'] != old.get('current-z-rotation', None):
            print('current-z-rotation', self.status['current-z-rotation'])
#         # current tool offsets
#         if self.status['current-tool-offset'] != old.get('current-tool-offset', None):
#                print('current-tool-offset', self.status['current-tool-offset'])
        #############################
        # Gcodes
        #############################
        # g-codes
        if self.status['g-code'] != old.get('g-code', None):
            print('g-code-changed', self.status['g-code'])

        # metric mode g21
        if self.status['metric'] != old.get('metric', None):
            print('metric-mode-changed', self.status['metric'])

        # G5x (active user system)
        if self.status['g5x-index'] != old.get('g5x-index', None):
            print('user-system-changed', self.status['g5x-index'])

        # absolute mode g90
        if self.status['g90'] != old.get('g90', None):
            print('g90-mode',self.status['g90'] )

        # incremental mode g91
        g91_old = old.get('g91', None)
        g91_new = self.status['g91']
        if g91_new != g91_old:
            print('g91-mode', g91_new)

        # inverse time mode g93
        if self.status['itime'] != old.get('itime', None):
            print('itime-mode', self.status['itime'])

        # feed per minute mode g94
        if self.status['fpm'] != old.get('fpm', None):
            print('fpm-mode', self.status['fpm'])

        # feed per revolution mode g95
        if self.status['fpr'] != old.get('fpr', None):
            print('fpr-mode', self.status['fpr'])

        # css mode g96
        if self.status['css'] != old.get('css', None):
            print('css-mode', self.status['css'])

        # rpm mode g97
        if self.status['rpm'] != old.get('rpm', None):
            print('rpm-mode', self.status['rpm'])

        # radius mode g8
        if self.status['radius'] != old.get('radius', None):
            print('radius-mode', self.status['radius'])

        # diameter mode g7
        if self.status['diameter'] != old.get('diameter', None):
            print('diameter-mode', self.status['diameter'])

        ####################################
        # Mcodes
        ####################################
        # m-codes
        if self.status['m-code'] != old.get('m-code', None):
            print('m-code-changed', self.status['m-code'])

        if self.status['tool-info'] != old.get('tool-info', None):
            print('tool-info-changed', self.status['tool-info'])

        #####################################
        # settings
        #####################################
        # feed code
        if self.status['f-code'] != old.get('f-code', None):
            print('f-code-changed', self.status['f-code'])

        # s code
        if self.status['s-code'] != old.get('s-code', None):
            print('s-code-changed', self.status['s-code'])

        # g53 blend code
        if self.status['blend-tolerance-code'] != old.get('blend-tolerance-code', None) or \
           self.status['naive-cam-tolerance-code'] != old.get('naive-cam-tolerance-code', None):
                print('blend-code-changed', self.status['blend-tolerance-code'], self.status['naive-cam-tolerance-code'])

#         # AND DONE... Return true to continue timeout
# #        print('periodic')
# #        return True

        self.after(100, self.periodic)

    def get_position(self):
        abs = STATUS.actual_position
#        mp = STATUS.position
        dtg = STATUS.dtg

        x = abs[0] - STATUS.g5x_offset[0] - STATUS.tool_offset[0]
        y = abs[1] - STATUS.g5x_offset[1] - STATUS.tool_offset[1]
        z = abs[2] - STATUS.g5x_offset[2] - STATUS.tool_offset[2]
        a = abs[3] - STATUS.g5x_offset[3] - STATUS.tool_offset[3]
        b = abs[4] - STATUS.g5x_offset[4] - STATUS.tool_offset[4]
        c = abs[5] - STATUS.g5x_offset[5] - STATUS.tool_offset[5]
        u = abs[6] - STATUS.g5x_offset[6] - STATUS.tool_offset[6]
        v = abs[7] - STATUS.g5x_offset[7] - STATUS.tool_offset[7]
        w = abs[8] - STATUS.g5x_offset[8] - STATUS.tool_offset[8]

        if STATUS.rotation_xy != 0:
            t = math.radians(-STATUS.rotation_xy)
            xr = x * math.cos(t) - y * math.sin(t)
            yr = x * math.sin(t) + y * math.cos(t)
            x = xr
            y = yr

        x -= STATUS.g92_offset[0]
        y -= STATUS.g92_offset[1]
        z -= STATUS.g92_offset[2]
        a -= STATUS.g92_offset[3]
        b -= STATUS.g92_offset[4]
        c -= STATUS.g92_offset[5]
        u -= STATUS.g92_offset[6]
        v -= STATUS.g92_offset[7]
        w -= STATUS.g92_offset[8]

        rel = [x, y, z, a, b, c, u, v, w]
        return abs, rel, dtg



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


# if __name__ == '__main__':
#     app = App()
#     app.mainloop()

app = App()
app.mainloop()

