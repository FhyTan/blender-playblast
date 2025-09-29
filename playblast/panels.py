import bpy


class PlayblastPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_playblast"
    bl_label = "Playblast"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        video_props = context.scene.playblast_props.video
        layout.prop(video_props, "codec")
        layout.prop(video_props, "quality")


class PlayblastFilePanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_playblast_file"
    bl_label = "Save To File"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_parent_id = "VIEW3D_PT_playblast"
    bl_order = 0

    def draw_header(self, context: bpy.types.Context):
        file_props = context.scene.playblast_props.file
        self.layout.prop(file_props, "enable", text="")

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        file_props = context.scene.playblast_props.file

        col = layout.column()
        col.enabled = file_props.enable

        col.prop(file_props, "directory")
        col.prop(file_props, "filename")

        row = col.row(align=True, heading="Version")
        row.prop(file_props, "use_version", text="")
        sub = row.row(align=True)
        sub.active = file_props.use_version
        sub.prop(file_props, "version", text="")

        col.prop(file_props, "extension")
        col.prop(file_props, "full_path")


class PlayblastBurnInPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_playblast_burn_in"
    bl_label = "Burn In Data"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_parent_id = "VIEW3D_PT_playblast"
    bl_order = 1

    def draw_header(self, context: bpy.types.Context):
        burn_in_props = context.scene.playblast_props.burn_in
        self.layout.prop(burn_in_props, "enable", text="")

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        burn_in_props = context.scene.playblast_props.burn_in

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
