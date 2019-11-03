from decimal import Decimal
from datetime import date


class AntecipationCalcutor:
    MONTHLY_PERCENTAGE = 0.03

    def __init__(self, payment):
        self.payment = payment

    def calculate(self):
        tax = self.payment.value * (Decimal(self.MONTHLY_PERCENTAGE / 30) * self._diff_in_days())
        return round(self.payment.value - tax, 2)

    def _diff_in_days(self):
        diff = self.payment.due_date - date.today()
        return int(diff.days)
