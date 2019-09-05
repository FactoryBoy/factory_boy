import datetime

import factory
import factory.django
import factory.fuzzy

from django.utils import timezone

from . import models


class StopFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Stop

    name = factory.Sequence(lambda n: "Stop #%d" % n)


class RouteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Route

    name = factory.Sequence(lambda n: "Route #%d" % n)


class RouteSlotStopInfoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.RouteSlotStopInfo

    order = factory.Sequence(lambda n: n)
    route_slot = factory.SubFactory('repro_640.RouteSlot')
    stop = factory.SubFactory(StopFactory)
    arrival_time = factory.fuzzy.FuzzyDateTime(start_dt=timezone.now())
    departure_time = factory.fuzzy.FuzzyDateTime(start_dt=timezone.now())


class RouteSlotFactory(factory.django.DjangoModelFactory): 
    class Meta:
        model = models.RouteSlot
        django_get_or_create = ('pk',)

    route = factory.SubFactory(RouteFactory)

    pk = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: 'Route Slot #' + str(n))
    start_time = factory.LazyFunction(lambda: (timezone.localtime(timezone.now()) + datetime.timedelta(minutes=10)).time())
    end_time = factory.LazyAttribute(lambda obj: (datetime.datetime.combine(timezone.localtime(timezone.now()).date(), obj.start_time) + datetime.timedelta(minutes=10)).time())

    @factory.post_generation
    def route_slot_stop_infos(self, create, extracted, **kwargs):
        rs = []
        stop_time = datetime.datetime.combine(timezone.localtime(timezone.now()).date(), self.start_time)
        for i in range(3):
            stop_time = stop_time + datetime.timedelta(minutes=2)
            rs.append(
                RouteSlotStopInfoFactory(
                    route_slot=self,
                    order=i,
                    stop=StopFactory(pk=self.route.pk*3+i),
                    arrival_time=stop_time,
                    departure_time=stop_time,
                )
            )

        self.route_slot_stop_infos = rs
        return rs


class VehicleRideFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.VehicleRide

    route_slot = factory.SubFactory(RouteSlotFactory)
    date = factory.LazyFunction(lambda: timezone.localtime(timezone.now()).date())


class CustomerRideFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.CustomerRide

    vehicle_ride = factory.SubFactory(VehicleRideFactory)
    start_stop = factory.LazyAttribute(lambda obj: obj.vehicle_ride.route_slot.route_slot_stop_infos[0].stop)  # <-- This is where I get that error
    end_stop = factory.LazyAttribute(lambda obj: obj.vehicle_ride.route_slot.route_slot_stop_infos[-1].stop)


