from django.conf import settings
from .models import Quote
import random

MANGA_QUOTES = [
    {"text": "Je n'ai qu'un seul père... et c'est Barbe Blanche !", "author": "Portgas D. Ace (One Piece)"},
    {"text": "Ceux qui sont au sommet déterminent ce qui est bien et ce qui est mal !", "author": "Don Quichotte Doflamingo (One Piece)"},
    {"text": "Tu ne le sais pas encore, mais tu es déjà mort !", "author": "Kenshiro (Hokuto no Ken)"},
    {"text": "En étudiant le concept de « démon », je crois que l'humain est celui qui s'en rapproche le plus.", "author": "Migi (Parasite)"},
    {"text": "La plus triste des choses, c'est quand la personne qui t'a donné les meilleurs souvenirs devient elle-même un souvenir.", "author": "Naruto Uzumaki (Naruto)"},
    {"text": "Si tu commences à regretter, tu vas ternir tes décisions futures et laisser les autres faire tes choix pour toi.", "author": "Erwin Smith (L'Attaque des Titans)"},
    {"text": "Vous devriez profiter des petits détours au maximum. C'est là que vous trouverez des choses plus importantes que ce que vous voulez.", "author": "Ging Freecss (Hunter x Hunter)"},
    {"text": "Crois en le toi qui croit en toi !", "author": "Kamina (Gurren Lagann)"},
    {"text": "Une leçon sans douleur n'a pas de sens. Car on ne peut rien gagner sans rien sacrifier.", "author": "Edward Elric (Fullmetal Alchemist)"},
    {"text": "Chez les salauds, j'fais pas la différence entre les mecs et les nanas ! C'est ma politique !", "author": "Eikichi Onizuka (GTO)"}
]

def random_quote(request):
    """
    Context processor that adds a random manga quote to the context.
    Fetches an active quote from the database, or falls back to hardcoded list.
    """
    quote = Quote.objects.filter(is_active=True).order_by('?').first()
    
    if quote:
        quote_data = {"text": quote.text, "author": quote.author}
    else:
        quote_data = random.choice(MANGA_QUOTES)
        
    return {
        'RANDOM_QUOTE': quote_data
    }

def static_version(request):
    """
    Context processor that adds STATIC_VERSION to the context.
    """
    return {
        'STATIC_VERSION': getattr(settings, 'STATIC_VERSION', '1.0.0')
    }
