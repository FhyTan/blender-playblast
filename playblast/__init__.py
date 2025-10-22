# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy

from . import handlers, operators, panels, properties

draw_handler = None


def register():
    global draw_handler

    # Register Operators
    bpy.utils.register_class(operators.PlayblastOperator)
    bpy.utils.register_class(operators.SaveAsDefaultOperator)
    bpy.utils.register_class(operators.ImportSettingsOperator)
    bpy.utils.register_class(operators.ExportSettingsOperator)

    # Register Property Groups
    bpy.utils.register_class(properties.VideoProperties)
    bpy.utils.register_class(properties.FileProperties)
    bpy.utils.register_class(properties.BurnInProperties)
    bpy.utils.register_class(properties.PlayblastProperties)
    bpy.types.Scene.playblast = bpy.props.PointerProperty(
        type=properties.PlayblastProperties
    )

    # Register Panels
    bpy.utils.register_class(panels.PlayblastPanel)
    bpy.utils.register_class(panels.PlayblastBurnInPanel)
    bpy.utils.register_class(panels.PlayblastFilePanel)
    bpy.utils.register_class(panels.PlayblastSettingsPanel)

    # Register Handlers
    bpy.app.handlers.load_post.append(handlers.load_default_settings_for_new_file)
    draw_handler = bpy.types.SpaceView3D.draw_handler_add(
        handlers.draw_text_in_viewport_handler, (), "WINDOW", "POST_PIXEL"
    )

    print(__name__, "registered")


def unregister():
    global draw_handler

    # Unregister Handlers
    if draw_handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(draw_handler, "WINDOW")
    bpy.app.handlers.load_post.remove(handlers.load_default_settings_for_new_file)

    # Unregister Panels
    bpy.utils.unregister_class(panels.PlayblastSettingsPanel)
    bpy.utils.unregister_class(panels.PlayblastFilePanel)
    bpy.utils.unregister_class(panels.PlayblastBurnInPanel)
    bpy.utils.unregister_class(panels.PlayblastPanel)

    # Unregister Property Groups
    del bpy.types.Scene.playblast
    bpy.utils.unregister_class(properties.PlayblastProperties)
    bpy.utils.unregister_class(properties.BurnInProperties)
    bpy.utils.unregister_class(properties.FileProperties)
    bpy.utils.unregister_class(properties.VideoProperties)

    # Unregister Operators
    bpy.utils.unregister_class(operators.ExportSettingsOperator)
    bpy.utils.unregister_class(operators.ImportSettingsOperator)
    bpy.utils.unregister_class(operators.SaveAsDefaultOperator)
    bpy.utils.unregister_class(operators.PlayblastOperator)

    print(__name__, "unregistered")
