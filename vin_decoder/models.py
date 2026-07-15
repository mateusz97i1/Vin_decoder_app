import uuid

from django.db import models


# Create your models here.
class MetadataRaports(models.Model):

    """Model for storing URl's of AI generated pdf raports"""

    STATUS_CHOICES=[
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SUCCESS', 'Success'),
        ('FAILURE', 'Failure'),
    ]

    id= models.UUIDField(primary_key=True, default= uuid.uuid4, editable= False)
    car_model=models.CharField(max_length=100, unique=True)
    status= models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    supabase_url=models.URLField(max_length=500, blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add= True)
    updated_at= models.DateTimeField(auto_now= True)
    
    class Meta:

        verbose_name = "Metadata Report"
        verbose_name_plural = "Metadata Reports"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.car_model} ({self.status}) - {self.id} "