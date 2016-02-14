from __future__ import unicode_literals

from tastypie.utils.timezone import now
from django.db import models
from jsonfield import JSONField


class Provider(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    phone = models.CharField(max_length=20)
    language = models.CharField(max_length=4)
    currency = models.CharField(max_length=3)
    created = models.DateTimeField(default=now)

    def __unicode__(self):
        return self.name


class ServiceArea(models.Model):
    provider = models.ForeignKey(Provider)
    name = models.CharField(max_length=200)
    price = models.FloatField()
    coordinates = JSONField()
    # This will have the minimum rectangle that contains the polygon to check fast if it's outside of it
    bounding_rectangle = JSONField()
    created = models.DateTimeField(default=now)

    def __unicode__(self):
        return self.name
