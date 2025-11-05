import bpy
from bl_ui.utils import PresetPanel

from .metadata import META_DATA_DESCRIPTIONS

# class PLAYBLAST_MT_presets(Menu):
#     bl_label = "Playblast Presets"
#     preset_subdir = "playblast"
#     preset_operator = "script.execute_preset"
#     draw = Menu.draw_preset


class PLAYBLAST_PT_presets(PresetPanel, bpy.types.Panel):
    bl_label = "Playblast Presets"
    preset_subdir = "playblast"
    preset_operator = "script.execute_preset"
    preset_add_operator = "playblast.preset_add"

    @staticmethod
    def post_cb(context, _filepath):
        # Modify an arbitrary built-in scene property to force a depsgraph
        # update, because add-on properties don't. (see #62325)
        render = context.scene.render
        render.filter_size = render.filter_size


class PlayblastPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_playblast"
    bl_label = "Playblast"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header_preset(self, context):
        PLAYBLAST_PT_presets.draw_panel_header(self.layout)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        video_props = context.scene.playblast.video
        layout.operator("playblast.run", text="Run", icon="RENDER_ANIMATION")
        layout.separator()

        col = layout.column()
        col.prop(video_props, "include_audio")
        col.prop(video_props, "codec")


class PlayblastOverridePanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_playblast_override"
    bl_label = "Override"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_parent_id = "VIEW3D_PT_playblast"
    bl_order = 0

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        override_props = context.scene.playblast.override

        col = layout.column()

        col.prop(override_props, "scale")

        row = col.row(align=True, heading="Frame Range")
        row.prop(override_props, "use_frame_range", text="")
        sub = row.column()
        sub.active = override_props.use_frame_range
        sub.prop(override_props, "frame_start", text="Start")
        sub.prop(override_props, "frame_end", text="End")

        col.prop(override_props, "show_overlays", icon="OVERLAY")

        col = layout.column()
        row = col.row(align=True, heading="Viewport Shading")
        row.prop(override_props, "use_viewport_shading", text="")
        sub = row.row()
        sub.active = override_props.use_viewport_shading
        sub.prop(override_props, "viewport_shading", text="", expand=True)


class PlayblastFilePanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_playblast_file"
    bl_label = "File"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_parent_id = "VIEW3D_PT_playblast"
    bl_order = 1

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        file_props = context.scene.playblast.file

        col = layout.column()

        col.prop(
            file_props,
            "directory",
            placeholder="Default to current blend file directory",
        )
        col.prop(file_props, "name")

        row = col.row(align=True, heading="Version")
        row.prop(file_props, "use_version", text="")
        sub = row.row(align=True)
        sub.active = file_props.use_version
        sub.prop(file_props, "version", text="")

        col.prop(file_props, "extension")
        col.prop(file_props, "full_path")


class PlayblastBurnInPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_playblast_burn_in"
    bl_label = "Burn-In Data"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_parent_id = "VIEW3D_PT_playblast"
    bl_order = 2

    def draw_header(self, context: bpy.types.Context):
        layout = self.layout

        burn_in_props = context.scene.playblast.burn_in
        layout.prop(burn_in_props, "enable", text="")
        layout.popover(
            panel="VIEW3D_PT_playblast_burn_in_help", text="", icon="QUESTION"
        )

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        burn_in_props = context.scene.playblast.burn_in

        col = layout.column()
        col.enabled = burn_in_props.enable

        col = layout.column()
        col.enabled = burn_in_props.enable

        col.prop(burn_in_props, "preview")
        col.prop(burn_in_props, "font_family", placeholder="Default to Blender Font")
        col.prop(burn_in_props, "font_size")
        col.prop(burn_in_props, "margin")
        col.prop(burn_in_props, "color")
        col.prop(burn_in_props, "top_left")
        col.prop(burn_in_props, "top_center")
        col.prop(burn_in_props, "top_right")
        col.prop(burn_in_props, "bottom_left")
        col.prop(burn_in_props, "bottom_center")
        col.prop(burn_in_props, "bottom_right")


class PlayblastBurnInHelpPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_playblast_burn_in_help"
    bl_label = "Burn-In Data Help"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_ui_units_x = 25
    bl_options = {"INSTANCED"}

    def draw(self, context: bpy.types.Context):
        layout = self.layout

        layout.label(
            text="Use curly braces {} to denote variables in text, for example {datetime} for the current time."
        )
        layout.label(text="The following variables are currently available:")

        grid = layout.grid_flow(row_major=True, columns=2)
        for key, description in META_DATA_DESCRIPTIONS.items():
            grid.label(text=f"{{{key}}}")
            grid.label(text=description)


class PlayblastSettingsPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_playblast_settings"
    bl_label = "Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_parent_id = "VIEW3D_PT_playblast"
    bl_order = 3

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        col.operator(
            "playblast.save_as_default", text="Save as Default", icon="FILE_TICK"
        )

        row = layout.row()
        row.operator("playblast.import_settings", text="Import", icon="IMPORT")
        row.operator("playblast.export_settings", text="Export", icon="EXPORT")
