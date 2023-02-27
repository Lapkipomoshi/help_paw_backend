from django_filters.rest_framework import CharFilter, FilterSet, NumberFilter

from shelters.models import Pet, Shelter


class SheltersFilter(FilterSet):
    """Фильтрация по наличию задач у приюта"""
    warnings = CharFilter(
        method='get_by_colour',
        help_text=('Фильтрация приютов по наличию задач, возможные значения: '
                   '"red", "yellow", "green"')
    )

    class Meta:
        model = Shelter
        fields = ('warnings', )

    def get_by_colour(self, queryset, name, value):
        if value and value == 'red':
            return queryset.filter(task__is_emergency=True)
        if value and value == 'yellow':
            return queryset.filter(task__is_emergency=False)
        if value and value == 'green':
            return queryset.filter(task=None)


class PetFilter(FilterSet):
    shelter = NumberFilter(field_name='shelter')
    animal_type = CharFilter(field_name='animal_type__slug')

    class Meta:
        model = Pet
        fields = ('shelter', 'animal_type', )
