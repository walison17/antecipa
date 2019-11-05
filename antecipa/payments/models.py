from datetime import date

from django.db import models
from django.db.models import Case, When, Value, Q, F
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from model_utils.models import TimeStampedModel

from .calculators import AnticipationCalcutor


class PaymentQuerySet(models.QuerySet):
    def with_status(self):
        return self.annotate(
            status=Case(
                When(Q(anticipation__isnull=False), then=F('anticipation__status')),
                When(Q(due_date__lte=date.today()), then=Value('UNAVAILABLE')),
                default=Value('AVAILABLE'),
                output_field=models.CharField()
            )
        )


class Payment(TimeStampedModel):
    description = models.CharField('Descrição', max_length=150)
    value = models.DecimalField('Valor', max_digits=9, decimal_places=2)
    due_date = models.DateField('Data de vencimento')
    company = models.ForeignKey(
        'companies.Company',
        verbose_name='Empresa',
        related_name='payments',
        on_delete=models.PROTECT
    )

    objects = PaymentQuerySet.as_manager()

    class Meta:
        verbose_name = 'pagamento'
        verbose_name_plural = 'pagamentos'
        ordering = ['due_date']

    def __str__(self):
        return f'ID: {self.pk} @ {self.company}'


class Anticipation(TimeStampedModel):
    WAITING = 'WAITING'
    CONFIRMED = 'CONFIRMED'
    DENIED = 'DENIED'
    STATUSES = (
        (WAITING, 'Aguardando confirmação'),
        (CONFIRMED, 'Antecipado'),
        (DENIED, 'Negado')
    )

    payment = models.OneToOneField(
        Payment,
        verbose_name='Pagamento',
        on_delete=models.CASCADE,
        limit_choices_to=Q(due_date__gt=date.today()) & Q(anticipation__isnull=True)
    )
    value = models.DecimalField('Valor antecipado', max_digits=9, decimal_places=2, editable=False)
    status = models.CharField(
        'Situação', max_length=20, choices=STATUSES, default=WAITING, editable=False
    )

    class Meta:
        verbose_name = 'antecipação'
        verbose_name_plural = 'antecipações'
        ordering = ['created']

    def __str__(self):
        return (
            f'{self.payment}, valor antecipado: {self.value}, '
            f'status: {self.get_status_display()}'
        )

    def save(self, *args, **kwargs):
        calculator = AnticipationCalcutor(self.payment)
        self.value = calculator.calculate()
        return super().save(*args, **kwargs)

    def confirm(self):
        self.status = self.CONFIRMED
        self.save(update_fields=['status'])

    def deny(self):
        self.status = self.DENIED
        self.save(update_fields=['status'])


class AnticipationHistory(models.Model):
    status = models.CharField('Situação', max_length=20, choices=Anticipation.STATUSES)
    created = models.DateTimeField('Criado em', auto_now_add=True, editable=False)
    anticipation = models.ForeignKey(
        Anticipation,
        verbose_name='Antecipação',
        related_name='history',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'histórico de antecipação'
        verbose_name_plural = 'históricos de antecipações'
        ordering = ['-created']
        unique_together = ['anticipation', 'status']

    def __str__(self):
        return f'Antecipação: {self.anticipation.pk}, status: {self.get_status_display()}'


@receiver(post_save, sender=Anticipation)
def update_anticipation_history(sender, instance, **kwargs):
    if not instance.history.filter(status=instance.status).exists():
        instance.history.create(status=instance.status)
