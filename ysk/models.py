from django.db import models


class TimeStampedModel(models.Model):
    """
        An abstract base class model that provides self-
        updating ``created`` and ``modified`` fields.
        """

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True
