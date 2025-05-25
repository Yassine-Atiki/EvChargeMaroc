from django.contrib import admin
from .models import CategoryFAQ, FAQ, Tutorial, TroubleshootingGuide, SupportTicket, TicketResponse

# Personnalisation de l'affichage des tickets dans l'admin
class TicketResponseInline(admin.TabularInline):
    model = TicketResponse
    extra = 0
    readonly_fields = ('created_at',)

class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'message', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [TicketResponseInline]
    fieldsets = (
        ('Informations du ticket', {
            'fields': ('user', 'subject', 'message')
        }),
        ('Statut', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )

class TicketResponseAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('message', 'user__username', 'ticket__subject')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Informations de la réponse', {
            'fields': ('ticket', 'user', 'message', 'created_at')
        }),
    )

class CategoryFAQAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    search_fields = ('name',)
    ordering = ('order',)

class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'order')
    list_filter = ('category',)
    search_fields = ('question', 'answer')
    ordering = ('category', 'order')

class TutorialAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'content')
    ordering = ('order',)

class TroubleshootingGuideAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'created_at', 'updated_at')
    search_fields = ('title', 'problem', 'solution')
    ordering = ('order',)

# Enregistrer les modèles avec leurs classes Admin
admin.site.register(CategoryFAQ, CategoryFAQAdmin)
admin.site.register(FAQ, FAQAdmin)
admin.site.register(Tutorial, TutorialAdmin)
admin.site.register(TroubleshootingGuide, TroubleshootingGuideAdmin)
admin.site.register(SupportTicket, SupportTicketAdmin)
admin.site.register(TicketResponse, TicketResponseAdmin)
