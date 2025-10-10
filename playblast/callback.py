import bpy


@bpy.app.handlers.persistent
def frame_change_post_handler(scene):
    """Handler called after the frame is changed."""
    print("Frame changed to", scene.frame_current)
