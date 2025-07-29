from unittest.mock import patch, MagicMock

from django.test import RequestFactory
from django.http import Http404, HttpResponseForbidden
from django.contrib.auth.models import User
from django.urls import reverse

from esi.models import Token
from app_utils.testing import NoSocketsTestCase

from miningtaxes.models import Character, AdminCharacter
from miningtaxes.decorators import (
    fetch_user_if_allowed,
    fetch_character_if_allowed,
    fetch_token_for_character
)
from miningtaxes.tests.utils import (
    create_miningtaxes_character,
    create_miningtaxes_admincharacter,
    create_user_from_evecharacter_with_access,
    add_miningtaxes_character_to_user,
)


class TestFetchUserIfAllowed(NoSocketsTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        
        # Create user with basic access
        self.user = create_user_from_evecharacter_with_access(
            character_id=1001,
            character_name='Test Character',
            corporation_name='Test Corp',
            alliance_name='TEST',
            permission_name='miningtaxes.basic_access'
        )
        
        # Create another user
        self.other_user = create_user_from_evecharacter_with_access(
            character_id=1002,
            character_name='Other Character',
            corporation_name='Test Corp',
            alliance_name='TEST',
            permission_name='miningtaxes.basic_access'
        )
        
        # Create admin user
        self.admin_user = create_user_from_evecharacter_with_access(
            character_id=1003,
            character_name='Admin Character',
            corporation_name='Test Corp',
            alliance_name='TEST',
            permission_name='miningtaxes.admin_access'
        )
        
        # Test view function to wrap with decorator
        @fetch_user_if_allowed()
        def test_view(request, user_pk, *args, **kwargs):
            return {"user": user_pk}
        
        self.test_view = test_view

    def test_fetch_own_user(self):
        # User tries to access their own data - should succeed
        request = self.factory.get('/')
        request.user = self.user
        
        result = self.test_view(request, self.user.pk)
        
        # Should get access to their own user
        self.assertEqual(result["user"], self.user)

    def test_fetch_other_user_as_non_admin(self):
        # Non-admin user tries to access another user's data - should fail
        request = self.factory.get('/')
        request.user = self.user
        
        result = self.test_view(request, self.other_user.pk)
        
        # Should get forbidden response
        self.assertIsInstance(result, HttpResponseForbidden)

    def test_fetch_other_user_as_admin(self):
        # Admin user tries to access another user's data - should succeed
        request = self.factory.get('/')
        request.user = self.admin_user
        
        result = self.test_view(request, self.other_user.pk)
        
        # Should get access to the other user
        self.assertEqual(result["user"], self.other_user)

    def test_fetch_nonexistent_user(self):
        # User tries to access non-existent user - should 404
        request = self.factory.get('/')
        request.user = self.user
        
        with self.assertRaises(Http404):
            self.test_view(request, 999999)  # Non-existent user ID


class TestFetchCharacterIfAllowed(NoSocketsTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        
        # Create users
        self.user = create_user_from_evecharacter_with_access(
            character_id=1001,
            character_name='Test Character',
            corporation_name='Test Corp',
            alliance_name='TEST',
            permission_name='miningtaxes.basic_access'
        )
        
        self.other_user = create_user_from_evecharacter_with_access(
            character_id=1002,
            character_name='Other Character',
            corporation_name='Test Corp',
            alliance_name='TEST',
            permission_name='miningtaxes.basic_access'
        )
        
        self.admin_user = create_user_from_evecharacter_with_access(
            character_id=1003,
            character_name='Admin Character',
            corporation_name='Test Corp',
            alliance_name='TEST',
            permission_name='miningtaxes.admin_access'
        )
        
        # Create characters
        self.character = create_miningtaxes_character(
            character_id=1001,
            character_name='Test Character',
            corporation_id=2001,
            corporation_name='Test Corp'
        )
        add_miningtaxes_character_to_user(self.character, self.user)
        
        self.other_character = create_miningtaxes_character(
            character_id=1002,
            character_name='Other Character',
            corporation_id=2001,
            corporation_name='Test Corp'
        )
        add_miningtaxes_character_to_user(self.other_character, self.other_user)
        
        # Create admin character
        self.admin_character = create_miningtaxes_admincharacter(
            character_id=1003,
            character_name='Admin Character',
            corporation_id=2001,
            corporation_name='Test Corp'
        )
        add_miningtaxes_character_to_user(self.admin_character, self.admin_user)
        
        # Test view function to wrap with decorator
        @fetch_character_if_allowed()
        def test_view(request, character_id, *args, **kwargs):
            return {"character": character_id}
        
        self.test_view = test_view

    def test_fetch_own_character(self):
        # User tries to access their own character - should succeed
        request = self.factory.get('/')
        request.user = self.user
        
        result = self.test_view(request, self.character.pk)
        
        # Should get access to their own character
        self.assertEqual(result["character"], self.character)

    def test_fetch_other_character_as_non_admin(self):
        # Non-admin user tries to access another character - should fail
        request = self.factory.get('/')
        request.user = self.user
        
        result = self.test_view(request, self.other_character.pk)
        
        # Should get forbidden response
        self.assertIsInstance(result, HttpResponseForbidden)

    def test_fetch_other_character_as_admin(self):
        # Admin user tries to access another character - should succeed
        request = self.factory.get('/')
        request.user = self.admin_user
        
        result = self.test_view(request, self.other_character.pk)
        
        # Should get access to the other character
        self.assertEqual(result["character"], self.other_character)

    def test_fetch_nonexistent_character(self):
        # User tries to access non-existent character - should 404
        request = self.factory.get('/')
        request.user = self.user
        
        with self.assertRaises(Http404):
            self.test_view(request, 999999)  # Non-existent character ID


class TestFetchTokenForCharacter(NoSocketsTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        
        # Create user and character
        self.user = create_user_from_evecharacter_with_access(
            character_id=1001,
            character_name='Test Character',
            corporation_name='Test Corp',
            alliance_name='TEST',
            permission_name='miningtaxes.basic_access'
        )
        
        self.character = create_miningtaxes_character(
            character_id=1001,
            character_name='Test Character',
            corporation_id=2001,
            corporation_name='Test Corp'
        )
        add_miningtaxes_character_to_user(self.character, self.user)

        # Create mock token
        self.token = MagicMock(spec=Token)
        
        # Test view function to wrap with decorator
        @fetch_token_for_character()
        def test_view(request, token, *args, **kwargs):
            return {"token": token}
        
        self.test_view = test_view

    @patch('esi.models.Token.objects.filter')
    def test_fetch_token_for_character_success(self, mock_filter):
        # Setup mock token retrieval
        mock_filter.return_value.require_scopes.return_value.require_valid.return_value.first.return_value = self.token
            
        # Create request
        request = self.factory.get('/')
        request.user = self.user
            
        # Call view with character ID
        result = self.test_view(request, character_id=self.character.character_id)
            
        # Should get the token
        self.assertEqual(result["token"], self.token)
    
    @patch('esi.models.Token.objects.filter')
    def test_fetch_token_for_character_missing(self, mock_filter):
        # Setup mock token retrieval that returns None
        mock_filter.return_value.require_scopes.return_value.require_valid.return_value.first.return_value = None
            
        # Create request
        request = self.factory.get('/')
        request.user = self.user
            
        # Call view with character ID
        result = self.test_view(request, character_id=self.character.character_id)
            
        # Should be a forbidden response
        self.assertIsInstance(result, HttpResponseForbidden)
    
    @patch('esi.models.Token.objects.filter')
    def test_fetch_token_for_character_with_required_scopes(self, mock_filter):
        # Setup mock token retrieval
        mock_filter.return_value.require_scopes.return_value.require_valid.return_value.first.return_value = self.token
            
        # Create specific test view with required scopes
        @fetch_token_for_character(
            scopes=['esi-industry.read_character_mining.v1', 'esi-universe.read_structures.v1']
        )
        def test_view_with_scopes(request, token, *args, **kwargs):
            return {"token": token}
            
        # Create request
        request = self.factory.get('/')
        request.user = self.user
            
        # Call view with character ID
        result = test_view_with_scopes(request, character_id=self.character.character_id)
            
        # Should get the token
        self.assertEqual(result["token"], self.token)
            
        # Verify require_scopes was called with the correct scopes
        mock_filter.return_value.require_scopes.assert_called_once_with(
            'esi-industry.read_character_mining.v1',
            'esi-universe.read_structures.v1'
        )