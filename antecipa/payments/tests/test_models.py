from datetime import date
from decimal import Decimal

from django.test import TestCase
from model_bakery import baker
from freezegun import freeze_time

from ..models import Antecipation, Payment


@freeze_time('2019-9-15')
class TestAntecipationModel(TestCase):
    def setUp(self):
        self.payment = baker.make(
            'payments.Payment', value=Decimal(1000), due_date=date(2019, 10, 1)
        )
        self.antecipation = baker.make(Antecipation, payment=self.payment)

    def test_calculate_value_on_save(self):
        self.assertEqual(self.antecipation.value, Decimal(984.00))
        self.assertEqual(self.antecipation.status, Antecipation.WAITING)

    def test_confirm(self):
        self.antecipation.confirm()

        self.antecipation.refresh_from_db()
        self.assertEqual(self.antecipation.status, Antecipation.CONFIRMED)

    def test_deny(self):
        self.antecipation.deny()

        self.antecipation.refresh_from_db()
        self.assertEqual(self.antecipation.status, Antecipation.DENIED)


class TestAntecipationHistoryModel(TestCase):
    def test_must_create_when_antecipation_is_created(self):
        antecipation = baker.make(Antecipation)

        self.assertEqual(antecipation.history.count(), 1)

    def test_must_create_when_antecipation_status_changed(self):
        antecipation = baker.make(Antecipation)

        antecipation.confirm()

        self.assertEqual(antecipation.history.count(), 2)

    def test_not_duplicate_status_history(self):
        antecipation = baker.make(Antecipation)

        antecipation.status = Antecipation.WAITING
        antecipation.save(update_fields=['status'])

        self.assertEqual(antecipation.history.count(), 1)


@freeze_time('2019-11-15')
class TestPaymentManager(TestCase):
    def setUp(self):
        self.company = baker.make('companies.Company')

    def test_annotate_available_status(self):
        baker.make('payments.Payment', company=self.company, due_date=date(2019, 11, 30))

        self.assertQuerysetEqual(Payment.objects.with_status(), ['AVAILABLE'], lambda p: p.status)

    def test_annotate_unavailable_status(self):
        baker.make('payments.Payment', company=self.company, due_date=date(2019, 11, 1))

        self.assertQuerysetEqual(Payment.objects.with_status(), ['UNAVAILABLE'], lambda p: p.status)
