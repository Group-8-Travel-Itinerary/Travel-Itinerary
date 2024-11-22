import unittest
from unittest.mock import patch, Mock
from integrations import get_freebase_id, send_quiz_to_gpt, get_custom_quiz, load_gpt_instructions, flights_api, weather_api, pexels_images, get_activities, concat_preferences_for_activities, text_search_activities, get_activity_details, get_photo_url, form_itinerary_prompt, get_itinerary

class TestIntegrations(unittest.TestCase):

    @patch('integrations.requests.get')
    def test_get_freebase_id(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            'search': [{'id': 'Q60'}],
            'entities': {'Q60': {'claims': {'P646': [{'mainsnak': {'datavalue': {'value': '/m/02_286'}}}]}}}
        }
        mock_get.return_value = mock_response

        result = get_freebase_id('New York')
        self.assertEqual(result, '/m/02_286')

    @patch('integrations.requests.post')
    def test_send_quiz_to_gpt(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Test response'}}]
        }
        mock_post.return_value = mock_response

        result = send_quiz_to_gpt('Test message')
        self.assertEqual(result, 'Test response')

    def test_get_custom_quiz(self):
        result = get_custom_quiz('Test prompt')
        self.assertIsNotNone(result)

    def test_load_gpt_instructions(self):
        result = load_gpt_instructions('test_instructions.txt')
        self.assertIsNotNone(result)

    @patch('integrations.requests.get')
    def test_flights_api(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'data': 'Test flight data'}
        mock_get.return_value = mock_response

        result = flights_api('NYC', ['LAX'], '2023-01-01', '2023-01-10')
        self.assertEqual(result, 'Test flight data')

    @patch('integrations.requests.get')
    def test_weather_api(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'data': 'Test weather data'}
        mock_get.return_value = mock_response

        result = weather_api(['NYC'])
        self.assertEqual(result, 'Test weather data')

    @patch('integrations.requests.get')
    def test_pexels_images(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'photos': ['Test photo']}
        mock_get.return_value = mock_response

        result = pexels_images('Nature')
        self.assertEqual(result, ['Test photo'])

    def test_get_activities(self):
        result = get_activities('NYC', 'Outdoor')
        self.assertIsNotNone(result)

    def test_concat_preferences_for_activities(self):
        result = concat_preferences_for_activities()
        self.assertIsNotNone(result)

    @patch('integrations.requests.get')
    def test_text_search_activities(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'results': ['Test activity']}
        mock_get.return_value = mock_response

        result = text_search_activities('Hiking', 'fake_api_key')
        self.assertEqual(result, ['Test activity'])

    @patch('integrations.requests.get')
    def test_get_activity_details(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'result': 'Test activity details'}
        mock_get.return_value = mock_response

        result = get_activity_details('place_id', 'fake_api_key')
        self.assertEqual(result, 'Test activity details')

    def test_get_photo_url(self):
        result = get_photo_url('photo_reference', 'fake_api_key')
        self.assertIsNotNone(result)

    def test_form_itinerary_prompt(self):
        result = form_itinerary_prompt('NYC', 'Answers', 'Instructions', 'Activities')
        self.assertIsNotNone(result)

    def test_get_itinerary(self):
        result = get_itinerary('Test prompt')
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()