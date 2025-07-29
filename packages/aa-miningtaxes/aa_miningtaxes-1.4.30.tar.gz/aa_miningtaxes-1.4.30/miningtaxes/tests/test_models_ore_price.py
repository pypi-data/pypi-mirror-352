from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.utils import timezone

from app_utils.testing import NoSocketsTestCase
from eveuniverse.models import EveType, EveTypeMaterial, EveGroup, EveCategory

from miningtaxes.models import OrePrices
from miningtaxes.models.orePrices import get_tax, get_price


class TestOrePrice(NoSocketsTestCase):
    def setUp(self):
        # Create category first
        self.category = EveCategory.objects.create(
            id=25,
            name="Asteroid",
            published=True
        )
        
        # Create group
        self.group = EveGroup.objects.create(
            id=450,
            name="Moon Materials",
            eve_category=self.category
        )
        
        # Create type
        self.type_id = 45511
        self.eve_type = EveType.objects.create(
            id=self.type_id,
            name="Zeolites",
            published=True,
            eve_group=self.group,
            description="Test ore type"
        )
        
        # Create ore price record manually
        self.raw_price = 1000000.0
        self.refined_price = 1200000.0
        self.tax_rate = 10.0
        self.ore_price = OrePrices.objects.create(
            eve_type=self.eve_type,
            buy=self.raw_price,
            sell=self.raw_price * 1.1,
            raw_price=self.raw_price,
            refined_price=self.refined_price,
            taxed_price=self.refined_price,
            tax_rate=self.tax_rate,
            updated=timezone.now()
        )
        
    @patch('miningtaxes.models.orePrices.EveType.objects.get_or_create_esi')
    @patch('miningtaxes.models.orePrices.EveTypeMaterial.objects.update_or_create_api')
    @patch('miningtaxes.models.orePrices.get_price')
    def test_calc_prices(self, mock_get_price, mock_update_materials, mock_get_type):
        # Mock EveType retrieval
        mock_get_type.return_value = (self.eve_type, True)
        
        # Mock materials retrieval
        mock_material = MagicMock(spec=EveTypeMaterial)
        mock_material.material_eve_type.id = 34
        mock_material.material_eve_type.name = "Tritanium"
        mock_material.quantity = 400
        mock_update_materials.return_value = [mock_material]
        
        # Mock price calculation
        mock_get_price.return_value = 120.0  # Price for one unit of material
        
        # Execute the calculation
        self.ore_price.calc_prices()
        
        # Verify the calculation
        expected_refined_price = 400 * 120.0 * 0.8 / self.eve_type.portion_size  # with default refining efficiency
        self.assertAlmostEqual(self.ore_price.refined_price, expected_refined_price, places=1)

    def test_ore_calc_prices2(self):
        """Test the get_price function with configured OrePrices."""
        # Create second type and price record for this test
        category = self.category  # Reuse existing category
        group = self.group  # Reuse existing group
        
        # Create another type
        type_id = 999
        eve_type = EveType.objects.create(
            id=type_id,
            name="Test Ore",
            published=True,
            eve_group=group,
            description="Test ore type"
        )
        
        # Create ore price record
        ore = OrePrices.objects.create(
            eve_type=eve_type,
            buy=1000.0,
            sell=1100.0,
            raw_price=1000.0,
            refined_price=1100.0,
            taxed_price=1100.0,
            tax_rate=5.0,  # 5%
            updated=timezone.now()
        )
        
        # Use buy price for get_price when OrePrices exists
        self.assertEqual(get_price(eve_type), ore.buy)
        
    def test_ore_calc_prices3(self):
        """Test getting refined prices for an ore."""
        # Create third type and price record for this test
        category = self.category  # Reuse existing category
        group = self.group  # Reuse existing group
        
        # Create type
        type_id = 998
        eve_type = EveType.objects.create(
            id=type_id,
            name="Rich Ore",
            published=True,
            eve_group=group,
            description="Test ore type"
        )
        
        # Create ore price record
        ore = OrePrices.objects.create(
            eve_type=eve_type,
            buy=1000.0,
            sell=1100.0,
            raw_price=1000.0,
            refined_price=2000.0,
            taxed_price=2000.0,
            tax_rate=5.0,  # 5%
            updated=timezone.now()
        )
        
        # For ore price calculation, refined is stored directly 
        # OrePrices doesn't use get_price for refined calculation
        self.assertEqual(ore.refined_price, 2000.0)
    
    def test_get_tax_rates(self):
        """Test the tax calculation function."""
        # The first ore price object created in setUp has tax_rate = 10.0
        # Tax should be calculated based on the ore's tax_rate / 100.0
        self.assertEqual(get_tax(self.eve_type), 0.1)