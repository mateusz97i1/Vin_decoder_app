from django.contrib import admin

from .models import MetadataRaports
# Register your models here.


@admin.register(MetadataRaports)
class MetadataReportsAdmin(admin.ModelAdmin):

    readonly_fields=('id','created_at', 'updated_at')

    list_display = [
        'id',
        'car_model',
        'status',
        'supabase_url',
        'created_at',
        'updated_at',
    ]

    list_filter = ['car_model','created_at']