import pytest

from info.models import Article


@pytest.fixture
def article():
    artical = Article.objects.create(
        header='Заголовок',
        text='Текст',
        profile_image='test.jpg',
    )
    return artical
