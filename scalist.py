"""
#######################################################################
scale_keys v1.5
by Eric Luhta

Last update: 5/27/2017

Makes scaling curves in the graph editor vastly more powerful and simple.
Helpful info can be found in the tool's "About" tab.

INSTALL:

- Place the scale_keys.py script in your maya scripts folder
- Place the scale_keys.png and the scale_keys_icon.png files in your ../icons folder

TO RUN:
Save the following as a python shelf button and add the scalist_icon for maximum performance.

import scale_keys
reload(scale_keys)
scale_keys

#######################################################################

"""

import pymel.core as pm

__author__ = 'Eric Luhta'


########################################################################
# Scalist Class
########################################################################

class Scalist(object):
    def __init__(self, pivot, user_scale, scale_type):
        self.pivot = pivot
        self.scale = user_scale.getValue()
        self.curves = pm.keyframe(query=True, selected=True, name=True)
        self.key_values = pm.keyframe(query=True, selected=True, valueChange=True, absolute=True)
        self.key_times = pm.keyframe(query=True, selected=True, timeChange=True, absolute=True)
        self.scale_type = scale_type

    #####################################################################
    # Pivot functions

    def get_pivot(self):
        """Returns the right function to determine the pivot based on a dictionary argument"""
        switcher = {'pivot_zero_value': self.pivot_zero_value,
                    'pivot_highest_value': self.pivot_highest_value,
                    'pivot_lowest_value': self.pivot_lowest_value,
                    'pivot_middle_value': self.pivot_middle_value,
                    'pivot_last_selected_value': self.pivot_last_selected_value,
                    'pivot_first_time': self.pivot_first_time,
                    'pivot_last_time': self.pivot_last_time,
                    'pivot_current_time': self.pivot_current_time,
                    'pivot_last_selected_time': self.pivot_last_selected_time,
                    'pivot_flip_curve_value': self.pivot_flip_curve_value,
                    'pivot_first_value': self.pivot_first_value,
                    'pivot_ramped_value': self.pivot_ramped_value,
                    'pivot_flip_zero_value': self.pivot_flip_zero_value
                    }

        # Get the function from the switcher dictionary
        func = switcher.get(self.pivot)
        return func()

    def pivot_zero_value(self):
        """Returns 0 for using it as a pivot point"""
        return 0

    def pivot_highest_value(self):
        """Returns the value of the highest keyframe in the active selection"""
        return max(self.key_values)

    def pivot_lowest_value(self):
        """Returns the value of the lowest keyframe in the active selection"""
        return min(self.key_values)

    def pivot_middle_value(self):
        """Returns the middle value of the current active selection"""
        return ((max(self.key_values) + min(self.key_values)) / 2)

    def pivot_last_selected_value(self):
        """Returns the value of the last selected key"""
        pivot = pm.keyframe(query=True, lastSelected=True, valueChange=True)

        # Pymel returns a set with lastSelected flag, so make sure it only sends the value
        return pivot[0]

    def pivot_first_time(self):
        """Returns the first key time of the active selection"""
        return min(self.key_times)

    def pivot_last_time(self):
        """Returns the last key time of the active selection"""
        return max(self.key_times)

    def pivot_current_time(self):
        """Returns the current frame"""
        return pm.currentTime(query=True)

    def pivot_last_selected_time(self):
        """Returns the time of the last selected keyframe"""
        pivot = pm.keyframe(query=True, lastSelected=True, timeChange=True)

        # Pymel returns a set with lastSelected flag, so make sure it only sends the value
        return pivot[0]

    def pivot_first_value(self):
        """Returns the value of the first key in each curve"""
        return self.key_values[0]

    def pivot_flip_curve_value(self):
        """Sets scale to -1 and returns middle value to invert selected curves"""
        self.scale = -1
        return self.pivot_middle_value()

    def pivot_flip_zero_value(self):
        """Sets scale to -1 and returns zero to flip curves over 0"""
        self.scale = -1
        return self.pivot_zero_value()

    def pivot_ramped_value(self):
        """Scales gradually over the selected range"""
        pass

    #############################################################################
    # Scale functions

    def scale_keys_value(self):
        """Scales all selected keys in value from a single pivot for all"""
        pm.scaleKey(valuePivot=self.get_pivot(), valueScale=self.scale)

    def scale_keys_value_multi(self):
        """Scales each selected curve's keys independently on their own pivots"""

        # Go through each curve, finding the times and values for each and apply the pivot for that curve
        for curve in self.curves:
            self.key_values = self.get_key_values(curve)
            self.key_times = self.get_key_times(curve)
            pivot = self.get_pivot()

            for i in xrange(len(self.key_values)):
                pm.scaleKey(curve, valuePivot=pivot, valueScale=self.scale, time=(self.key_times[i], self.key_times[i]))

    def scale_keys_time(self):
        """Scales all selected keys in time from a single pivot for all"""
        pm.scaleKey(timePivot=(self.get_pivot()), timeScale=self.scale)

        # Snap all keys so there are no subframe keys
        pm.snapKey(tm=1.0)

    def scale_keys_time_multi(self):
        """Scales each selected curve's keys independently in time on their own pivots"""

        for curve in self.curves:
            self.key_times = self.get_key_times(curve)

            # if we're scaling time from the last key, we need to iterate backwards through the scaling or some values
            # will give weird results as the first keys end up after ones not yet scaled
            if self.pivot == 'pivot_last_time':
                key_range = reversed(xrange(len(self.key_times)))
            else:
                key_range = xrange(len(self.key_times))

            for i in key_range:
                pm.scaleKey(curve, timePivot=(self.get_pivot()), timeScale=self.scale, time=(self.key_times[i], self.key_times[i]))

            pm.snapKey(tm=1.0)

    ##########################################################################
    # Helper functions

    def get_scale_type(self):
        """For the UI, a switcher to pick the appropriate type of scaling based on a passed value"""

        scale_operations = {'scale_keys_value': self.scale_keys_value,
                            'scale_keys_value_multi': self.scale_keys_value_multi,
                            'scale_keys_time': self.scale_keys_time,
                            'scale_keys_time_multi': self.scale_keys_time_multi}

        func = scale_operations.get(self.scale_type)
        return func()

    def get_curves(self):
        """Get a list of the names of any selected curves"""
        return pm.keyframe(query=True, selected=True, name=True)

    def get_key_values(self, curve):
        """Get list of values for an individual curve"""
        return pm.keyframe(curve, query=True, selected=True, valueChange=True, absolute=True)

    def get_key_times(self, curve):
        """Get list of times for an individual curve"""
        return pm.keyframe(curve, query=True, selected=True, timeChange=True, absolute=True)


#############################################################################
# Scaling tool functions

def check_for_selected_keys(pivot):
    """ Makes sure there are keys selected in the graph editor """
    selected_keys = pm.keyframe(q=True, sl=True)

    # a few of the pivots could feasibly be used with just a single keyframe selected so allow those
    single_key_exceptions = ['pivot_zero_value', 'pivot_current_time', 'pivot_flip_zero_value']

    if len(selected_keys) >= 2:
        return True
    elif len(selected_keys) > 0 and pivot in single_key_exceptions:
        return True
    pm.warning('[scalist.py] Please select at least 2 keyframes.'),
    return False


def do_scale(pivot, user_scale, scale_type):
    """If selection is ok, create an instance and do the scaling"""
    if check_for_selected_keys(pivot):
        scalist = Scalist(pivot, user_scale, scale_type)
        scalist.get_scale_type()


# UI

class Window_UI:
    def __init__(self):
        if pm.window('scalist', exists=True):
            pm.deleteUI('scalist')
        self.window_id = 'scalist'

    def update_slider(self, ctrl, val):
        """updates the slider when a scale amount preset button is clicked"""
        pm.floatSliderGrp(ctrl, edit=True, v=val)

    def rgb(self, values):
        """converts rgb values to 0.0-1.0 for maya flags"""
        converted = []
        for val in values:
            converted.append(round(val / 255.0, 3))
        return converted

    def build_ui(self):
        """builds the ui window"""

        tool_window = pm.window(self.window_id, title="scalist", width=368, height=295, mnb=True, mxb=True,
                                sizeable=True)
        main_layout = pm.rowColumnLayout(w=368, h=295)

        # get the header image from the user's prefs
        imagePath = pm.internalVar(upd=True) + "icons/scalist.png"
        pm.image(w=225, h=75, image=imagePath)

        # scale amount slider
        user_scale = pm.floatSliderGrp(label='Amount', field=True, precision=2, width=363, minValue=-2.0, maxValue=5.0,
                                       v=1.0, fieldMinValue=-10.0, fieldMaxValue=10.0)

        # scale preset buttons
        btn_layout = pm.rowColumnLayout(nc=11)

        btn_1 = pm.button(label='-1', w=33, bgc=self.rgb([231, 205, 59]),
                          c=pm.Callback(self.update_slider, user_scale, -1))
        btn_2 = pm.button(label='.25', w=33, c=pm.Callback(self.update_slider, user_scale, 0.25))
        btn_3 = pm.button(label='.50', w=33, c=pm.Callback(self.update_slider, user_scale, 0.5))
        btn_4 = pm.button(label='.75', w=33, c=pm.Callback(self.update_slider, user_scale, 0.75))
        btn_5 = pm.button(label='.90', w=33, c=pm.Callback(self.update_slider, user_scale, 0.9))
        btn_6 = pm.button(label='reset', w=33, bgc=self.rgb([231, 205, 59]),
                          c=pm.Callback(self.update_slider, user_scale, 1.0))
        btn_7 = pm.button(label='1.1', w=33, bgc=self.rgb([215, 215, 215]),
                          c=pm.Callback(self.update_slider, user_scale, 1.1))
        btn_8 = pm.button(label='1.25', w=33, bgc=self.rgb([215, 215, 215]),
                          c=pm.Callback(self.update_slider, user_scale, 1.25))
        btn_9 = pm.button(label='1.5', w=33, bgc=self.rgb([215, 215, 215]),
                          c=pm.Callback(self.update_slider, user_scale, 1.5))
        btn_10 = pm.button(label='1.75', w=33, bgc=self.rgb([215, 215, 215]),
                           c=pm.Callback(self.update_slider, user_scale, 1.75))
        btn_11 = pm.button(label='x2', w=33, bgc=self.rgb([231, 205, 59]),
                           c=pm.Callback(self.update_slider, user_scale, 2.0))


        # headers
        pm.setParent(main_layout)
        pm.separator(style='none', h=5)
        categories = pm.rowColumnLayout(nc=3)
        pm.text(label='Value', w=177, font='boldLabelFont', bgc=self.rgb([231, 205, 59]))
        pm.separator(style='single', w=10)
        pm.text(label='Time', w=179, font='boldLabelFont', bgc=self.rgb([20, 20, 20]))
        pm.separator(style='none', h=5)
        pm.separator(style='single', w=10)
        pm.separator(style='none', h=5)

        # pivot buttons
        pm.setParent('..')
        pivot_buttons = pm.rowColumnLayout(nc=5)
        pb1 = pm.button(label='Mid', w=88, annotation='Scaled from midpoint value of curve',
                        bgc=self.rgb([215, 215, 215]),
                        command=pm.Callback(do_scale, 'pivot_middle_value', user_scale, 'scale_keys_value'))
        pb2 = pm.button(label='Multi', w=89, annotation='Each curve scaled from its own midpoint',
                        bgc=self.rgb([45, 45, 45]),
                        command=pm.Callback(do_scale, 'pivot_middle_value', user_scale, 'scale_keys_value_multi'))
        pm.separator(style='single', w=10)
        pb3 = pm.button(label='First', w=87, annotation='Scaled from first frame of selection',
                        bgc=self.rgb([120, 120, 120]),
                        command=pm.Callback(do_scale, 'pivot_first_time', user_scale, 'scale_keys_time'))
        pb4 = pm.button(label='Multi', w=88, annotation='Each curve scaled from its first frame',
                        bgc=self.rgb([45, 45, 45]),
                        command=pm.Callback(do_scale, 'pivot_first_time', user_scale, 'scale_keys_time_multi'))
        pb5 = pm.button(label='Highest', w=87, annotation='Scaled from the highest key value selected',
                        bgc=self.rgb([215, 215, 215]),
                        command=pm.Callback(do_scale, 'pivot_highest_value', user_scale, 'scale_keys_value'))
        pb6 = pm.button(label='Multi', w=88, annotation='Each curve scaled from its highest selected key',
                        bgc=self.rgb([45, 45, 45]),
                        command=pm.Callback(do_scale, 'pivot_highest_value', user_scale, 'scale_keys_value_multi'))
        pm.separator(style='single', w=10)
        pb7 = pm.button(label='Last', w=89, annotation='Scaled from last frame of selection',
                        bgc=self.rgb([120, 120, 120]),
                        command=pm.Callback(do_scale, 'pivot_last_time', user_scale, 'scale_keys_time'))
        pb8 = pm.button(label='Multi', w=88, annotation='Each curve scaled from its last frame',
                        bgc=self.rgb([45, 45, 45]),
                        command=pm.Callback(do_scale, 'pivot_last_time', user_scale, 'scale_keys_time_multi'))
        pb9 = pm.button(label='Lowest', w=87, annotation='Scaled from the lowest key value selected',
                        bgc=self.rgb([215, 215, 215]),
                        command=pm.Callback(do_scale, 'pivot_lowest_value', user_scale, 'scale_keys_value'))
        pb10 = pm.button(label='Multi', w=88, annotation='Each curve scaled from its lowest selected key',
                         bgc=self.rgb([45, 45, 45]),
                         command=pm.Callback(do_scale, 'pivot_lowest_value', user_scale, 'scale_keys_value_multi'))
        pm.separator(style='single', w=10)
        pb11 = pm.button(label='Current', w=89, annotation='Scaled from the current frame in timerange',
                         bgc=self.rgb([120, 120, 120]),
                         command=pm.Callback(do_scale, 'pivot_current_time', user_scale, 'scale_keys_time'))
        pm.separator(style='none')
        pb12 = pm.button(label='0', w=87, annotation='Scaled from 0', bgc=self.rgb([215, 215, 215]),
                         command=pm.Callback(do_scale, 'pivot_zero_value', user_scale, 'scale_keys_value'))
        pm.separator(style='none')
        pm.separator(style='single', w=10)
        pb13 = pm.button(label='Last Selected', w=89, annotation='Scaled in time from the last selected key frame',
                         bgc=self.rgb([120, 120, 120]),
                         command=pm.Callback(do_scale, 'pivot_last_selected_time', user_scale, 'scale_keys_time'))
        pm.separator(style='none')
        pb14 = pm.button(label='Last Selected', w=87, annotation='Scaled in value from the last selected key',
                         bgc=self.rgb([215, 215, 215]),
                         command=pm.Callback(do_scale, 'pivot_last_selected_value', user_scale, 'scale_keys_value'))
        pm.separator(style='none')
        pm.separator(style='single', w=10)
        pm.separator(style='in')
        pm.separator(style='in')
        pb15 = pm.button(label='First', w=87, annotation='Each curve selected from its earliest selected key',
                         bgc=self.rgb([215, 215, 215]),
                         command=pm.Callback(do_scale, 'pivot_first_value', user_scale, 'scale_keys_value_multi'))
        pm.separator(style='none')
        pm.separator(style='single', w=10)

        pb16 = pm.button(label='Flip Mid', w=77, annotation='Flip each selected curve along its midpoint value',
                         bgc=self.rgb([231, 205, 59]),
                         command=pm.Callback(do_scale, 'pivot_flip_curve_value', user_scale, 'scale_keys_value_multi'))

        pb17 = pm.button(label='Flip 0', w=77, annotation='Flip each selected curve over 0',
                         bgc=self.rgb([231, 205, 59]),
                         command=pm.Callback(do_scale, 'pivot_flip_zero_value', user_scale, 'scale_keys_value'))

        pm.setParent('..')
        pm.separator(h=10, style='in')

        pm.showWindow(tool_window)


w = Window_UI()
w.build_ui()






