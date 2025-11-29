from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=255)
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.FloatField(default=1)
    importance = models.IntegerField(default=5)
    # Dependencies stored as self-referential M2M for completeness (not required for stateless POST)
    dependencies = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='dependents')

    def __str__(self):
        return self.title
