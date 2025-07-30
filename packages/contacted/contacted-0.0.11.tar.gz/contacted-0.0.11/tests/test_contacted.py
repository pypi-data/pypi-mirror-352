"""
Tests for Contacted Python SDK
"""

import pytest
from unittest.mock import Mock, patch
from contacted import ContactedAI
from contacted.validation import (
    validate_send_options,
    validate_prompt,
    validate_data,
    validate_emails,
    validate_subject,
    is_valid_email
)


class TestEmailValidation:
    """Test email validation functions"""

    def test_should_validate_correct_email_formats(self):
        """Test valid email formats"""
        assert is_valid_email('test@example.com') == True
        assert is_valid_email('user.name@domain.co.uk') == True
        assert is_valid_email('test+label@example.org') == True
        assert is_valid_email('user123@test-domain.com') == True
        assert is_valid_email('valid.email@example123.co') == True

    def test_should_reject_invalid_email_formats(self):
        """Test invalid email formats"""
        assert is_valid_email('invalid-email') == False
        assert is_valid_email('test@') == False
        assert is_valid_email('@example.com') == False
        assert is_valid_email('test..test@example.com') == False  # consecutive dots
        assert is_valid_email('test@example') == False  # no TLD
        assert is_valid_email('.test@example.com') == False  # leading dot
        assert is_valid_email('test.@example.com') == False  # trailing dot
        assert is_valid_email('test@.example.com') == False  # dot after @
        assert is_valid_email('test@example.com.') == False  # trailing dot
        assert is_valid_email('') == False  # empty string
        assert is_valid_email('test @example.com') == False  # space in email

    def test_should_validate_required_email_fields(self):
        """Test required email validation"""
        with pytest.raises(ValueError, match='Both "from" and "to" email addresses are required'):
            validate_emails('', 'test@example.com')

        with pytest.raises(ValueError, match='Both "from" and "to" email addresses are required'):
            validate_emails('test@example.com', '')

    def test_should_validate_email_format_in_validate_emails(self):
        """Test email format validation in validate_emails function"""
        with pytest.raises(ValueError, match='Invalid "from" email address format'):
            validate_emails('invalid-email', 'test@example.com')

        with pytest.raises(ValueError, match='Invalid "to" email address format'):
            validate_emails('test@example.com', 'invalid-email')


class TestSubjectValidation:
    """Test subject validation functions"""

    def test_should_validate_subject_is_required(self):
        """Test subject is required"""
        with pytest.raises(ValueError, match='Subject is required'):
            validate_subject(None)

    def test_should_validate_subject_is_string(self):
        """Test subject must be string"""
        with pytest.raises(ValueError, match='Subject must be a string'):
            validate_subject(123)

        with pytest.raises(ValueError, match='Subject must be a string'):
            validate_subject({})

        with pytest.raises(ValueError, match='Subject must be a string'):
            validate_subject([])

        with pytest.raises(ValueError, match='Subject must be a string'):
            validate_subject(True)

    def test_should_validate_subject_length(self):
        """Test subject length validation"""
        with pytest.raises(ValueError, match='Subject must be at least 2 characters long'):
            validate_subject('a')

        with pytest.raises(ValueError, match='Subject must be at least 2 characters long'):
            validate_subject('')

        long_subject = 'a' * 257
        with pytest.raises(ValueError, match='Subject must be no more than 256 characters long'):
            validate_subject(long_subject)

    def test_should_accept_valid_subjects(self):
        """Test valid subjects are accepted"""
        # These should not raise any exception
        validate_subject('Hi')
        validate_subject('Hello there')
        validate_subject('Meeting Tomorrow')

        # Test exactly at boundaries
        validate_subject('ab')  # exactly 2 chars
        validate_subject('a' * 256)  # exactly 256 chars


class TestPromptValidation:
    """Test prompt validation functions"""

    def test_should_validate_prompt_is_required(self):
        """Test prompt is required"""
        with pytest.raises(ValueError, match='Prompt is required'):
            validate_prompt(None)

    def test_should_validate_prompt_is_string(self):
        """Test prompt must be string"""
        with pytest.raises(ValueError, match='Prompt must be a string'):
            validate_prompt(123)

        with pytest.raises(ValueError, match='Prompt must be a string'):
            validate_prompt({})

    def test_should_validate_prompt_length(self):
        """Test prompt length validation"""
        with pytest.raises(ValueError, match='Prompt must be at least 10 characters long'):
            validate_prompt('short')

        long_prompt = 'a' * 251
        with pytest.raises(ValueError, match='Prompt must be no more than 250 characters long'):
            validate_prompt(long_prompt)

    def test_should_accept_valid_prompts(self):
        """Test valid prompts are accepted"""
        # This should not raise any exception
        validate_prompt('This is a valid prompt with enough characters')


class TestDataValidation:
    """Test data validation functions"""

    def test_should_allow_optional_data(self):
        """Test data is optional"""
        # These should not raise exceptions
        validate_data(None)

    def test_should_validate_data_is_dict(self):
        """Test data must be dictionary"""
        with pytest.raises(ValueError, match='Data must be an object'):
            validate_data('string')

        with pytest.raises(ValueError, match='Data must be an object'):
            validate_data([])

        with pytest.raises(ValueError, match='Data must be an object'):
            validate_data(123)

    def test_should_validate_data_keys_are_strings(self):
        """Test data keys must be strings"""
        with pytest.raises(ValueError, match='All data keys must be non-empty strings'):
            validate_data({'': 'value'})

        with pytest.raises(ValueError, match='All data keys must be non-empty strings'):
            validate_data({'   ': 'value'})

    def test_should_validate_data_keys_have_no_spaces(self):
        """Test data keys cannot have spaces"""
        with pytest.raises(ValueError, match='Data keys cannot contain spaces'):
            validate_data({'key with space': 'value'})

        with pytest.raises(ValueError, match='Data keys cannot contain spaces'):
            validate_data({'key\twith\ttab': 'value'})

    def test_should_accept_valid_data_objects(self):
        """Test valid data objects are accepted"""
        # This should not raise any exception
        validate_data({
            'name': 'John Doe',
            'age': 30,
            'active': True,
            'link': 'https://example.com'
        })


class TestCompleteSendOptionsValidation:
    """Test complete send options validation"""

    def setUp(self):
        self.valid_options = {
            'from': 'sender@example.com',
            'to': 'receiver@example.com',
            'subject': 'Meeting Tomorrow',
            'prompt': 'This is a valid prompt with enough characters',
            'data': {
                'name': 'John',
                'link': 'https://example.com'
            }
        }

    def test_should_validate_complete_valid_options(self):
        """Test complete valid options"""
        valid_options = {
            'from': 'sender@example.com',
            'to': 'receiver@example.com',
            'subject': 'Meeting Tomorrow',
            'prompt': 'This is a valid prompt with enough characters',
            'data': {
                'name': 'John',
                'link': 'https://example.com'
            }
        }
        # This should not raise any exception
        validate_send_options(valid_options)

    def test_should_fail_on_missing_subject(self):
        """Test missing subject validation"""
        options = {
            'from': 'sender@example.com',
            'to': 'receiver@example.com',
            'prompt': 'This is a valid prompt with enough characters'
        }
        with pytest.raises(ValueError, match='Subject is required'):
            validate_send_options(options)

    def test_should_fail_on_invalid_subject_type(self):
        """Test invalid subject type validation"""
        options = {
            'from': 'sender@example.com',
            'to': 'receiver@example.com',
            'subject': 123,
            'prompt': 'This is a valid prompt with enough characters'
        }
        with pytest.raises(ValueError, match='Subject must be a string'):
            validate_send_options(options)

    def test_should_fail_on_subject_too_short(self):
        """Test subject too short validation"""
        options = {
            'from': 'sender@example.com',
            'to': 'receiver@example.com',
            'subject': 'a',
            'prompt': 'This is a valid prompt with enough characters'
        }
        with pytest.raises(ValueError, match='Subject must be at least 2 characters long'):
            validate_send_options(options)

    def test_should_fail_on_subject_too_long(self):
        """Test subject too long validation"""
        options = {
            'from': 'sender@example.com',
            'to': 'receiver@example.com',
            'subject': 'a' * 257,
            'prompt': 'This is a valid prompt with enough characters'
        }
        with pytest.raises(ValueError, match='Subject must be no more than 256 characters long'):
            validate_send_options(options)

    def test_should_fail_on_invalid_email(self):
        """Test invalid email validation"""
        options = {
            'from': 'invalid-email',
            'to': 'receiver@example.com',
            'subject': 'Meeting Tomorrow',
            'prompt': 'This is a valid prompt with enough characters'
        }
        with pytest.raises(ValueError, match='Invalid "from" email address format'):
            validate_send_options(options)

    def test_should_fail_on_invalid_prompt(self):
        """Test invalid prompt validation"""
        options = {
            'from': 'sender@example.com',
            'to': 'receiver@example.com',
            'subject': 'Meeting Tomorrow',
            'prompt': 'short'
        }
        with pytest.raises(ValueError, match='Prompt must be at least 10 characters long'):
            validate_send_options(options)

    def test_should_fail_on_invalid_data(self):
        """Test invalid data validation"""
        options = {
            'from': 'sender@example.com',
            'to': 'receiver@example.com',
            'subject': 'Meeting Tomorrow',
            'prompt': 'This is a valid prompt with enough characters',
            'data': {'key with space': 'value'}
        }
        with pytest.raises(ValueError, match='Data keys cannot contain spaces'):
            validate_send_options(options)

    def test_should_work_without_data_field(self):
        """Test options work without data field"""
        options = {
            'from': 'sender@example.com',
            'to': 'receiver@example.com',
            'subject': 'Meeting Tomorrow',
            'prompt': 'This is a valid prompt with enough characters'
        }
        # This should not raise any exception
        validate_send_options(options)

    def test_should_accept_minimum_valid_subject(self):
        """Test minimum valid subject"""
        options = {
            'from': 'sender@example.com',
            'to': 'receiver@example.com',
            'subject': 'Hi',
            'prompt': 'This is a valid prompt with enough characters'
        }
        # This should not raise any exception
        validate_send_options(options)

    def test_should_accept_maximum_valid_subject(self):
        """Test maximum valid subject"""
        options = {
            'from': 'sender@example.com',
            'to': 'receiver@example.com',
            'subject': 'a' * 256,
            'prompt': 'This is a valid prompt with enough characters'
        }
        # This should not raise any exception
        validate_send_options(options)


class TestContactedAIClient:
    """Test ContactedAI client class"""

    def test_should_initialize_with_api_key(self):
        """Test client initialization"""
        client = ContactedAI(api_key='test-api-key')
        assert client.api_key == 'test-api-key'

    def test_should_throw_error_without_api_key(self):
        """Test client requires API key"""
        with pytest.raises(ValueError, match='API key is required'):
            ContactedAI(api_key='')

        with pytest.raises(ValueError, match='API key is required'):
            ContactedAI(api_key=None)

    def test_should_initialize_with_custom_settings(self):
        """Test client initialization with custom settings"""
        client = ContactedAI(
            api_key='test-key',
            base_url='https://custom-api.contacted.io',
            timeout=60
        )
        assert client.api_key == 'test-key'
        assert client.base_url == 'https://custom-api.contacted.io'
        assert client.timeout == 60


class TestContactedAISendMethod:
    """Test ContactedAI send method with new keyword interface"""

    def setup_method(self):
        """Set up test client"""
        self.client = ContactedAI(api_key='test-api-key')

    def test_should_validate_parameters_before_api_call(self):
        """Test that validation happens before API call"""
        # Test invalid email validation
        with pytest.raises(ValueError, match='Invalid "from" email address format'):
            self.client.send(
                subject='Test Subject',
                from_email='invalid-email',
                to_email='valid@example.com',
                prompt='This is a valid prompt with enough characters'
            )

        # Test short prompt validation
        with pytest.raises(ValueError, match='Prompt must be at least 10 characters long'):
            self.client.send(
                subject='Test Subject',
                from_email='sender@example.com',
                to_email='receiver@example.com',
                prompt='short'
            )

        # Test subject validation
        with pytest.raises(ValueError, match='Subject must be at least 2 characters long'):
            self.client.send(
                subject='a',
                from_email='sender@example.com',
                to_email='receiver@example.com',
                prompt='This is a valid prompt with enough characters'
            )

        # Test data validation
        with pytest.raises(ValueError, match='Data keys cannot contain spaces'):
            self.client.send(
                subject='Test Subject',
                from_email='sender@example.com',
                to_email='receiver@example.com',
                prompt='This is a valid prompt with enough characters',
                data={'key with space': 'value'}
            )

    @patch('contacted.ContactedAI.session')
    def test_should_send_with_required_parameters_only(self, mock_session):
        """Test sending with only required parameters"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 'test-id', 'status': 'queued'}
        mock_session.post.return_value = mock_response

        result = self.client.send(
            subject='Test Subject',
            from_email='sender@example.com',
            to_email='receiver@example.com',
            prompt='This is a valid prompt with enough characters'
        )

        # Verify the API was called with correct payload
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args

        # Check URL
        assert call_args[0][0].endswith('/send')

        # Check payload
        payload = call_args[1]['json']
        assert payload['subject'] == 'Test Subject'
        assert payload['from'] == 'sender@example.com'
        assert payload['to'] == 'receiver@example.com'
        assert payload['prompt'] == 'This is a valid prompt with enough characters'
        assert payload['data'] == {}

        # Check result
        assert result['id'] == 'test-id'
        assert result['status'] == 'queued'

    @patch('contacted.ContactedAI.session')
    def test_should_send_with_all_parameters(self, mock_session):
        """Test sending with all parameters including optional ones"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 'test-id', 'status': 'queued'}
        mock_session.post.return_value = mock_response

        result = self.client.send(
            subject='Test Subject',
            from_email='sender@example.com',
            to_email='receiver@example.com',
            prompt='This is a valid prompt with enough characters',
            data={
                'name': 'John Doe',
                'link': 'https://example.com'
            },
            sending_profile='test-profile-id'
        )

        # Verify the API was called with correct payload
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args

        payload = call_args[1]['json']
        assert payload['subject'] == 'Test Subject'
        assert payload['from'] == 'sender@example.com'
        assert payload['to'] == 'receiver@example.com'
        assert payload['prompt'] == 'This is a valid prompt with enough characters'
        assert payload['data'] == {'name': 'John Doe', 'link': 'https://example.com'}
        assert payload['sendingProfile'] == 'test-profile-id'

        assert result['id'] == 'test-id'

    @patch('contacted.ContactedAI.session')
    def test_should_handle_api_errors(self, mock_session):
        """Test handling of API errors"""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'message': 'Invalid request'}
        mock_response.content = True
        mock_session.post.return_value = mock_response

        with pytest.raises(ValueError, match='ContactedAI API Error: Invalid request'):
            self.client.send(
                subject='Test Subject',
                from_email='sender@example.com',
                to_email='receiver@example.com',
                prompt='This is a valid prompt with enough characters'
            )

    def test_should_accept_valid_parameter_combinations(self):
        """Test various valid parameter combinations"""
        # These should not raise validation errors (we're not testing API calls)
        test_cases = [
            {
                'subject': 'Hi',  # minimum length
                'from_email': 'a@b.co',
                'to_email': 'c@d.co',
                'prompt': 'a' * 10  # minimum length
            },
            {
                'subject': 'a' * 256,  # maximum length
                'from_email': 'test@example.com',
                'to_email': 'user@domain.org',
                'prompt': 'a' * 250,  # maximum length
                'data': {'key': 'value'}
            },
            {
                'subject': 'Normal Subject',
                'from_email': 'user.name+tag@example-domain.co.uk',
                'to_email': 'test123@subdomain.example.org',
                'prompt': 'Generate a personalized welcome email',
                'data': {
                    'name': 'John Doe',
                    'age': 30,
                    'active': True,
                    'items': ['a', 'b', 'c'],
                    'nested': {'key': 'value'}
                },
                'sending_profile': 'profile-123'
            }
        ]

        for case in test_cases:
            try:
                # Create temporary client for validation testing
                client = ContactedAI(api_key='test-key')

                # Test that validation passes (this will fail at network call, which is expected)
                with patch.object(client, 'session') as mock_session:
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {'id': 'test'}
                    mock_session.post.return_value = mock_response

                    client.send(**case)

            except ValueError as e:
                # If we get a validation error, the test should fail
                pytest.fail(f"Validation failed for valid case {case}: {e}")


class TestContactedAIMessageStatus:
    """Test ContactedAI get_message_status method"""

    def setup_method(self):
        """Set up test client"""
        self.client = ContactedAI(api_key='test-api-key')

    def test_should_validate_message_id_parameter(self):
        """Test message ID validation"""
        with pytest.raises(ValueError, match='Message ID is required'):
            self.client.get_message_status('')

        with pytest.raises(ValueError, match='Message ID is required'):
            self.client.get_message_status(None)

        with pytest.raises(ValueError, match='Message ID must be a string'):
            self.client.get_message_status(123)

    @patch('contacted.ContactedAI.session')
    def test_should_get_message_status_successfully(self, mock_session):
        """Test successful message status retrieval"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'test-message-id',
            'status': 'sent',
            'message': 'Message delivered successfully'
        }
        mock_session.get.return_value = mock_response

        result = self.client.get_message_status('test-message-id')

        # Verify the API was called correctly
        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args

        # Check URL and params
        assert call_args[0][0].endswith('/message')
        assert call_args[1]['params'] == {'id': 'test-message-id'}

        # Check result
        assert result['id'] == 'test-message-id'
        assert result['status'] == 'sent'