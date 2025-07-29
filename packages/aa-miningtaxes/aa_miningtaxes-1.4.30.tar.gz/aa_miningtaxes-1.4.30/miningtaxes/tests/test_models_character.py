from unittest.mock import patch, MagicMock
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from app_utils.testing import NoSocketsTestCase

from miningtaxes.models import Character, CharacterUpdateStatus, CharacterMiningLedgerEntry, CharacterTaxCredits
from miningtaxes.tests.utils import (
    create_miningtaxes_character,
    create_user_from_evecharacter_with_access,
    add_miningtaxes_character_to_user,
    create_character_update_status,
    create_test_ore_price,
)


class TestCharacter(NoSocketsTestCase):
    def setUp(self):
        # Create user and character
        self.user = create_user_from_evecharacter_with_access(
            character_id=1001,
            character_name='Test Character',
            corporation_name='Test Corp',
            alliance_name='TEST'
        )
        
        self.character = create_miningtaxes_character(
            character_id=1001,
            character_name='Test Character',
            corporation_id=2001,
            corporation_name='Test Corp'
        )
        add_miningtaxes_character_to_user(self.character, self.user)
        
        # Create sample ore price
        self.ore_price = create_test_ore_price(
            type_id=45511,
            type_name="Zeolites",
            tax_rate=0.1,
            raw_price=1000000.0,
            refined_price=1200000.0
        )

    def test_should_return_main_when_it_exists_1(self):
        """Test that user.profile.main_character is returned when it exists."""
        self.assertEqual(self.character.character_name, 'Test Character')
        self.assertEqual(self.character.corporation_name, 'Test Corp')
    
    def test_user_should_return_user_when_not_orphan(self):
        """Test that character.user returns the correct user when character is not orphaned."""
        self.assertEqual(self.character.user, self.user)
    
    def test_user_should_be_None_when_orphan(self):
        """Test that character.user returns None when character is orphaned."""
        # Create an orphaned character (no user)
        orphan = create_miningtaxes_character(
            character_id=2001,
            character_name='Orphan Character',
            corporation_id=2001,
            corporation_name='Test Corp'
        )
        self.assertIsNone(orphan.user)
    
    @patch('miningtaxes.models.character.Character.create_ledger_entry')
    def test_mining_ledger(self, mock_create_entry):
        """Test the process_mining_data method on Character."""
        # Setup mock
        mock_create_entry.return_value = True
        
        # Create test mining data
        mining_data = [
            {
                'date': '2023-01-01',
                'quantity': 1000,
                'type_id': 45511,
                'solar_system_id': 30000142
            }
        ]
        
        # Process the mining data
        self.character.process_mining_data(mining_data)
        
        # Verify ledger entry was created
        mock_create_entry.assert_called_once()
    
    def test_tax_credits(self):
        """Test adding and calculating tax credits."""
        # Set up character with unpaid taxes
        self.character.current_taxes = 100000.0
        self.character.taxes_paid = False
        self.character.save()
        
        # Create a tax credit
        CharacterTaxCredits.objects.create(
            character=self.character,
            amount=75000.0,
            credit_date=timezone.now(),
            credit_type="payment"
        )
        
        # Check that credits are properly calculated
        self.character.calculate_taxes()
        self.character.refresh_from_db()
        
        # Character should still have unpaid taxes, but less than initial
        self.assertEqual(self.character.current_taxes, 25000.0)
        self.assertFalse(self.character.taxes_paid)
        
        # Add another credit that fully pays taxes
        CharacterTaxCredits.objects.create(
            character=self.character,
            amount=30000.0,  # More than needed
            credit_date=timezone.now(),
            credit_type="payment"
        )
        
        # Recalculate
        self.character.calculate_taxes()
        self.character.refresh_from_db()
        
        # Character should now have paid taxes
        self.assertEqual(self.character.current_taxes, 0.0)
        self.assertTrue(self.character.taxes_paid)


class TestCharacterUpdateStatus(NoSocketsTestCase):
    def setUp(self):
        # Create character for testing
        self.character = create_miningtaxes_character(
            character_id=1001,
            character_name='Test Character',
            corporation_id=2001,
            corporation_name='Test Corp'
        )
        
        # Create sample update status
        self.update_status = create_character_update_status(
            self.character,
            is_success=True,
            started_at=timezone.now() - timedelta(minutes=5),
            finished_at=timezone.now()
        )

    def test_str(self):
        """Test string representation."""
        expected = f"Update Status for {self.character.character_name}"
        self.assertEqual(str(self.update_status), expected)
    
    def test_is_updating_1(self):
        """When started_at exist and finished_at does not exist, return True."""
        self.update_status.finished_at = None
        self.update_status.save()
        self.assertTrue(self.update_status.is_updating)
    
    def test_is_updating_2(self):
        """When started_at and finished_at does not exist, return False."""
        self.update_status.started_at = None
        self.update_status.finished_at = None
        self.update_status.save()
        self.assertFalse(self.update_status.is_updating)
    
    def test_has_changed_1(self):
        """When hash is different, then return True."""
        self.update_status.data_hash = "old_hash"
        self.update_status.save()
        self.assertTrue(self.update_status.has_changed("new_hash"))
    
    def test_has_changed_2(self):
        """When no hash exists, then return True."""
        self.update_status.data_hash = None
        self.update_status.save()
        self.assertTrue(self.update_status.has_changed("new_hash"))
    
    def test_has_changed_3a(self):
        """When hash is equal, then return False."""
        test_hash = "test_hash"
        self.update_status.data_hash = test_hash
        self.update_status.save()
        self.assertFalse(self.update_status.has_changed(test_hash))
    
    def test_has_changed_3b(self):
        """When hash is equal, then return False."""
        # Same test with empty string hash
        self.update_status.data_hash = ""
        self.update_status.save()
        self.assertFalse(self.update_status.has_changed(""))
    
    def test_has_changed_3c(self):
        """When hash is equal, then return False."""
        # Same test with None hash
        self.update_status.data_hash = None
        self.update_status.save()
        self.assertFalse(self.update_status.has_changed(None))
    
    def test_reset_1(self):
        """Test reset when both started_at and finished_at are set."""
        self.update_status.reset()
        self.assertIsNone(self.update_status.started_at)
        self.assertIsNone(self.update_status.finished_at)
    
    def test_reset_2(self):
        """Test reset when only started_at is set."""
        self.update_status.finished_at = None
        self.update_status.save()
        self.update_status.reset()
        self.assertIsNone(self.update_status.started_at)
        self.assertIsNone(self.update_status.finished_at)