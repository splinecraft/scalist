"""
#######################################################################
scalist v1.3
by Eric Luhta

Last update: 7/20/2016

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
                    'pivot_first_value': self.pivot_first_value}

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
        """Returns -1 to invert selected curves"""
        self.scale = -1
        return self.pivot_middle_value()

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
            pm.scaleKey(curve, timePivot=(self.get_pivot()), timeScale=self.scale)
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

def check_for_selected_keys():
    """ Makes sure there are keys selected in the graph editor """
    selected_keys = pm.keyframe(q=True, sl=True)
    if len(selected_keys) >= 2:
        return True
    pm.warning('[scalist.py] Please select at least 2 keyframes.'),
    return False


def do_scale(pivot, user_scale, scale_type):
    if check_for_selected_keys():
        scalist = Scalist(pivot, user_scale, scale_type)
        scalist.get_scale_type()

#################################################################################
# User Interface

def WindowUI():
    windowID = "scalist"

    if pm.window(windowID, exists=True):
        pm.deleteUI(windowID)

    testWindow = pm.window(windowID, title="scalist", width=225, height=285, mnb=False, mxb=False, sizeable=True)

    mainLayout = pm.columnLayout(w=190, h=285)

    # get the header image from the user's prefs
    imagePath = pm.internalVar(upd=True) + "icons/scalist.png"
    pm.image(w=225, h=75, image=imagePath)

    form = pm.formLayout()
    tabs = pm.tabLayout(innerMarginWidth=5, innerMarginHeight=5, w=220, h=205)
    pm.formLayout(form, edit=True,
                  attachForm=((tabs, 'top', 0), (tabs, 'left', 0), (tabs, 'bottom', 0), (tabs, 'right', 0)))

    # Main tool tab
    child1 = pm.rowColumnLayout(numberOfColumns=5, columnWidth=[(1, 60), (2, 40), (3, 10), (4, 60), (5, 40)])

    # user scale amount section

    pm.text(label="Amount", bgc=(.969, .922, .145))
    user_scale = pm.floatField(precision=2, value=1.0)
    pm.separator(style='none')
    pm.separator(style='none')
    pm.separator(style='none')

    # separator line
    pm.separator(style='none', h=10)
    pm.separator(style='none', h=10)
    pm.separator(style='single', h=10)
    pm.separator(style='none', h=10)
    pm.separator(style='none', h=10)

    # Headers for value and time
    pm.text(label="Value", font="boldLabelFont")
    pm.separator(style='none')
    pm.separator(style='single', horizontal=False)
    pm.text(label="Time", font="boldLabelFont")
    pm.separator(style='none')

    # Buttons

    # row 1
    pm.button(label="Mid", bgc=(.780, .780, .780), command=pm.Callback(do_scale, 'pivot_middle_value', user_scale, 'scale_keys_value'))
    pm.button(label="M", bgc=(.1, .1, .1), command=pm.Callback(do_scale, 'pivot_middle_value', user_scale, 'scale_keys_value_multi'))
    pm.separator(style='single', horizontal=False)
    pm.button(label="First", bgc=(.780, .780, .780), command=pm.Callback(do_scale, 'pivot_first_time', user_scale, 'scale_keys_time'))
    pm.button(label="M", bgc=(.1, .1, .1), command=pm.Callback(do_scale, 'pivot_first_time', user_scale, 'scale_keys_time_multi'))
    # row 2
    pm.button(label="Highest", bgc=(.780, .780, .780), command=pm.Callback(do_scale, 'pivot_highest_value', user_scale, 'scale_keys_value'))
    pm.button(label="M", bgc=(.1, .1, .1), command=pm.Callback(do_scale, 'pivot_highest_value', user_scale, 'scale_keys_value_multi'))
    pm.separator(style='single', horizontal=False)
    pm.button(label="Last", bgc=(.780, .780, .780), command=pm.Callback(do_scale, 'pivot_last_time', user_scale, 'scale_keys_time'))
    pm.button(label="M", bgc=(.1, .1, .1), command=pm.Callback(do_scale, 'pivot_last_selected_time', user_scale, 'scale_keys_time_multi'))
    # row 3
    pm.button(label="Lowest", bgc=(.780, .780, .780), command=pm.Callback(do_scale, 'pivot_lowest_value', user_scale, 'scale_keys_value'))
    pm.button(label="M", bgc=(.1, .1, .1), command=pm.Callback(do_scale, 'pivot_lowest_value', user_scale, 'scale_keys_value_multi'))
    pm.separator(style='single', horizontal=False)
    pm.button(label="Current", bgc=(.780, .780, .780), command=pm.Callback(do_scale, 'pivot_current_time', user_scale, 'scale_keys_time'))
    pm.separator(style='none')
    # row 4
    pm.button(label="0", bgc=(.780, .780, .780), command=pm.Callback(do_scale, 'pivot_zero_value', user_scale, 'scale_keys_value'))
    pm.separator(style='none')
    pm.separator(style='single', horizontal=False)
    pm.button(label="Last Sel", bgc=(.780, .780, .780), command=pm.Callback(do_scale, 'pivot_last_selected_time', user_scale, 'scale_keys_time'))
    pm.separator(style='none')
    # row 5
    pm.button(label="Last Sel", bgc=(.780, .780, .780), command=pm.Callback(do_scale, 'pivot_last_selected_value', user_scale, 'scale_keys_value'))
    pm.separator(style='none')
    pm.separator(style='single', horizontal=False)
    pm.separator(style='none')
    pm.separator(style='none')
    # row 6
    pm.button(label="First", bgc=(.780, .780, .780), command=pm.Callback(do_scale, 'pivot_first_value', user_scale, 'scale_keys_value_multi'))
    pm.separator(style='none')
    pm.separator(style='single', horizontal=False)
    pm.button(label="Flip", bgc=(.969, .922, .145), command=pm.Callback(do_scale, 'pivot_flip_curve_value', user_scale, 'scale_keys_value_multi'))
    pm.setParent('..')

    # About tab content
    child2 = pm.rowColumnLayout(numberOfColumns=2, columnWidth=(105, 105))
    aboutText = ""
    aboutText += "Amount is in 100%, so .9 will reduce by 10%, 1.1 will increase by 10%, etc.\n"
    aboutText += "\n"
    aboutText += "All keys are placed on even frames, no subframes.\n"
    aboutText += "\n"
    aboutText += "The M button next to several pivots is for scaling multiple selected curves relative to themselves. "\
            "If you have multiple curves or groups of keys selected and want to scale each one up/down based on its " \
            "own midpoint, highest key, or lowest key use the M button. The main pivot button will take the pivot based" \
            " on the mid, highest, or lowest of all selected curves/keys if used on multiple selections.\n"
    aboutText += "\n"
    aboutText += "Use the main operation button when you are working on only one curve or a group of keys on a curve.\n"
    aboutText += "\n"
    aboutText += "For predictable time scaling results, every curve should have a key at the pivot you're using.\n"
    aboutText += "\n"
    aboutText += "Middle will calculate the midpoint from highest and lowest keys on a selected curve or keys and scale from there.\n"
    aboutText += "\n"
    aboutText += "Last selected will use the last selected key as the pivot point. Use ctrl-selecting to specify what you want.\n"
    aboutText += "\n"
    aboutText += "Lowest and Highest use the respective key in the selection as the pivot.\n"
    aboutText += "\n"
    aboutText += "First is rather niche but can be handy in cycles or when you want to tone up/down a curve but keep " \
            "the first pose the same. It scales from the first value on each curve.\n"
    aboutText += "\n"
    aboutText += "Flip is a simple quick way to invert selected curves from their center value pivot.\n"

    pm.scrollField(editable=False, wordWrap=True, w=210, text=aboutText)
    pm.setParent('..')

    # Tabs
    pm.tabLayout(tabs, edit=True, tabLabel=((child1, 'Scaling'), (child2, 'About')))
    pm.showWindow(testWindow)


# Let's see if this code is worth the price we paid for it.
WindowUI()
