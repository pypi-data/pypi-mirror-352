from django import template
from ..models import BrandingTheme, EventInfo, SemanaNavigation

register = template.Library()

@register.simple_tag
def get_active_branding():
    """Retorna o tema de branding ativo"""
    try:
        return BrandingTheme.objects.filter(is_active=True).first()
    except BrandingTheme.DoesNotExist:
        return None

@register.simple_tag  
def get_active_event_info():
    """Retorna as informações do evento ativo"""
    try:
        return EventInfo.objects.filter(is_active=True).first()
    except EventInfo.DoesNotExist:
        return None

@register.simple_tag
def get_active_navigation():
    """Retorna a configuração de navegação ativa"""
    try:
        return SemanaNavigation.objects.filter(is_active=True).first()
    except SemanaNavigation.DoesNotExist:
        return None

@register.inclusion_tag('enap_designsystem/semana_inovacao/includes/branding_vars.html')
def load_branding_css():
    """Template tag para carregar as variáveis CSS do branding"""
    branding = get_active_branding()
    return {'branding': branding}

@register.inclusion_tag('enap_designsystem/semana_inovacao/includes/event_info.html')
def show_event_info():
    """Template tag para exibir informações do evento"""
    event = get_active_event_info()
    return {'event': event}

@register.inclusion_tag('enap_designsystem/semana_inovacao/includes/footer_links.html')
def show_footer_links():
    """Template tag para exibir links do footer"""
    event = get_active_event_info()
    navigation = get_active_navigation()
    return {
        'event': event,
        'navigation': navigation
    }

@register.simple_tag
def get_page_date_display(event_info):
    """Formata as datas do evento de forma inteligente"""
    if not event_info:
        return "29 a 31 de outubro"
    
    start = event_info.start_date
    end = event_info.end_date
    
    if start.month == end.month:
        return f"{start.day} a {end.day} de {start.strftime('%B')}"
    else:
        return f"{start.day} de {start.strftime('%B')} a {end.day} de {end.strftime('%B')}"