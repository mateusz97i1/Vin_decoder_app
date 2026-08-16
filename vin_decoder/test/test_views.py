import pytest

from django.urls import reverse
from django.test import Client

from vin_decoder.models import NewsletterSubscriber, MetadataRaports



#------------------------ FIXTURES--------------------------
@pytest.fixture
def database_mock_obj_metadaReports() -> None:
    """Creates a single MetadataRaports row with status SUCCESS."""

    MetadataRaports.objects.create(
        car_model = "FORD",
        status = "SUCCESS",
        supabase_url="test_url"
    )


@pytest.fixture
def database_mock_obj_newslettersubscriber() -> None:
    """Creates a single active NewsletterSubscriber row."""

    NewsletterSubscriber.objects.create(
        email = "test.email@test.pl"
    )

"""Creates a single test user."""
@pytest.fixture
def database_mock_user(django_user_model):

    user = django_user_model.objects.create_user(
            username = "test_user", password= "test_pass", email="test_email@test.com"
        )

    return user



    
# ------------------------TEST_CASES-------------------------
class Test_simple_view_only_renders_template:
    """Tests all views that just generate template view, no extra logic"""


    #list of views that just render html templates
    BASIC_VIEWS_AND_TEMPLATES=[
        ('vin_decoder:rules','rules.html'),
        ('vin_decoder:privacy_policy','privacy_policy.html'),
        ('vin_decoder:about_us','about_us.html'),
        ('vin_decoder:contact','contact.html'),
    ]


    @pytest.mark.parametrize('url_name , template_name', BASIC_VIEWS_AND_TEMPLATES)
    def test_simple_view_render_correctly(self, client : Client, url_name : str, template_name: str) -> None:
        """Get 200 response and renders expected template"""

        url = reverse(url_name)

        response = client.get(url)


        assert response.status_code == 200
        assert template_name in [t.name for t in response.templates]

    @pytest.mark.parametrize('url_name , template_name', BASIC_VIEWS_AND_TEMPLATES)
    def test_post_not_allowed(self, client : Client, url_name : str, template_name: str) -> None:
        """functions are reuied_safe so post should be rejected"""

        url = reverse(url_name)

        response = client.post(url)

        assert response.status_code == 405