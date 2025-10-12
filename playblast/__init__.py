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

from .handlers import draw_text_in_viewport_handler
from .operators import PlayblastOperator
from .panels import PlayblastBurnInPanel, PlayblastFilePanel, PlayblastPanel
from .properties import (
    BurnInProperties,
    FileProperties,
    PlayblastProperties,
    VideoProperties,
)

draw_handler = None


def register():
    global draw_handler

    # Register Operators
    bpy.utils.register_class(PlayblastOperator)

    # Register Property Groups
    bpy.utils.register_class(VideoProperties)
    bpy.utils.register_class(FileProperties)
    bpy.utils.register_class(BurnInProperties)
    bpy.utils.register_class(PlayblastProperties)
    bpy.types.Scene.playblast = bpy.props.PointerProperty(type=PlayblastProperties)

    # Register Panels
    bpy.utils.register_class(PlayblastPanel)
    bpy.utils.register_class(PlayblastBurnInPanel)
    bpy.utils.register_class(PlayblastFilePanel)

    # Register Handlers
    draw_handler = bpy.types.SpaceView3D.draw_handler_add(
        draw_text_in_viewport_handler, (), "WINDOW", "POST_PIXEL"
    )

    print(__name__, "registered")


def unregister():
    global draw_handler

    # Unregister Handlers
    if draw_handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(draw_handler, "WINDOW")

    # Unregister Panels
    bpy.utils.unregister_class(PlayblastFilePanel)
    bpy.utils.unregister_class(PlayblastBurnInPanel)
    bpy.utils.unregister_class(PlayblastPanel)

    # Unregister Property Groups
    del bpy.types.Scene.playblast
    bpy.utils.unregister_class(PlayblastProperties)
    bpy.utils.unregister_class(BurnInProperties)
    bpy.utils.unregister_class(FileProperties)
    bpy.utils.unregister_class(VideoProperties)

    # Unregister Operators
    bpy.utils.unregister_class(PlayblastOperator)

    print(__name__, "unregistered")
