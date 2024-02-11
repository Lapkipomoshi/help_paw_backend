from django_filters.rest_framework import BooleanFilter, CharFilter, FilterSet

from shelters.models import Pet, Shelter


class SheltersFilter(FilterSet):
    warnings = CharFilter(
        method='get_by_colour',
        help_text=('Фильтрация приютов по необходимости поддержки, '
                   'возможные значения: "red", "yellow", "green"')
    )
    is_favourite = BooleanFilter(
        method='get_favourite',
        help_text='true - отображает приюты добавленные пользователем в избранное, '
                  'false - недобавленные. '
                  'Для анонима всегда возращает пустой список'
    )
    is_helped = BooleanFilter(
        method='get_helped',
        help_text='true - отображает приюты которым пользователь жертвовал деньги, '
                  'false - которым не жертвовал. '
                  'Для анонима всегда возращает пустой список'
    )

    class Meta:
        model = Shelter
        fields = ('warnings', 'is_favourite', 'is_helped')

    # TODO Add logic when algorithm invented
    def get_by_colour(self, queryset, name, value):
        if value and value == 'red':
            return queryset.none()
        if value and value == 'yellow':
            return queryset
        if value and value == 'green':
            return queryset.none()
        return queryset.none()

    def get_favourite(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()
        if value:
            return queryset.filter(subscribers=self.request.user)
        return queryset.exclude(subscribers=self.request.user)

    def get_helped(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()
        if value:
            return queryset.filter(payments__user=self.request.user)
        return queryset.exclude(payments__user=self.request.user)


class PetFilter(FilterSet):
    animal_type = CharFilter(field_name='animal_type__slug')

    class Meta:
        model = Pet
        fields = ('animal_type',)
