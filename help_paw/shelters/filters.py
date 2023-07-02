from django_filters.rest_framework import BooleanFilter, CharFilter, FilterSet

from shelters.models import Pet, Shelter


class SheltersFilter(FilterSet):
    """Фильтрация по наличию задач у приюта"""
    warnings = CharFilter(
        method='get_by_colour',
        help_text=('Фильтрация приютов по наличию задач, возможные значения: '
                   '"red", "yellow", "green"')
    )
    is_favourite = BooleanFilter(method='get_favourite')
    is_helped = BooleanFilter(method='get_helped')

    class Meta:
        model = Shelter
        fields = ('warnings', 'is_favourite')

    # TODO Add logic when algorithm invented
    def get_by_colour(self, queryset, name, value):
        if value and value == 'red':
            return queryset.none()
        if value and value == 'yellow':
            return queryset
        if value and value == 'green':
            return queryset.none()

    def get_favourite(self, queryset, name, value):
        if value:
            return queryset.filter(subscribers=self.request.user)
        return queryset

    # TODO Add logic when payment added
    def get_helped(self, queryset, name, value):
        if value:
            return queryset.order_by('?')[:3]
        return queryset


class PetFilter(FilterSet):
    animal_type = CharFilter(field_name='animal_type__slug')

    class Meta:
        model = Pet
        fields = ('animal_type',)
