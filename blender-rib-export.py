#!BPY

# """ Registration info for Blender menus
# Name: 'Export to RIB'
# Blender: 248
# Group: 'Render'
# Tip: 'Export to Renderman RIB format'
# """

__author__ = 'Roland Kuck'
__version__ = '1.0 2009/08/19'
__url__ = "Author's site, http://www.kuck.name/blender-rib-export/"
__email__ = "Roland Kuck, blenderrib:roland*kuck*name"
__bpydoc__ = """\
This script exports the current scene into a RIB file that can be rendered by a Renderman-compliant renderer.
"""

import Blender
from Blender import Draw
from Blender import BGL
from Blender import Window

import ribexport.export
from ribexport import config

class UI(object):
    "User interface class for export plug-in"

    EVENT_NONE = 1
    EVENT_EXIT = 2
    EVENT_RENDER = 3
    EVENT_FILECHOOSER = 4

    def __init__(self):
        super(UI, self).__init__()
        self._output = ''

    def _get_scene(self):
        return Blender.Scene.GetCurrent()

    def _get_properties(self):
        properties = self._get_scene().properties
        if config.property_group not in properties:
            properties[config.property_group] = { 'Output': 'output.rib' }
        return properties[config.property_group]

    def _get_output(self):
        return self._get_properties()['Output']

    def _set_output(self, value):
        self._get_properties()['Output'] = value

    def _draw(self):
        BGL.glClear(BGL.GL_COLOR_BUFFER_BIT)

        height = 32
        y_pos = 10

        quit_text = "Quit"
        Draw.Button(quit_text, self.EVENT_EXIT, 10, y_pos, 2 * Draw.GetStringWidth(quit_text), height, "Quit script")
        y_pos += int(height * 1.5)

        render_text = "Render"
        Draw.Button(render_text, self.EVENT_RENDER, 10, y_pos, 2 * Draw.GetStringWidth(render_text), height, "Render scene to output")
        y_pos += int(height * 1.5)

        file_chooser_text = "..."
        Draw.Button(file_chooser_text, self.EVENT_FILECHOOSER, 10, y_pos, 2 * Draw.GetStringWidth(file_chooser_text), height, "Select file from file system")

        Draw.String("Output: ", self.EVENT_NONE, 2*Draw.GetStringWidth(file_chooser_text) + 10, y_pos, 256, height, self._get_output(), 399,
                    "Name of output file", self._output_input_callback)

    def _event(self, event, pressed):
        if event == Draw.ESCKEY and pressed:
            Draw.Exit()

    def _button_event(self, evt):
        if evt == self.EVENT_EXIT:
            Draw.Exit()
        elif evt == self.EVENT_FILECHOOSER:
            Window.FileSelector(self._output_file_callback, "Select output RIB name", self._get_output())
        elif evt == self.EVENT_RENDER:
            scene = self._get_scene()
            ribexport.export.export(self._get_output(), scene)

    def _output_file_callback(self, filename):
        self._set_output(filename)
        Draw.Redraw(1)

    def _output_input_callback(self, event, filename):
        self._set_output(filename)

    def register(self):
        Draw.Register(self._draw, self._event, self._button_event)


ui = UI()
ui.register()
