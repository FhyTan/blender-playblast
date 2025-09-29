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

from .operators import PlayblastOperator
from .panels import PlayblastBurnInPanel, PlayblastFilePanel, PlayblastPanel
from .properties import (
    BurnInProperties,
    FileProperties,
    PlayblastProperties,
    VideoProperties,
)
from .render import draw_burn_in_text_in_viewport

draw_handler = None


def register():
    global draw_handler

    # Register Property Groups
    bpy.utils.register_class(VideoProperties)
    bpy.utils.register_class(FileProperties)
    bpy.utils.register_class(BurnInProperties)
    bpy.utils.register_class(PlayblastProperties)
    bpy.types.Scene.playblast_props = bpy.props.PointerProperty(
        type=PlayblastProperties
    )

    # Register Operators
    bpy.utils.register_class(PlayblastOperator)

    # Register Panels
    bpy.utils.register_class(PlayblastPanel)
    bpy.utils.register_class(PlayblastBurnInPanel)
    bpy.utils.register_class(PlayblastFilePanel)

    draw_handler = bpy.types.SpaceView3D.draw_handler_add(
        draw_burn_in_text_in_viewport, (), "WINDOW", "POST_PIXEL"
    )

    print(__name__, "registered")


def unregister():
    global draw_handler

    if draw_handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(draw_handler, "WINDOW")

    # Unregister Panels
    bpy.utils.unregister_class(PlayblastFilePanel)
    bpy.utils.unregister_class(PlayblastBurnInPanel)
    bpy.utils.unregister_class(PlayblastPanel)

    # Unregister Operators
    bpy.utils.unregister_class(PlayblastOperator)

    # Unregister Property Groups
    del bpy.types.Scene.playblast_props
    bpy.utils.unregister_class(PlayblastProperties)
    bpy.utils.unregister_class(BurnInProperties)
    bpy.utils.unregister_class(FileProperties)
    bpy.utils.unregister_class(VideoProperties)

    print(__name__, "unregistered")
