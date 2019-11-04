from django.contrib import admin

from .models import Payment, Anticipation, AnticipationHistory


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['company', 'value', 'due_date']


class AnticipationHistoryInline(admin.TabularInline):
    model = AnticipationHistory
    readonly_fields = ['get_status']
    can_delete = False
    extra = 0

    def get_status(self, obj):
        return obj.get_status_display()

    # def has_add_permission(self, request, obj=None):
    #     return False


@admin.register(Anticipation)
class AnticipationAdmin(admin.ModelAdmin):
    list_display = ['payment', 'value', 'status']
    inlines = [AnticipationHistoryInline]
