import logging
from tastypie.authorization import Authorization
from tastypie import fields
from tastypie.resources import ModelResource
from serviceareas.models import Provider, ServiceArea
from serviceareas.validators import ProviderValidator, ServiceAreaValidator


class ProviderResource(ModelResource):
    class Meta:
        queryset = Provider.objects.all()
        resource_name = 'provider'
        authorization = Authorization()
        validation = ProviderValidator()

    def determine_format(self, request):
        return 'application/json'


class ServiceAreaResource(ModelResource):
    provider = fields.ForeignKey(ProviderResource, 'provider', full=True)

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        orm_filters = super(ServiceAreaResource, self).build_filters(filters)

        if 'lat' in filters and 'lng' in filters:
            orm_filters["lat"] = filters['lat']
            orm_filters["lng"] = filters['lng']

        return orm_filters

    def point_in_poly(self, x, y, coordinates):
        j = len(coordinates) - 1
        c = False
        for i in range(len(coordinates)):
            if ((((coordinates[i][1] <= y) and (y < coordinates[j][1])) or
                 ((coordinates[j][1] <= y) and (y < coordinates[i][1]))) and
                (x < (coordinates[j][0] - coordinates[i][0]) * (y - coordinates[i][1]) /
                    (coordinates[j][1] - coordinates[i][1]) + coordinates[i][0])):
                c = not c
            j = i

        return c

    def in_coordinates(self, lat, lng):
        def partial(area):
            boundaries = area.bounding_rectangle
            if not (boundaries[0][0] <= lat <= boundaries[1][0] and boundaries[0][1] <= lng <= boundaries[1][1]):
                return False

            coordinates = area.coordinates

            if not self.point_in_poly(lat, lng, coordinates[0]):
                return False

            if len(coordinates) == 1:
                return True

            for poly in coordinates[1:]:
                if self.point_in_poly(lat, lng, poly):
                    return False

            return True
        return partial

    def apply_filters(self, request, applicable_filters):
        lat = lng = None
        try:
            if 'lat' in applicable_filters:
                lat = applicable_filters.pop('lat')
                lat = float(lat)
            if 'lng' in applicable_filters:
                lng = applicable_filters.pop('lng')
                lng = float(lng)
        except ValueError as ve:
            logging.info('Invalid values for lat/lng: {}, {}'.format(lat, lng))

        semi_filtered = super(ServiceAreaResource, self).apply_filters(request, applicable_filters)

        if lat is not None and lng is not None and type(lat) == type(lng) == float:
            return filter(self.in_coordinates(lat, lng), semi_filtered)
        else:
            return semi_filtered


    class Meta:
        queryset = ServiceArea.objects.all()
        resource_name = 'service_area'
        authorization = Authorization()
        validation = ServiceAreaValidator()

    def hydrate(self, bundle):
        coordinates = bundle.data['coordinates'][0]
        lower_boundary_x = min([e[0] for e in coordinates])
        lower_boundary_y = min([e[1] for e in coordinates])
        upper_boundary_x = max([e[0] for e in coordinates])
        upper_boundary_y = max([e[1] for e in coordinates])

        bundle.obj.bounding_rectangle = [[lower_boundary_x, lower_boundary_y], [upper_boundary_x, upper_boundary_y]]
        return bundle

    def dehydrate(self, bundle):
        bundle.data['provider'] = bundle.data['provider'].data['name']
        del bundle.data['coordinates']
        del bundle.data['bounding_rectangle']
        del bundle.data['created']
        del bundle.data['resource_uri']
        del bundle.data['id']
        return bundle

    def determine_format(self, request):
        return 'application/json'
