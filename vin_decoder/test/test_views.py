import pytest

from django.urls import reverse
from django.test import Client


#list of views that just render html templates
basic_views=[
    'vin_decoder:rules',
    'vin_decoder:privacy_policy',
    'vin_decoder:about_us',
    'vin_decoder:contact',
]


@pytest.mark.parametrize("url_name", basic_views)
def test_simple_view_render_correctly(client : Client, url_name : str) -> None:
    """Tests all views that just generate template view"""

    url = reverse(url_name)

    response = client.get(url)

    assert response.status_code == 200