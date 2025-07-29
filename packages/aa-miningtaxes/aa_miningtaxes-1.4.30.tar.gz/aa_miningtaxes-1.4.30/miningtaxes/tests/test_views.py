from unittest.mock import patch, MagicMock

from django.test import RequestFactory
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.http import JsonResponse

from app_utils.testing import NoSocketsTestCase
from allianceauth.eveonline.models import EveCharacter

from miningtaxes.models import Character, AdminCharacter, Stats
from miningtaxes.views import (
    launcher, index, user_summary, user_ledger, character_viewer,
    ore_prices, ore_prices_json, faq, add_character, remove_character,
    admin_launcher, admin_launcher_tax_table, admin_launcher_save_rates,
    admin_tables, admin_char_json, admin_main_json,
)
from miningtaxes.tests.utils import (
    create_miningtaxes_character,
    create_miningtaxes_admincharacter,
    create_user_from_evecharacter_with_access,
    add_miningtaxes_character_to_user,
    create_character_update_status,
    create_test_settings,
    create_test_general,
    create_test_ore_price,
)


class ViewsTestCase(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.token_patch = patch('esi.models.Token.objects.filter')
        cls.mock_token = cls.token_patch.start()
        mock_token_instance = MagicMock()
        cls.mock_token.return_value.require_scopes.return_value.require_valid.return_value.first.return_value = mock_token_instance

    @classmethod
    def tearDownClass(cls):
        cls.token_patch.stop()
        super().tearDownClass()

    def setUp(self):
        self.factory = RequestFactory()
        
        # Create users and permissions
        self.user = create_user_from_evecharacter_with_access(
            character_id=1001,
            character_name='Test Character',
            corporation_name='Test Corp',
            alliance_name='TEST',
            permission_name='miningtaxes.basic_access'
        )
        
        self.admin_user = create_user_from_evecharacter_with_access(
            character_id=1002,
            character_name='Admin Character',
            corporation_name='Test Corp',
            alliance_name='TEST',
            permission_name='miningtaxes.admin_access'
        )
        
        # Add admin permission
        content_type = ContentType.objects.get_for_model(Character)
        permission = Permission.objects.get(
            content_type=content_type,
            codename='admin_access'
        )
        self.admin_user.user_permissions.add(permission)
        
        # Create characters
        self.character = create_miningtaxes_character(
            character_id=1001,
            character_name='Test Character',
            corporation_id=2001,
            corporation_name='Test Corp'
        )
        add_miningtaxes_character_to_user(self.character, self.user)
        
        self.admin_character = create_miningtaxes_admincharacter(
            character_id=1002,
            character_name='Admin Character',
            corporation_id=2001,
            corporation_name='Test Corp'
        )
        add_miningtaxes_character_to_user(self.admin_character, self.admin_user)
        
        # Create update status
        create_character_update_status(self.character, is_success=True)
        create_character_update_status(self.admin_character, is_success=True)
        
        # Create settings
        self.settings = create_test_settings()
        
        # Create General entry
        self.general = create_test_general()
        
        # Create ore prices
        self.ore = create_test_ore_price()
        
        # Create stats
        self.stats = Stats.objects.create(
            admin_get_all_activity_json={},
            curmonth_leadergraph={},
            user_mining_ledger_90day={}
        )
        
        # Set up character mining data
        self.character.life_taxes = 1000000.0
        self.character.current_taxes = 500000.0
        self.character.taxes_paid = False
        self.character.monthly_mining_json = {
            str(timezone.now().year): {
                str(timezone.now().month): {
                    "45511": {"quantity": 1000, "value": 1000000.0, "tax": 100000.0}
                }
            }
        }
        self.character.save()

    def test_index_view(self):
        # Create request
        request = self.factory.get(reverse('miningtaxes:index'))
        request.user = self.user
        
        # Call view
        response = index(request)
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('miningtaxes:user_summary'))

    def test_launcher_view(self):
        # Create request
        request = self.factory.get(reverse('miningtaxes:launcher'))
        request.user = self.user
        
        # Call view
        response = launcher(request)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn('chars', response.context)
        self.assertEqual(len(response.context['chars']), 1)

    def test_user_summary_view(self):
        # Create request
        request = self.factory.get(reverse('miningtaxes:user_summary'))
        request.user = self.user
        
        # Call view
        response = user_summary(request)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn('user_obj', response.context)
        self.assertEqual(response.context['user_obj'], self.user)
        self.assertIn('chars', response.context)
        self.assertEqual(len(response.context['chars']), 1)

    def test_user_ledger_view(self):
        # Create request
        request = self.factory.get(reverse('miningtaxes:user_ledger'))
        request.user = self.user
        
        # Call view
        response = user_ledger(request)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn('user_obj', response.context)
        self.assertEqual(response.context['user_obj'], self.user)

    @patch('miningtaxes.views.fetch_character_if_allowed')
    def test_character_viewer_view(self, mock_fetch):
        # Set up mock
        mock_fetch.return_value = self.character
        
        # Create request
        request = self.factory.get(
            reverse('miningtaxes:character_viewer', kwargs={'character_id': self.character.pk})
        )
        request.user = self.user
        
        # Call view
        response = character_viewer(request, self.character.pk)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn('character', response.context)
        self.assertEqual(response.context['character'], self.character)

    def test_ore_prices_view(self):
        # Create request
        request = self.factory.get(reverse('miningtaxes:ore_prices'))
        request.user = self.user
        
        # Call view
        response = ore_prices(request)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
    def test_ore_prices_json_view(self):
        # Create request
        request = self.factory.get(reverse('miningtaxes:ore_prices_json'))
        request.user = self.user
        
        # Call view
        response = ore_prices_json(request)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        
        # Parse JSON response
        data = response.json()
        self.assertIn('data', data)
        self.assertEqual(len(data['data']), 1)  # One ore price entry

    def test_faq_view(self):
        # Create request
        request = self.factory.get(reverse('miningtaxes:faq'))
        request.user = self.user
        
        # Call view
        response = faq(request)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn('general', response.context)
        self.assertEqual(response.context['general'], self.general)

    @patch('miningtaxes.views.messages')
    @patch('miningtaxes.views.Character.objects.create')
    @patch('miningtaxes.views.EveCharacter.objects.get')
    def test_add_character_view(self, mock_get, mock_create, mock_messages):
        # Setup mocks
        mock_eve_char = MagicMock(spec=EveCharacter)
        mock_eve_char.character_id = 1003
        mock_eve_char.character_name = "New Character"
        mock_eve_char.corporation_id = 2001
        mock_eve_char.corporation_name = "Test Corp"
        mock_get.return_value = mock_eve_char
        
        mock_create.return_value = self.character
        
        # Create request
        request = self.factory.get(
            reverse('miningtaxes:add_character', kwargs={'character_id': 1003})
        )
        request.user = self.user
        
        # Mock messages
        request._messages = MagicMock()
        
        # Call view
        response = add_character(request, 1003)
        
        # Check response - should be a redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('miningtaxes:launcher'))
        
        # Verify character creation was called
        mock_create.assert_called_once()
        mock_messages.success.assert_called_once()

    @patch('miningtaxes.views.messages')
    @patch('miningtaxes.views.fetch_character_if_allowed')
    def test_remove_character_view(self, mock_fetch, mock_messages):
        # Setup mock
        mock_fetch.return_value = self.character
        
        # Create request
        request = self.factory.get(
            reverse('miningtaxes:remove_character', kwargs={'character_id': self.character.pk})
        )
        request.user = self.user
        
        # Mock messages
        request._messages = MagicMock()
        
        # Call view
        response = remove_character(request, self.character.pk)
        
        # Check response - should be a redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('miningtaxes:launcher'))
        
        # Verify character was deleted and message shown
        mock_messages.success.assert_called_once()

    def test_admin_launcher_view(self):
        # Create request
        request = self.factory.get(reverse('miningtaxes:admin_launcher'))
        request.user = self.admin_user
        
        # Call view
        response = admin_launcher(request)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn('settings', response.context)
        self.assertEqual(response.context['settings'], self.settings)
        self.assertIn('general', response.context)
        self.assertEqual(response.context['general'], self.general)

    def test_admin_launcher_view_for_non_admin(self):
        # Create request
        request = self.factory.get(reverse('miningtaxes:admin_launcher'))
        request.user = self.user  # Non-admin user
        
        # Call view
        response = admin_launcher(request)
        
        # Should get a permission denied (403)
        self.assertEqual(response.status_code, 403)

    def test_admin_launcher_tax_table_view(self):
        # Create request
        request = self.factory.get(reverse('miningtaxes:admin_launcher_tax_table'))
        request.user = self.admin_user
        
        # Call view
        response = admin_launcher_tax_table(request)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        
        # Parse JSON response
        data = response.json()
        self.assertIn('data', data)
        self.assertEqual(len(data['data']), 1)  # One ore price entry

    @patch('miningtaxes.views.messages')
    def test_admin_launcher_save_rates_view(self, mock_messages):
        # Create POST data
        post_data = {
            'type_id_45511': '0.15',  # Update tax rate for our ore
        }
        
        # Create request
        request = self.factory.post(
            reverse('miningtaxes:admin_launcher_save_rates'),
            data=post_data
        )
        request.user = self.admin_user
        
        # Mock messages
        request._messages = MagicMock()
        
        # Call view
        response = admin_launcher_save_rates(request)
        
        # Check response - should be a redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('miningtaxes:admin_launcher'))
        
        # Verify tax rate was updated
        updated_ore = self.ore.__class__.objects.get(type_id=45511)
        self.assertEqual(updated_ore.tax_rate, 0.15)
        mock_messages.success.assert_called_once()

    def test_admin_char_json_view(self):
        # Create request
        request = self.factory.get(reverse('miningtaxes:admin_char_json'))
        request.user = self.admin_user
        
        # Call view
        response = admin_char_json(request)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        
        # Parse JSON response
        data = response.json()
        self.assertIn('data', data)

    def test_admin_main_json_view(self):
        # Create request
        request = self.factory.get(reverse('miningtaxes:admin_main_json'))
        request.user = self.admin_user
        
        # Call view
        response = admin_main_json(request)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        
        # Parse JSON response
        data = response.json()
        self.assertIn('data', data)

    def test_admin_tables_view(self):
        # Create request
        request = self.factory.get(reverse('miningtaxes:admin_tables'))
        request.user = self.admin_user
        
        # Call view
        response = admin_tables(request)
        
        # Check response
        self.assertEqual(response.status_code, 200)