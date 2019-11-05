from django.contrib import admin

from .models import Payment, Anticipation


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'company', 'value', 'due_date', 'get_created']

    def get_created(self, obj):
        return obj.created
    get_created.short_description = 'Data de emissão'


@admin.register(Anticipation)
class AnticipationAdmin(admin.ModelAdmin):
    list_display = ['payment', 'value', 'status']
