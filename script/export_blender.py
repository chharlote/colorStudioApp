import bpy
import os

bl_info = {
    "name": "ColorStudio Exporter",
    "blender": (3, 0, 0),
    "category": "Render",
    "description": "Génère les passes d'éclairage pour ColorStudio",
}

class COLORSTUDIO_OT_render_passes(bpy.types.Operator):
    bl_idname = "colorstudio.render_passes"
    bl_label = "Générer les passes lumineuses"

    def execute(self, context):
            scene = context.scene
            
            # 1. FORCER LE FORMAT HDR
            scene.render.image_settings.file_format = 'HDR'
            
            # 2. CRÉER LE DOSSIER AVEC LE NOM DE LA SCÈNE
            base_dir = "C:/Users/charl/Documents/BUT3_semestre_6/sae_maintenance/colorStudioApp/assets/images"
            scene_name = scene.name 
            output_dir = os.path.join(base_dir, scene_name)
            os.makedirs(output_dir, exist_ok=True)
            
            # 3. RÉCUPÉRER TOUTES LES LAMPES DE LA SCÈNE
            lights = [obj for obj in scene.objects if obj.type == 'LIGHT']
            
            if not lights:
                self.report({'ERROR'}, "Aucune lampe n'a été trouvée dans la scène !")
                return {'CANCELLED'}
                
            # 4. BOUCLER SUR CHAQUE LAMPE
            for current_light in lights:
                
                # Étape cruciale : Éteindre TOUTES les lampes pour le rendu
                for l in lights:
                    l.hide_render = True
                    
                # Allumer UNIQUEMENT la lampe que l'on traite actuellement
                current_light.hide_render = False
                
                # 5. BOUCLER SUR LA TRAJECTOIRE (TIMELINE)
                for frame in range(scene.frame_start, scene.frame_end + 1):
                    scene.frame_set(frame) 
                    
                    # Le nom du fichier prend automatiquement le nom de la lampe (Light, Light.001, etc.)
                    filename = f"{current_light.name}_{frame:04d}.hdr"
                    scene.render.filepath = os.path.join(output_dir, filename)
                    
                    # Lancer le rendu
                    bpy.ops.render.render(write_still=True)
                    
            # RESTAURATION : Rallumer toutes les lampes dans la scène à la fin du script
            for l in lights:
                l.hide_render = False
                
            self.report({'INFO'}, f"Génération terminée pour {len(lights)} lampes dans {scene_name} !")
            return {'FINISHED'}


class COLORSTUDIO_PT_panel(bpy.types.Panel):
    bl_label = "ColorStudio"
    bl_idname = "COLORSTUDIO_PT_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        # Bouton qui appelle notre opérateur
        layout.operator("colorstudio.render_passes", icon='LIGHT_SUN')


def register():
    bpy.utils.register_class(COLORSTUDIO_OT_render_passes)
    bpy.utils.register_class(COLORSTUDIO_PT_panel)

def unregister():
    bpy.utils.unregister_class(COLORSTUDIO_PT_panel)
    bpy.utils.unregister_class(COLORSTUDIO_OT_render_passes)

if __name__ == "__main__":
    register()