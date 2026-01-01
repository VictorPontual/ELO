from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Pesquisador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # O campo 'nome' e 'email' podem ser gerenciados pelo modelo User (first_name, last_name, email)
    titulo = models.CharField(max_length=100, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username
