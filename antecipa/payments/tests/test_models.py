from datetime import date
from decimal import Decimal

from django.test import TestCase
from model_bakery import baker
from freezegun import freeze_time

from ..models import Anticipation, Payment


@freeze_time('2019-9-15')
class TestAnticipationModel(TestCase):
    def setUp(self):
        self.payment = baker.make(
            'payments.Payment', value=Decimal(1000), due_date=date(2019, 10, 1)
        )
        self.anticipation = baker.make(Anticipation, payment=self.payment)

    def test_calculate_value_on_save(self):
        self.assertEqual(self.anticipation.value, Decimal(984.00))
        self.assertEqual(self.anticipation.status, Anticipation.WAITING)

    def test_confirm(self):
        self.anticipation.confirm()

        self.anticipation.refresh_from_db()
        self.assertEqual(self.anticipation.status, Anticipation.CONFIRMED)

    def test_deny(self):
        self.anticipation.deny()

        self.anticipation.refresh_from_db()
        self.assertEqual(self.anticipation.status, Anticipation.DENIED)


class TestAnticipationHistoryModel(TestCase):
    def test_must_create_when_anticipation_is_created(self):
        anticipation = baker.make(Anticipation)

        self.assertEqual(anticipation.history.count(), 1)

    def test_must_create_when_anticipation_status_changed(self):
        anticipation = baker.make(Anticipation)

        anticipation.confirm()

        self.assertEqual(anticipation.history.count(), 2)

    def test_not_duplicate_status_history(self):
        anticipation = baker.make(Anticipation)

        anticipation.status = Anticipation.WAITING
        anticipation.save(update_fields=['status'])

        self.assertEqual(anticipation.history.count(), 1)


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
