from unittest.mock import patch, MagicMock

from django.utils import timezone
from app_utils.testing import NoSocketsTestCase

from esi.models import Token

from miningtaxes.models import Character, AdminCharacter, Settings, OrePrices
from miningtaxes.tasks import (
    update_character,
    update_admin_character,
    add_tax_credits,
    update_all_prices,
    precalcs,
    update_daily,
    notify_taxes_due,
    notify_second_taxes_due,
    apply_interest,
    auto_add_chars,
)
from miningtaxes.tests.utils import (
    create_miningtaxes_character,
    create_miningtaxes_admincharacter,
    create_user_from_evecharacter_with_access,
    add_miningtaxes_character_to_user,
    create_test_settings,
    create_test_ore_price,
)


class TasksTestCase(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.token_patch = patch('esi.models.Token.objects.filter')
        cls.mock_token = cls.token_patch.start()
        mock_token_instance = MagicMock(spec=Token)
        cls.mock_token.return_value.require_scopes.return_value.require_valid.return_value.first.return_value = mock_token_instance

    @classmethod
    def tearDownClass(cls):
        cls.token_patch.stop()
        super().tearDownClass()

    def setUp(self):
        # Create user with basic access
        self.user = create_user_from_evecharacter_with_access(
            character_id=1001,
            character_name='Test Character',
            corporation_name='Test Corp',
            alliance_name='TEST',
            permission_name='miningtaxes.basic_access'
        )
        
        # Create character
        self.character = create_miningtaxes_character(
            character_id=1001,
            character_name='Test Character',
            corporation_id=2001,
            corporation_name='Test Corp'
        )
        add_miningtaxes_character_to_user(self.character, self.user)

        # Create admin user
        self.admin_user = create_user_from_evecharacter_with_access(
            character_id=1002,
            character_name='Admin Character',
            corporation_name='Test Corp',
            alliance_name='TEST',
            permission_name='miningtaxes.admin_access'
        )
        
        # Create admin character
        self.admin_character = create_miningtaxes_admincharacter(
            character_id=1002,
            character_name='Admin Character',
            corporation_id=2001,
            corporation_name='Test Corp'
        )
        add_miningtaxes_character_to_user(self.admin_character, self.admin_user)

        # Create settings
        self.settings = create_test_settings()

        # Create ore prices
        self.ore_price = create_test_ore_price()

    @patch('miningtaxes.tasks.get_esi_client')
    def test_update_character(self, mock_get_esi_client):
        # Setup mock ESI client
        mock_esi = MagicMock()
        mock_get_esi_client.return_value = mock_esi
        
        # Mock mining ledger response
        mock_mining_data = [
            {
                'date': '2023-01-01',
                'quantity': 1000,
                'type_id': 45511,
                'solar_system_id': 30000142
            }
        ]
        mock_esi.Character.get_characters_character_id_mining.return_value = mock_mining_data
        
        # Call the task
        result = update_character(self.character.pk)
        
        # Assertions
        self.assertTrue(result)
        self.character.refresh_from_db()
        self.assertIsNotNone(self.character.last_update)
        
        # Verify ESI client was called with correct parameters
        mock_get_esi_client.assert_called_once()
        mock_esi.Character.get_characters_character_id_mining.assert_called_once_with(
            character_id=self.character.character_id,
            if_none_match=None
        )

    @patch('miningtaxes.tasks.get_esi_client')
    def test_update_admin_character(self, mock_get_esi_client):
        # Setup mock ESI client
        mock_esi = MagicMock()
        mock_get_esi_client.return_value = mock_esi
        
        # Mock mining observer response
        mock_observer_data = [
            {
                'last_updated': '2023-01-01T12:00:00Z',
                'observer_id': 1000000000001,
                'observer_type': 'structure',
                'character_id': 1001,
                'quantity': 1000,
                'recorded_corporation_id': 2001,
                'type_id': 45511
            }
        ]
        mock_esi.Industry.get_corporation_corporation_id_mining_observers.return_value = [
            {'observer_id': 1000000000001, 'last_updated': '2023-01-01T12:00:00Z'}
        ]
        mock_esi.Industry.get_corporation_corporation_id_mining_observers_observer_id.return_value = mock_observer_data
        
        # Mock structure info
        mock_esi.Universe.get_universe_structures_structure_id.return_value = {
            'name': 'Test Structure',
            'solar_system_id': 30000142
        }
        
        # Call the task
        result = update_admin_character(self.admin_character.pk)
        
        # Assertions
        self.assertTrue(result)
        self.admin_character.refresh_from_db()
        self.assertIsNotNone(self.admin_character.last_update)
        
        # Verify ESI client was called with correct parameters
        mock_get_esi_client.assert_called_once()
        mock_esi.Industry.get_corporation_corporation_id_mining_observers.assert_called_once_with(
            corporation_id=self.admin_character.corporation_id,
            if_none_match=None
        )

    @patch('miningtaxes.tasks.get_esi_client')
    def test_add_tax_credits(self, mock_get_esi_client):
        # Setup mock ESI client
        mock_esi = MagicMock()
        mock_get_esi_client.return_value = mock_esi
        
        # Mock wallet journal response
        mock_wallet_data = [
            {
                'amount': 1000000.0,
                'date': '2023-01-01T12:00:00Z',
                'description': 'mining taxes',
                'reason': 'player donation',
                'ref_type': 'player_donation',
                'first_party_id': 1001
            }
        ]
        mock_esi.Wallet.get_corporations_corporation_id_wallets_division_journal.return_value = mock_wallet_data
        
        # Call the task
        result = add_tax_credits(self.admin_character.pk)
        
        # Assertions
        self.assertTrue(result)
        
        # Verify ESI client was called with correct parameters
        mock_get_esi_client.assert_called_once()
        mock_esi.Wallet.get_corporations_corporation_id_wallets_division_journal.assert_called_once()

    @patch('miningtaxes.tasks.get_bulk_prices')
    def test_update_all_prices(self, mock_get_bulk_prices):
        # Setup mock price data
        mock_price_data = {
            45511: {
                'buy': 900000.0,
                'sell': 1100000.0
            }
        }
        mock_get_bulk_prices.return_value = mock_price_data
        
        # Call the task
        result = update_all_prices()
        
        # Assertions
        self.assertTrue(result)
        updated_price = OrePrices.objects.get(type_id=45511)
        self.assertEqual(updated_price.raw_price, 1100000.0)  # Should use sell price
        
        # Verify bulk prices function was called
        mock_get_bulk_prices.assert_called_once()

    def test_apply_interest(self):
        # Setup test data - character with taxes due
        self.character.current_taxes = 1000000.0
        self.character.taxes_paid = False
        self.character.save()
        
        # Call the task
        apply_interest()
        
        # Assertions
        self.character.refresh_from_db()
        expected_taxes = 1000000.0 * (1 + self.settings.interest_rate)
        self.assertEqual(self.character.current_taxes, expected_taxes)

    @patch('miningtaxes.tasks.update_character')
    @patch('miningtaxes.tasks.update_admin_character')
    @patch('miningtaxes.tasks.update_all_prices')
    @patch('miningtaxes.tasks.precalcs')
    def test_update_daily(self, mock_precalcs, mock_update_prices, 
                           mock_update_admin, mock_update_char):
        # Setup mocks to return success
        mock_update_char.return_value = True
        mock_update_admin.return_value = True
        mock_update_prices.return_value = True
        mock_precalcs.return_value = True
        
        # Call the task
        result = update_daily()
        
        # Assertions
        self.assertTrue(result)
        mock_update_prices.assert_called_once()
        mock_precalcs.assert_called_once()
        
        # Character updates should be called for each character
        self.assertEqual(mock_update_char.call_count, 1)
        self.assertEqual(mock_update_admin.call_count, 1)

    @patch('miningtaxes.tasks.notify_user')
    def test_notify_taxes_due(self, mock_notify_user):
        # Setup test data - character with taxes due
        self.character.current_taxes = 1000000.0
        self.character.taxes_paid = False
        self.character.save()
        
        # Call the task
        notify_taxes_due()
        
        # Assertions
        mock_notify_user.assert_called_once_with(
            self.user,
            'Mining Taxes Due',
            'Your mining taxes of 1,000,000.00 ISK are due.'
        )

    @patch('miningtaxes.tasks.notify_user')
    def test_notify_second_taxes_due(self, mock_notify_user):
        # Setup test data - character with taxes due and past grace period
        self.character.current_taxes = 1000000.0
        self.character.taxes_paid = False
        self.character.save()
        
        # Set settings past grace period
        self.settings.current_month = (timezone.now().month - 1) % 12 or 12  # Previous month
        if self.settings.current_month == 12:
            self.settings.current_year = timezone.now().year - 1
        self.settings.save()
        
        # Call the task
        notify_second_taxes_due()
        
        # Assertions
        mock_notify_user.assert_called_once()
        
    @patch('miningtaxes.tasks.Character.objects.filter')
    @patch('miningtaxes.tasks.update_character')
    def test_auto_add_chars(self, mock_update_character, mock_character_filter):
        # Setup mocks
        mock_update_character.return_value = True
        mock_character_filter.return_value.values_list.return_value = [self.character.pk]
        
        # Call the task
        result = auto_add_chars()
        
        # Assertions
        self.assertTrue(result)
        mock_update_character.assert_called_once_with(self.character.pk)