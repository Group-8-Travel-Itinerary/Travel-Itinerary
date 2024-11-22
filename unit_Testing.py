import unittest
from unittest.mock import patch, Mock
from integrations import get_freebase_id, send_quiz_to_gpt, get_custom_quiz, load_gpt_instructions, flights_api, weather_api, pexels_images, get_user_location, get_activities, concat_preferences_for_activities, text_search_activities, get_activity_details, get_photo_url, form_itinerary_prompt, get_itinerary

# FILE: test_unit_Testing.py


class TestIntegrations(unittest.TestCase):

    @patch('integrations.requests.get')
    def test_get_freebase_id(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            'search': [{'id': 'Q60', 'label': 'New York City'}]
        }
        mock_get.return_value = mock_response

        result = get_freebase_id('New York City')
        self.assertEqual(result, 'Q60')

    @patch('integrations.openai.Completion.create')
    def test_send_quiz_to_gpt(self, mock_create):
        mock_create.return_value = {'choices': [{'text': 'response'}]}
        result = send_quiz_to_gpt('message')
        self.assertEqual(result, 'response')

    def test_get_custom_quiz(self):
        result = get_custom_quiz('prompt')
        self.assertIsNotNone(result)

    def test_load_gpt_instructions(self):
        result = load_gpt_instructions('path/to/file')
        self.assertIsNotNone(result)

    @patch('integrations.requests.get')
    def test_flights_api(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'data': 'flight_data'}
        mock_get.return_value = mock_response

        result = flights_api('city1', 'city2', '2023-01-01', '2023-01-10')
        self.assertEqual(result, 'flight_data')

    @patch('integrations.requests.get')
    def test_weather_api(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'weather': 'sunny'}
        mock_get.return_value = mock_response

        result = weather_api(['city1', 'city2'])
        self.assertEqual(result, 'sunny')

    @patch('integrations.requests.get')
    def test_pexels_images(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'photos': ['photo1', 'photo2']}
        mock_get.return_value = mock_response

        result = pexels_images('query')
        self.assertEqual(result, ['photo1', 'photo2'])

    @patch('integrations.requests.get')
    def test_get_user_location(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'location': 'user_location'}
        mock_get.return_value = mock_response

        result = get_user_location()
        self.assertEqual(result, 'user_location')

    @patch('integrations.requests.get')
    def test_get_activities(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'activities': ['activity1', 'activity2']}
        mock_get.return_value = mock_response

        result = get_activities('destination', 'preferences')
        self.assertEqual(result, ['activity1', 'activity2'])

    def test_concat_preferences_for_activities(self):
        result = concat_preferences_for_activities()
        self.assertIsNotNone(result)

    @patch('integrations.requests.get')
    def test_text_search_activities(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'results': ['activity1', 'activity2']}
        mock_get.return_value = mock_response

        result = text_search_activities('query', 'api_key')
        self.assertEqual(result, ['activity1', 'activity2'])

    @patch('integrations.requests.get')
    def test_get_activity_details(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'details': 'activity_details'}
        mock_get.return_value = mock_response

        result = get_activity_details('place_id', 'api_key')
        self.assertEqual(result, 'activity_details')

    @patch('integrations.requests.get')
    def test_get_photo_url(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'url': 'photo_url'}
        mock_get.return_value = mock_response

        result = get_photo_url('photo_reference', 'api_key')
        self.assertEqual(result, 'photo_url')

    def test_form_itinerary_prompt(self):
        result = form_itinerary_prompt('destination', 'formatted_answers', 'quiz_instructions', 'itinerary_activities')
        self.assertIsNotNone(result)

    def test_get_itinerary(self):
        result = get_itinerary('prompt')
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()