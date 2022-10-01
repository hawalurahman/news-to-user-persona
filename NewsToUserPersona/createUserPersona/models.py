from django.db import models
import json

# Create your models here.
class UserPersona(models.Model):   
    def user_persona(self):
        return json.loads(self.saved_data)