from django.db import models
from django.conf import settings

# Create your models here.
class User(models.Model):
    username=models.CharField(max_length=150,unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, default='user')

    def __str__(self):
        return f"{self.username} - {self.email} - {self.password}"
    

class Slips(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,   # links to your User model (drivers/admins)
        on_delete=models.CASCADE,
        related_name="slips"
    )
    file = models.FileField(upload_to="slips/")  # files will be saved in MEDIA_ROOT/slips/
    file_name = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=100,default="Unknown", blank=False)

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="pending"
    )

    @property
    def is_image(self):
        """Check if file is an image based on extension."""
        return self.file.name.lower().endswith(('.jpg', '.jpeg', '.png'))

    def __str__(self):
        return f"{self.user.username} - {self.file_name or self.file.name}"

    def save(self, *args, **kwargs):
        if self.file:
            self.file_name = self.file.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.file_name} ({self.status})"