from django.contrib import admin
from django.utils.html import format_html
from .models import Model3D

@admin.register(Model3D)
class Model3DAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'user', 'created_at', 'model_folder', 'preview_model')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'category__category_name', 'user__first_name', 'user__last_name')

    readonly_fields = ('preview_model', 'created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('name', 'model_file', 'preview_model', 'category', 'user')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    class Media:
        js = ('https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js',)

    def preview_model(self, obj):
        """3D model preview inside the admin panel"""
        if obj.model_file:
            return format_html(
                '''
                <div style="text-align:center;">
                    <model-viewer
                        src="{}"
                        camera-controls
                        auto-rotate
                        ar
                        style="width: 250px; height: 250px; border-radius: 10px; background: #f9f9f9; border: 1px solid #ccc;">
                    </model-viewer>
                </div>
                ''',
                obj.model_file.url
            )
        return "⚠️ No model uploaded"
    preview_model.short_description = "3D Preview"

    def model_folder(self, obj):
        """Show the unique folder where the model is stored"""
        if obj.model_file:
            return obj.model_file.url.rsplit('/', 2)[-2]
        return "-"
    model_folder.short_description = "Folder"
