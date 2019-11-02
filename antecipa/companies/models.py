from django.db import models
from django.conf import settings

from model_utils.models import TimeStampedModel
from localflavor.br.models import BRCNPJField


class Company(TimeStampedModel):
    trade_name = models.CharField('Nome fantasia', max_length=100)
    cnpj = BRCNPJField(unique=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name='Responsável',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'empresa'
        verbose_name_plural = 'empresas'

    def __str__(self):
        return self.trade_name
