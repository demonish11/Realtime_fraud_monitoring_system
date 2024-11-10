from django.db import models
from django.db.models import Q

class NotDeletedManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset().filter(deleted_at=None)
        return queryset


class WithDeletedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


class DeletedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(~Q(deleted_at=None))


class BaseModel(models.Model):
    created_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    updated_date = models.DateTimeField(blank=True, null=True, auto_now=True)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)
    objects = NotDeletedManager()
    with_deleted = WithDeletedManager()
    deleted = DeletedManager()

    class Meta:
        abstract = True