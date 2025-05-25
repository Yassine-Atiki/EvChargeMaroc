from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import CategoryFAQ, FAQ, Tutorial, TroubleshootingGuide, SupportTicket, TicketResponse
from .forms import SupportTicketForm, TicketResponseForm
from django.contrib.admin.views.decorators import staff_member_required
from users.models import Fournisseur, ProprietaireVE

# Exemple pour la vue help_home
def help_home(request):
    """Page d'accueil de la section d'aide"""
    # Assurez-vous que le contexte utilisateur est préservé
    return render(request, 'help/help_home.html')

def faq_list(request):
    """Liste des FAQs par catégorie"""
    categories = CategoryFAQ.objects.all()
    return render(request, 'help/faq_list.html', {'categories': categories})

def tutorial_list(request):
    """Liste des tutoriels"""
    tutorials = Tutorial.objects.all()
    return render(request, 'help/tutorial_list.html', {'tutorials': tutorials})

def tutorial_detail(request, tutorial_id):
    """Détail d'un tutoriel"""
    tutorial = get_object_or_404(Tutorial, id=tutorial_id)
    return render(request, 'help/tutorial_detail.html', {'tutorial': tutorial})

def troubleshooting_list(request):
    """Liste des guides de dépannage"""
    guides = TroubleshootingGuide.objects.all()
    return render(request, 'help/troubleshooting_list.html', {'guides': guides})

@login_required
def support_home(request):
    """Page d'accueil du support"""
    user_tickets = SupportTicket.objects.filter(user=request.user)
    return render(request, 'help/support_home.html', {'tickets': user_tickets})

@login_required
def create_ticket(request):
    """Création d'un ticket de support"""
    if request.method == 'POST':
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('help:support_home')
    else:
        form = SupportTicketForm()
    
    return render(request, 'help/create_ticket.html', {'form': form})

@login_required
def ticket_detail(request, ticket_id):
    """Détail d'un ticket de support"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    responses = ticket.responses.all()
    
    if request.method == 'POST':
        form = TicketResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.ticket = ticket
            response.user = request.user
            response.save()
            return redirect('help:ticket_detail', ticket_id=ticket.id)
    else:
        form = TicketResponseForm()
    
    return render(request, 'help/ticket_detail.html', {
        'ticket': ticket,
        'responses': responses,
        'form': form
    })

# Ajouter cette vue à la fin du fichier
# Importez le décorateur user_passes_test
from django.contrib.auth.decorators import user_passes_test

# Fonction pour vérifier si l'utilisateur est un superuser
def is_superuser(user):
    return user.is_authenticated and user.is_superuser

# Remplacez le décorateur staff_member_required par user_passes_test
# Modifiez l'utilisation du décorateur pour inclure la redirection
@user_passes_test(is_superuser, login_url='help:permission_denied')
def admin_tickets(request):
    """Vue d'administration des tickets"""
    tickets = SupportTicket.objects.all().order_by('-created_at')
    return render(request, 'help/admin/ticket_list.html', {'tickets': tickets})

@user_passes_test(is_superuser, login_url='help:permission_denied')
def admin_ticket_detail(request, ticket_id):
    """Détail d'un ticket pour l'administrateur"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    responses = ticket.responses.all()
    
    if request.method == 'POST':
        form = TicketResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.ticket = ticket
            response.user = request.user
            response.save()
            
            # Mettre à jour le statut du ticket si nécessaire
            if 'update_status' in request.POST:
                ticket.status = request.POST.get('status')
                ticket.save()
                
            return redirect('help:admin_ticket_detail', ticket_id=ticket.id)
    else:
        form = TicketResponseForm()
    
    return render(request, 'help/admin/ticket_detail.html', {
        'ticket': ticket,
        'responses': responses,
        'form': form
    })

# Ajoutez cette fonction dans views.py
def permission_denied(request):
    return render(request, 'help/permission_denied.html')


# Ajoutez cette fonction d'aide
def get_user_context(request):
    """Ajoute des informations sur le type d'utilisateur au contexte"""
    context = {}
    if request.user.is_authenticated:
        # Vérifier explicitement le type d'utilisateur
        context['is_fournisseur'] = isinstance(request.user, Fournisseur)
        context['is_proprietaire'] = isinstance(request.user, ProprietaireVE)
    return context

# Puis modifiez chaque vue pour utiliser cette fonction
def help_home(request):
    """Page d'accueil de la section d'aide"""
    context = get_user_context(request)
    return render(request, 'help/help_home.html', context)

def faq_list(request):
    """Liste des FAQs par catégorie"""
    categories = CategoryFAQ.objects.all()
    context = {'categories': categories}
    context.update(get_user_context(request))
    return render(request, 'help/faq_list.html', context)

# Faites de même pour toutes les autres vues
