from django.db import models


class IngestedModelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(exists_in_last_import=True)


class IngestedModel(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    exists_in_last_import = models.BooleanField(default=True)

    objects = IngestedModelManager()
