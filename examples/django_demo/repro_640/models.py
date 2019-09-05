from __future__ import unicode_literals

from django.db import models


class Route(models.Model):
    name = models.CharField(max_length=20)


class RouteSlot(models.Model):
    name = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()
    route = models.ForeignKey(Route, on_delete=models.CASCADE)


class VehicleRide(models.Model):
    route_slot = models.ForeignKey(RouteSlot, on_delete=models.CASCADE)
    date = models.DateField()


class Stop(models.Model):
    name = models.CharField(max_length=20)


class CustomerRide(models.Model):
    vehicle_ride = models.OneToOneField(VehicleRide, on_delete=models.CASCADE)
    start_stop = models.ForeignKey(Stop, related_name='+', on_delete=models.CASCADE)
    end_stop = models.ForeignKey(Stop, related_name='+', on_delete=models.CASCADE)


class RouteSlotStopInfo(models.Model):
    route_slot = models.ForeignKey(RouteSlot, on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)

    order = models.IntegerField()
    arrival_time = models.DateTimeField()
    departure_time = models.DateTimeField()
