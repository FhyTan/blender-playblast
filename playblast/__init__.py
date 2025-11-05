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
from .translations import translations_dict

draw_handler = None


def register():
    global draw_handler

    # Register Translations
    # bpy.app.translations.register(__name__, translations_dict)

    properties.register()
    operators.register()
    panels.register()

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

    panels.unregister()
    operators.unregister()
    properties.unregister()

    # Unregister Translations
    # bpy.app.translations.unregister(__name__)

    print(__name__, "unregistered")
