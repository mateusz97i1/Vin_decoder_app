import pytest
from django.urls import reverse


def test_simple_view_render_correctly(client):
    url = reverse("vin_decoder:home")
    response = client.get(url)
    assert response.status_code == 200