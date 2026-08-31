import pytest

from django.urls import reverse
from django.test import Client
from unittest.mock import patch, PropertyMock

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



class Test_newsletter_subscription:
    """tests view: thanks_for_newsletter_subscription"""

    pytestmark = pytest.mark.django_db
    url_name = 'vin_decoder:thanks_newsletter_sub'
    template_name = 'partials/newsletter_block.html'
    test_valid_email = 'test@mail.com'
    test_invalid_email = 'invalid_email'

    def test_newsletter_partial_correct_render(self, client : Client) -> None:

        
        url = reverse(self.url_name)

        response = client.post(url)

        assert response.status_code == 200
        assert self.template_name in [t.name for t in response.templates]


    @patch('vin_decoder.views.join_newsletter.delay')
    def test_valid_form_to_send_email_success(self, mock_delay ,client: Client) -> None:

        url = reverse(self.url_name)

        response = client.post(url, data={'send_email_to' : self.test_valid_email})

        assert response.status_code == 200
        assert response.context['success'] is True
        assert NewsletterSubscriber.objects.filter(email= self.test_valid_email).exists()
        mock_delay.assert_called_once_with(self.test_valid_email)


    @patch('vin_decoder.views.join_newsletter.delay')
    def test_invalid_form_to_send_mail_return_error(self, mock_delay , client : Client) -> None:

        url= reverse(self.url_name)

        response = client.post(url, data = {'send_email_to' : self.test_invalid_email})

        assert response.status_code == 200
        assert response.context['success'] is False
        assert NewsletterSubscriber.objects.filter(email = self.test_invalid_email).count() == 0
        mock_delay.assert_not_called()


    @patch('vin_decoder.views.join_newsletter.delay')
    def test_duplicate_email_return_error(self, mock_delay , client: Client) -> None:

        NewsletterSubscriber.objects.create(email= self.test_valid_email)
        
        url = reverse(self.url_name)

        response = client.post(url, data = {'send_email_to' : self.test_valid_email})

        assert response.status_code == 200
        assert response.context['success'] is False
        assert response.context['error'] == 'This email has been already used.'
        assert NewsletterSubscriber.objects.filter(email = self.test_valid_email).count() == 1
        mock_delay.assert_not_called()



class Test_export_vin_raport_pdf:
    """ test export_vin_raport_pdf view login is requied for all tests """

    pytestmark = pytest.mark.django_db
    url_name = 'vin_decoder:export_pdf'
    partial_template_name = "partials/pdf_loading.html"


    @patch('vin_decoder.views.generate_pdf_task.delay')
    def test_partial_pdfloadig_renders_correctly(self , mock_delay ,database_mock_user ,client: Client)-> None:

        client.force_login(database_mock_user)
        mock_delay.return_value.id= "fake-task-id"

        url = reverse(self.url_name)

        response = client.post(
            url,
            data ={
                "action": "save_pdf",
                "vin": "WBA5U9C00LFJ37061",
                "car_description": "Some car description",
                }
            )

        assert response.status_code == 200
        assert self.partial_template_name in [t.name for t  in response.templates]
        mock_delay.assert_called_once_with("WBA5U9C00LFJ37061" , "Some car description")


    @patch('vin_decoder.views.generate_pdf_task.delay')
    def test_get_vin_and_task_id_success(self, mock_delay, database_mock_user  ,client: Client)-> None:

        client.force_login(database_mock_user)
        mock_delay.return_value.id= 'fake_success-id'

        url= reverse(self.url_name)

        response = client.post(
            url,
            data={
                "action": "save_pdf",
                "vin": "1G1FG1R77J0170121",
                "car_description": "Some car description v2",
            })

        assert response.context["task_id"] == 'fake_success-id'
        mock_delay.assert_called_once_with("1G1FG1R77J0170121" , "Some car description v2")


    def test_incorrect_vin_number_redirect_home(self,  database_mock_user  ,client: Client)-> None:

        client.force_login(database_mock_user)
        url= reverse(self.url_name)
        
        response = client.post(
            url,
            data={
                "action": "save_pdf",
                "vin": ""
            })

        assert response.status_code == 302
        assert response.url == reverse('vin_decoder:home')


    def test_no_action_button_redirect_home(self,  database_mock_user  ,client: Client)-> None:

        client.force_login(database_mock_user)
        url= reverse(self.url_name)

        response = client.post(
            url,
            data={
                'action':"",
                'vin':'1G1FG1R77J0170121'
            }
        )

        assert response.status_code == 302
        assert response.url == reverse('vin_decoder:home')


    @patch('vin_decoder.views.generate_pdf_task.delay', side_effect= Exception("boom xd") )
    def test_save_pdf_action_returns_500_on_task_error(self, mock_delay, database_mock_user  ,client: Client)-> None:

        client.force_login(database_mock_user)
        url = reverse(self.url_name)

        response = client.post(
            url,
            data = {
                'action':"save_pdf",
                'vin':'1G1FG1R77J0170121',
                "car_description": "Some car description v3",
            }
        )

        assert response.status_code == 500
        assert response.content == b"Error during generating pdf."
        mock_delay.assert_called_once_with("1G1FG1R77J0170121", "Some car description v3")



class Test_openai_common_car_issues:
    """ test openai_common_car_issues view login is requied for all tests """

    pytestmark = pytest.mark.django_db
    template_name = 'partials/gpt_typical_issues_car.html'
    url_name = 'vin_decoder:get_car_issues'


    @patch('django_ratelimit.decorators.is_ratelimited', return_value= True)
    def test_hit_rate_limit_error(self, mock_is_ratelimited, database_mock_user, client : Client)-> None:

        client.force_login(database_mock_user)


        url = reverse(self.url_name)

        response = client.post(
            url,
            data={}
        )

        assert response.status_code == 200
        assert self.template_name in [t.name for t in response.templates]
        assert response.context['message_error'] == "You have reached refresh limit, Pleas wait 1 min to try agian."


    @pytest.mark.parametrize("post_data", [
    {'car_description': 'test car description'},
    {'action': 'submit'},
    ])
    def test_invalid_action_return_error(self, database_mock_user, client : Client, post_data)-> None:
        """Tests two cases when action is missing and when car description is missing"""

        client.force_login(database_mock_user)

        url= reverse(self.url_name)

        response = client.post(
            url , data=post_data
        )

        assert response.status_code == 200
        assert response.context['message_error'] == 'Invalid action'
        assert self.template_name in [t.name for t in response.templates]


    @patch('vin_decoder.views.openai_prompt_basic')
    def test_data_isvalid_generating_AI_reponse_success(self, open_AI_prompt_mock_func,  database_mock_user, client: Client )-> None:

        client.force_login(database_mock_user)
        url= reverse(self.url_name)

        open_AI_prompt_mock_func.return_value = ("Check your brake pads regularly.", None)

        response = client.post(
            url,
            data={
                'action': 'submit',
                'car_description': 'test car description',
                'vin':'1G1FG1R77J0170121'
            }
        )


        assert response.status_code == 200
        assert response.context['vin'] == '1G1FG1R77J0170121'
        assert self.template_name in [t.name for t in response.templates]
        open_AI_prompt_mock_func.assert_called_once_with('test car description')
        assert 'Check your brake pads regularly.' in response.context['results_html']



class Test_check_task_status:
    """ test check_task_status view login is requied for all tests """

    pytestmark= pytest.mark.django_db
    url_name='vin_decoder:check_task_status'
    template_name_loading='partials/pdf_loading.html'
    template_name_download="partials/pdf_download.html"
    template_name_failed="partials/pdf_download_failed.html"


    #Decorators are going from bottom to up order
    @patch('vin_decoder.views.AsyncResult')
    def test_template_render_status_download_not_ready(self, mock_async_result_cls, database_mock_user, client :Client)-> None:

        mock_async_result_cls.return_value.ready.return_value = False
        mock_async_result_cls.return_value.status = 'PENDING'

        client.force_login(database_mock_user)

        url= reverse(self.url_name, kwargs={'task_id': 'fake-task-id'})

        response = client.get(url)

        assert response.status_code == 200
        assert self.template_name_loading in [t.name for t in response.templates]
        assert response.context['status'] == 'PENDING'


    @patch('vin_decoder.views.AsyncResult')
    def test_status_success_get_download_url(self, mock_async_result_cls, database_mock_user, client : Client)-> None:

        mock_async_result_cls.return_value.ready.return_value = True
        mock_async_result_cls.return_value.status = 'SUCCESS'
        mock_async_result_cls.return_value.result = 'test-download-url'

        client.force_login(database_mock_user)

        url = reverse(self.url_name, kwargs= {'task_id': 'fake-task-id-download'})

        response = client.get(url)

        assert response.status_code == 200
        assert self.template_name_download in [t.name for t in response.templates]
        assert self.template_name_failed not in [t.name for t in response.templates]
        assert response.context['download_url'] == 'test-download-url'
        mock_async_result_cls.assert_called_once_with('fake-task-id-download')


    @patch('vin_decoder.views.AsyncResult')
    def test_status_failed_get_error(self,  mock_async_result_cls, database_mock_user, client: Client)-> None:

        mock_async_result_cls.return_value.ready.return_value = True
        mock_async_result_cls.return_value.status = 'FAILURE'
        mock_async_result_cls.return_value.info = 'Error occurred during generating download url'

        client.force_login(database_mock_user)

        url= reverse(self.url_name, kwargs= {'task_id': 'fake-task-id-download'})

        response = client.get(url)

        assert response.status_code == 200
        assert self.template_name_failed in [t.name for t in response.templates]
        assert self.template_name_download not in [t.name for t in response.templates]
        assert response.context['failed_info'] == 'Error occurred during generating download url'


    def test_anonymous_user_redirected_to_login(self, client: Client)-> None:

        url= reverse(self.url_name , kwargs= {'task_id': 'fake-task-id-download'})

        resposne = client.get(url)

        assert resposne.status_code == 302
        assert '/login' in resposne.url
