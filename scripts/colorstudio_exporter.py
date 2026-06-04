import bpy
import os
import json

bl_info = {
    "name": "ColorStudio Exporter",
    "blender": (3, 0, 0),
    "category": "Render",
    "description": "Génère les passes d'éclairage et le fichier JSON pour ColorStudio",
}

class ColorStudioSettings(bpy.types.PropertyGroup):
    output_directory: bpy.props.StringProperty(
        name="Dossier de sortie",
        description="Choisissez le dossier racine (ex: .../assets/images)",
        default="",
        subtype='DIR_PATH'
    )
    
    json_filename: bpy.props.StringProperty(
        name="Suffixe du JSON",
        description="Ce texte sera ajouté après le nom de la scène (ex: test_lumiere)",
        default="config" 
    )
    
    export_format: bpy.props.EnumProperty(
        name="Format",
        description="Choisissez le format des images",
        items=[
            ('OPEN_EXR', "HDR (OpenEXR)", "Haute qualité 32-bit pour le compositing"),
            ('JPEG', "LDR (JPEG)", "Basse qualité 8-bit pour des tests rapides")
        ],
        default='OPEN_EXR'
    )
    
    max_frames: bpy.props.EnumProperty(
        name="Limite d'images",
        description="Nombre d'images à rendre par lampe",
        items=[
            ('50', "50 images", "Test très rapide"),
            ('100', "100 images", "Test rapide"),
            ('150', "150 images", "Rendu intermédiaire"),
            ('200', "200 images", "Rendu avancé"),
            ('250', "250 images (Complet)", "Rendu final complet")
        ],
        default='250'
    )

class COLORSTUDIO_OT_render_passes(bpy.types.Operator):
    bl_idname = "colorstudio.render_passes"
    bl_label = "Générer les passes et le JSON"

    def execute(self, context):
        scene = context.scene
        cs_settings = scene.colorstudio_settings 

        base_dir = bpy.path.abspath(cs_settings.output_directory)
        if not base_dir:
            self.report({'ERROR'}, "Veuillez sélectionner un dossier de sortie dans le panneau !")
            return {'CANCELLED'}

       
        scene.render.image_settings.file_format = cs_settings.export_format
        
        if cs_settings.export_format == 'OPEN_EXR':
            scene.render.image_settings.color_depth = '32'
            file_ext = ".exr"
            is_hdr_flag = True
        else:
            scene.render.image_settings.color_depth = '8'
            file_ext = ".jpg"
            is_hdr_flag = False

 
        scene_name = scene.name
        output_dir = os.path.join(base_dir, scene_name)
        os.makedirs(output_dir, exist_ok=True)

        lights = [obj for obj in scene.objects if obj.type == 'LIGHT']

        if not lights:
            self.report({'ERROR'}, "Aucune lampe n'a été trouvée dans la scène !")
            return {'CANCELLED'}

      
        start_frame = scene.frame_start
        limite_choisie = int(cs_settings.max_frames)
        end_frame = min(start_frame + limite_choisie - 1, scene.frame_end)
        total_frames = (end_frame - start_frame) + 1

        render_file_path = f"{base_dir}/render_{scene_name}_final.jpg".replace('\\', '/')


        json_data = {
            "lights": [],
            "postprocesses": [
                {
                    "name": "white balance",
                    "chroma": { "type": "AWB", "color": { "r": 1.0, "g": 1.0, "b": 1.0 } }
                },
                {
                    "name": "auto exposure",
                    "luminance": { "type": "AE", "y": 0.5 }
                },
                {
                    "name": "gamma",
                    "luminance": { "type": "GAMMA", "gamma": 1.2 }
                }
            ],
            "renderFile": render_file_path
        }

     
        for current_light in lights:
            for l in lights:
                l.hide_render = True
            
            current_light.hide_render = False

            light_color = current_light.data.color
            
            chemin_image_json = f"{output_dir}/{current_light.name}_".replace('\\', '/')
            
            light_entry = {
                "name": current_light.name,
                "inputFile": {
                    "path": chemin_image_json, 
                    "ext": file_ext, 
                    "min": 0,
                    "max": total_frames,
                    "digit": 4,
                    "isHDR": is_hdr_flag 
                },
                "idxPos": 0,
                "exp": 0.0,
                "color": {
                    "r": round(light_color[0], 3),
                    "g": round(light_color[1], 3),
                    "b": round(light_color[2], 3)
                }
            }
            json_data["lights"].append(light_entry)

            for img_index, frame in enumerate(range(start_frame, end_frame + 1)):
                scene.frame_set(frame)

                filename = f"{current_light.name}_{img_index:04d}{file_ext}"
                scene.render.filepath = os.path.join(output_dir, filename)

                bpy.ops.render.render(write_still=True)

        for l in lights:
            l.hide_render = False


        suffixe = cs_settings.json_filename
        nom_fichier = f"{scene_name}_{suffixe}"
        if not nom_fichier.endswith('.json'):
            nom_fichier += '.json'
            
        json_filepath = os.path.join(base_dir, nom_fichier).replace('\\', '/')
        
        with open(json_filepath, 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, indent=4)

        self.report({'INFO'}, f"Génération terminée ! {total_frames} images/lampe. JSON créé : {nom_fichier}")
        return {'FINISHED'}

class COLORSTUDIO_PT_panel(bpy.types.Panel):
    bl_label = "ColorStudio Exporter"
    bl_idname = "COLORSTUDIO_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ColorStudio"

    def draw(self, context):
        layout = self.layout
        cs_settings = context.scene.colorstudio_settings

        layout.prop(cs_settings, "output_directory")
        layout.prop(cs_settings, "json_filename")
        layout.prop(cs_settings, "export_format") 
        layout.prop(cs_settings, "max_frames")
        
        layout.separator()
        
        layout.operator("colorstudio.render_passes", icon='LIGHT_SUN')

classes = (
    ColorStudioSettings,
    COLORSTUDIO_OT_render_passes,
    COLORSTUDIO_PT_panel
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.colorstudio_settings = bpy.props.PointerProperty(type=ColorStudioSettings)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.colorstudio_settings

if __name__ == "__main__":
    register()