from django.contrib import admin

from .models import MetadataRaports
# Register your models here.


@admin.register(MetadataRaports)
class MetadataReportsAdmin(admin.ModelAdmin):

    readonly_fields=('id','created_at', 'updated_at', 'most_recent_download')

    list_display = [
        'id',
        'car_model',
        'status',
        'supabase_url',
        'created_at',
        'updated_at',
        'most_recent_download'
    ]

    list_filter = ['car_model','created_at']