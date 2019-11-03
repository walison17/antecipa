from datetime import date
from decimal import Decimal

from django.test import TestCase
from model_bakery import baker
from freezegun import freeze_time

from ..calculators import AntecipationCalcutor


@freeze_time('2019-9-15')
class TestAntecipationCalculator(TestCase):
    def setUp(self):
        payment = baker.make(
            'payments.Payment', value=Decimal(1000), due_date=date(2019, 10, 1)
        )
        self.calculator = AntecipationCalcutor(payment)

    def test_diff_in_days(self):
        diff = self.calculator._diff_in_days()
        self.assertEqual(diff, 16)
        self.assertIsInstance(diff, int)

    def test_calculate(self):
        self.assertEqual(self.calculator.calculate(), Decimal(984.00))
