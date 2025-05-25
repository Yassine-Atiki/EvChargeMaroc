from django.contrib import admin
from .models import Users, ProprietaireVE, Fournisseur

# Personnalisation de l'affichage des utilisateurs dans l'admin
class UsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('CIN', 'first_name', 'last_name', 'username', 'email', 'phone_number')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
    )

class ProprietaireVEAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('CIN', 'first_name', 'last_name', 'username', 'email', 'phone_number')
        }),
        ('Permissions', {
            'fields': ('is_active',)
        }),
    )

class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('CIN', 'first_name', 'last_name', 'username', 'email', 'phone_number')
        }),
        ('Permissions', {
            'fields': ('is_active',)
        }),
    )

# Enregistrer les modèles avec leurs classes Admin
admin.site.register(Users, UsersAdmin)
admin.site.register(ProprietaireVE, ProprietaireVEAdmin)
admin.site.register(Fournisseur, FournisseurAdmin)