from django.db import models

class ChatOption(models.Model):
    menu_text = models.CharField(max_length=255)
    response_text = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='suboptions')
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.menu_text