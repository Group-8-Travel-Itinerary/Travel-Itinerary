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
            "choices": [
                {
                    "text": "Summary: Adventurous traveler\nDestination 1:\nName: Bali\nDescription: Beautiful island\nActivities: Surfing|Hiking|Diving|Yoga|Snorkeling|Relaxing\nAccommodation: Hotel A|Hotel B|Hotel C\nTips: Tip 1|Tip 2\nDestination 2:\nName: Paris\nDescription: City of love\nActivities: Sightseeing|Museum visits|Shopping|Dining|Walking tours|Relaxing\nAccommodation: Hotel D|Hotel E|Hotel F\nTips: Tip 3|Tip 4\nDestination 3:\nName: Tokyo\nDescription: Modern city\nActivities: Shopping|Dining|Sightseeing|Cultural tours|Nightlife|Relaxing\nAccommodation: Hotel G|Hotel H|Hotel I\nTips: Tip 5|Tip 6"
                }
            ]
        }
        mock_post.return_value = mock_response

        with patch('integrations.session', {'initial_prompt': 'Initial prompt'}):
            result = send_quiz_to_gpt('I love adventure')
            expected_result = "Summary: Adventurous traveler\nDestination 1:\nName: Bali\nDescription: Beautiful island\nActivities: Surfing|Hiking|Diving|Yoga|Snorkeling|Relaxing\nAccommodation: Hotel A|Hotel B|Hotel C\nTips: Tip 1|Tip 2\nDestination 2:\nName: Paris\nDescription: City of love\nActivities: Sightseeing|Museum visits|Shopping|Dining|Walking tours|Relaxing\nAccommodation: Hotel D|Hotel E|Hotel F\nTips: Tip 3|Tip 4\nDestination 3:\nName: Tokyo\nDescription: Modern city\nActivities: Shopping|Dining|Sightseeing|Cultural tours|Nightlife|Relaxing\nAccommodation: Hotel G|Hotel H|Hotel I\nTips: Tip 5|Tip 6"
            self.assertEqual(result, expected_result)

    @patch('integrations.requests.get')
    def test_pexels_images(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "photos": [
                {"src": {"medium": "http://example.com/photo1.jpg"}},
                {"src": {"medium": "http://example.com/photo2.jpg"}}
            ]
        }
        mock_get.return_value = mock_response

        result = pexels_images('Nature', 2)
        expected_result = ["http://example.com/photo1.jpg", "http://example.com/photo2.jpg"]
        self.assertEqual(result, expected_result)

    def test_get_custom_quiz(self):
        result = get_custom_quiz('Test prompt')
        self.assertIsNotNone(result)

    def test_load_gpt_instructions(self):
        with patch('builtins.open', unittest.mock.mock_open(read_data="Test instructions")):
            result = load_gpt_instructions('test_instructions.txt')
            self.assertEqual(result, "Test instructions")

    def test_get_activities(self):
        result = get_activities('NYC', 'Outdoor')
        self.assertIsNotNone(result)

    @patch('integrations.session', {'initial_prompt': 'Initial prompt', 'custom_quiz': 'Custom quiz', 'formatted_answers': 'Formatted answers', 'summary': 'Summary', 'destinations': 'Destinations', 'destination': 'Destination'})
    def test_concat_preferences_for_activities(self):
        result = concat_preferences_for_activities()
        expected_prompt = (
            "The user selected Destination as their destination. "
            "Here is the quiz they were given: Custom quiz. "
            "Their answers to the quiz: Formatted answers. "
            "Summary of preferences: Summary. "
            "Here were the output suggestions for the destination. Use the provided destination to find activities that match Destinations. "
            "Based on this, suggest activities that align with these preferences. "
            "Please format the activities in JSON format, with each activity containing a 'name', 'type', and 'description'."
        )
        self.assertEqual(result, expected_prompt)

    @patch('integrations.requests.get')
    def test_text_search_activities(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'results': ['Test activity']}
        mock_get.return_value = mock_response

        result = text_search_activities('query', 'api_key')
        self.assertEqual(result, {'results': ['Test activity']})

    @patch('integrations.requests.get')
    def test_get_activity_details(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'result': 'Test activity details'}
        mock_get.return_value = mock_response

        result = get_activity_details('place_id', 'api_key')
        self.assertEqual(result, {'result': 'Test activity details'})

    def test_get_photo_url(self):
        result = get_photo_url('photo_reference', 'fake_api_key')
        self.assertIsNotNone(result)

    def test_form_itinerary_prompt(self):
        formatted_answers = ["Answer 1", "Answer 2"]
        itinerary_activities = [
            {"name": "Activity 1", "type": "Type 1", "description": "Description 1"},
            {"name": "Activity 2", "type": "Type 2", "description": "Description 2"}
        ]
        result = form_itinerary_prompt('NYC', formatted_answers, 'Instructions', itinerary_activities)
        expected_prompt = (
            "You are planning a travel itinerary for the destination: NYC.\n\n"
            "Here are some quiz instructions for better customization:\nInstructions\n\n"
            "User preferences based on quiz:\n"
            "- Answer 1\n"
            "- Answer 2\n\n"
            "The selected activities for the itinerary include:\n"
            "\nActivity Name: Activity 1\n"
            "Type: Type 1\n"
            "Description: Description 1\n"
            "\nActivity Name: Activity 2\n"
            "Type: Type 2\n"
            "Description: Description 2\n"
        )
        self.assertEqual(result, expected_prompt)

    def test_get_itinerary(self):
        result = get_itinerary('Test prompt')
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()