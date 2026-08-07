from django.contrib import admin

from .models import MetadataRaports, NewsletterSubscriber
# Register your models here.


@admin.register(MetadataRaports)
class MetadataReportsAdmin(admin.ModelAdmin):

    """This model stores pdf reports for specific car model"""

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



@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):

    """This model stores also checks if given email is already subscribing to newsletter"""

    readonly_fields= ('email','created_at')

    list_display= [
        'email',
        'created_at',
        'is_active'
    ]

    list_filter =['created_at', 'is_active']