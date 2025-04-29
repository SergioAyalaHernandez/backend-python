from django.db import models

class Actividad(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    fechaInicio = models.DateField()
    fechaFin = models.DateField()
    horaInicio = models.TimeField(null=True, blank=True) 
    horaFin = models.TimeField(null=True, blank=True)     
    cupoMaximo = models.IntegerField(null=True, blank=True)
    recursos = models.TextField(null=True, blank=True)
    categoria = models.CharField(max_length=100)
    enlace = models.URLField(max_length=500, null=True, blank=True) 
    imagen = models.ImageField(upload_to='imagenes_actividades/', null=True, blank=True)

    def __str__(self):
        return self.nombre
