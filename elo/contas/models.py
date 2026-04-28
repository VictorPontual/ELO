from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Pesquisador(models.Model):
    FORMACAO_CHOICES = [
        ('graduacao', 'Graduação'),
        ('mestrado', 'Mestrado'),
        ('doutorado', 'Doutorado'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    formacao = models.CharField(max_length=15, choices=FORMACAO_CHOICES, default='graduacao')
    celular = models.CharField(max_length=25, blank=True, null=True)
    preferencia_comunicacao_celular = models.BooleanField(default=False)
    preferencia_comunicacao_email = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'pesquisador'
    
    def __str__(self):
        return self.user.get_full_name()
