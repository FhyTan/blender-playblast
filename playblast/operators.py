import bpy
import gpu

from .render import offscreen_render


class PlayblastOperator(bpy.types.Operator):
    bl_idname = "playblast.run"
    bl_label = "Playblast"
    bl_description = "Create a playblast of the current scene"

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return True

    def execute(self, context: bpy.types.Context):
        scene = context.scene
        props = scene.playblast_props

        resolution = (
            context.scene.render.resolution_x,
            context.scene.render.resolution_y,
        )

        offscreen = gpu.types.GPUOffScreen(*resolution)

        output_dir = "C:/tmp"

        for frame in range(scene.frame_start, scene.frame_start + 2):
            scene.frame_set(frame)
            image = offscreen_render(context, offscreen)
            image.save(
                filepath=f"{output_dir}/playblast_{frame:04d}.png",
                quality=props.video.quality,
            )

        offscreen.free()

        return {"FINISHED"}
