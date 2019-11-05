from django.test import SimpleTestCase

from model_bakery import baker

from ..models import Company


class TestCompanyModel(SimpleTestCase):
    def setUp(self):
        self.company = baker.prepare(Company, trade_name='Coca Cola', cnpj='83.096.895/0001-37')

    def test_str(self):
        self.assertEqual(str(self.company), 'Coca Cola')
