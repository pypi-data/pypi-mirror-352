# semana_models.py - Páginas e Models da Semana de Inovação
from django.db import models
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

# Importar os blocks da Semana
from .semana_blocks import (
    ImageBlock, ParticipanteBlock, StatBlock, GaleriaFotoBlock,
    FAQItemBlock, FAQTabBlock, AtividadeBlock, HospitalityCardBlock,
    VideoBlock, CertificadoBlock, NewsletterBlock, ContatoBlock, FooterBlock
)


# =============================================================================
# SNIPPETS - COMPONENTES REUTILIZÁVEIS
# =============================================================================

@register_snippet
class BrandingTheme(ClusterableModel):
    """Sistema de Branding e Cores Dinâmicas"""
    name = models.CharField("Nome do Tema", max_length=100)
    
    # Cores principais
    cor_primaria = models.CharField("Cor Primária", max_length=7, default="#163841")
    cor_secundaria = models.CharField("Cor Secundária", max_length=7, default="#FFEA05")
    cor_texto_destaque = models.CharField("Cor do Texto Destaque", max_length=7, default="#8B951C")
    
    # Cores de fundo para cada seção
    cor_fundo_banner = models.CharField("Cor Fundo Banner", max_length=7, default="#4A9AA8")
    cor_fundo_destaques = models.CharField("Cor Fundo Destaques", max_length=7, default="#1a2e38")
    cor_fundo_video = models.CharField("Cor Fundo Video", max_length=7, default="#4A9AA8")
    cor_fundo_numeros = models.CharField("Cor Fundo Números", max_length=7, default="#EEEEEE")
    cor_fundo_certificado = models.CharField("Cor Fundo Certificado", max_length=7, default="#2B5E2B")
    cor_fundo_forms = models.CharField("Cor Fundo Forms", max_length=7, default="#FFFFFF")
    cor_fundo_galeria = models.CharField("Cor Fundo Galeria", max_length=7, default="#1a2e38")
    cor_fundo_newsletter = models.CharField("Cor Fundo Newsletter", max_length=7, default="#EEEEEE")
    cor_fundo_contato = models.CharField("Cor Fundo Contato", max_length=7, default="#4A9AA8")
    
    is_active = models.BooleanField("Tema Ativo", default=False)

    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('is_active'),
        ], heading="Informações Básicas"),
        
        MultiFieldPanel([
            FieldPanel('cor_primaria'),
            FieldPanel('cor_secundaria'),
            FieldPanel('cor_texto_destaque'),
        ], heading="Cores Principais"),
        
        MultiFieldPanel([
            FieldPanel('cor_fundo_banner'),
            FieldPanel('cor_fundo_destaques'),
            FieldPanel('cor_fundo_video'),
            FieldPanel('cor_fundo_numeros'),
            FieldPanel('cor_fundo_certificado'),
            FieldPanel('cor_fundo_forms'),
            FieldPanel('cor_fundo_galeria'),
            FieldPanel('cor_fundo_newsletter'),
            FieldPanel('cor_fundo_contato'),
        ], heading="Cores de Fundo das Seções"),
    ]

    def save(self, *args, **kwargs):
        if self.is_active:
            BrandingTheme.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {'(Ativo)' if self.is_active else ''}"

    class Meta:
        verbose_name = "Tema de Branding"
        verbose_name_plural = "Temas de Branding"


@register_snippet
class EventInfo(models.Model):
    """Informações centralizadas do evento"""
    name = models.CharField("Nome do Evento", max_length=200, default="Semana de Inovação")
    year = models.CharField("Ano", max_length=4, default="2025")
    tagline = models.CharField("Slogan", max_length=300, default="O maior evento de inovação em governo da América Latina")
    
    # Datas
    start_date = models.DateField("Data de Início")
    end_date = models.DateField("Data de Fim")
    
    # Contatos
    contact_email = models.EmailField("Email de Contato", default="contato.si@enap.gov.br")
    
    # Redes sociais
    youtube_url = models.URLField("YouTube", blank=True)
    instagram_url = models.URLField("Instagram", blank=True)
    linkedin_url = models.URLField("LinkedIn", blank=True)
    
    is_active = models.BooleanField("Configuração Ativa", default=True)

    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('year'),
            FieldPanel('tagline'),
            FieldPanel('is_active'),
        ], heading="Informações Básicas"),
        
        MultiFieldPanel([
            FieldPanel('start_date'),
            FieldPanel('end_date'),
        ], heading="Datas do Evento"),
        
        MultiFieldPanel([
            FieldPanel('contact_email'),
        ], heading="Contatos"),
        
        MultiFieldPanel([
            FieldPanel('youtube_url'),
            FieldPanel('instagram_url'),
            FieldPanel('linkedin_url'),
        ], heading="Redes Sociais"),
    ]

    def save(self, *args, **kwargs):
        if self.is_active:
            EventInfo.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.year}"

    class Meta:
        verbose_name = "Informações do Evento"
        verbose_name_plural = "Informações do Evento"


@register_snippet
class SemanaNavigation(ClusterableModel):
    """Configuração da navegação global da Semana"""
    
    # Logo
    logo_stream = StreamField([
        ('logo_imagem', ImageBlock()),
    ], blank=True, use_json_field=True)
    logo_alt_text = models.CharField("Texto Alternativo do Logo", max_length=200, blank=True)
    
    # Links de navegação
    sobre_link = models.URLField("Link Sobre", blank=True)
    nossa_historia_link = models.URLField("Link Nossa História", blank=True)
    o_local_link = models.URLField("Link O Local", blank=True)
    programacao_link = models.URLField("Link Programação", blank=True)
    quem_vai_estar_la_link = models.URLField("Link Quem vai estar lá", blank=True)
    noticias_link = models.URLField("Link Notícias", blank=True)
    apoie_inovacao_link = models.URLField("Link Apoie a Inovação", blank=True)
    perguntas_frequentes_link = models.URLField("Link Perguntas Frequentes", blank=True)
    entenda_gamificacao_link = models.URLField("Link Entenda Gamificação", blank=True)
    
    # Seletor de idiomas
    mostrar_seletor_idiomas = models.BooleanField("Mostrar Seletor de Idiomas", default=True)
    pt_br_link = models.URLField("Link PT-BR", blank=True)
    en_link = models.URLField("Link EN", blank=True)
    es_link = models.URLField("Link ES", blank=True)
    
    # Busca
    mostrar_busca = models.BooleanField("Mostrar Busca", default=True)
    
    # CTA
    cta_texto = models.CharField("Texto do CTA", max_length=100, default="Inscreva-se")
    cta_link = models.URLField("Link do CTA", blank=True)
    
    # JavaScript personalizado
    javascript_personalizado = models.TextField("JavaScript Personalizado", blank=True)
    
    is_active = models.BooleanField("Configuração Ativa", default=True)

    panels = [
        MultiFieldPanel([
            FieldPanel('logo_stream'),
            FieldPanel('logo_alt_text'),
            FieldPanel('is_active'),
        ], heading="Logo"),
        
        MultiFieldPanel([
            FieldPanel('sobre_link'),
            FieldPanel('nossa_historia_link'),
            FieldPanel('o_local_link'),
            FieldPanel('programacao_link'),
            FieldPanel('quem_vai_estar_la_link'),
            FieldPanel('noticias_link'),
            FieldPanel('apoie_inovacao_link'),
            FieldPanel('perguntas_frequentes_link'),
            FieldPanel('entenda_gamificacao_link'),
        ], heading="Links de Navegação"),
        
        MultiFieldPanel([
            FieldPanel('mostrar_seletor_idiomas'),
            FieldPanel('pt_br_link'),
            FieldPanel('en_link'),
            FieldPanel('es_link'),
        ], heading="Seletor de Idiomas"),
        
        MultiFieldPanel([
            FieldPanel('mostrar_busca'),
        ], heading="Busca"),
        
        MultiFieldPanel([
            FieldPanel('cta_texto'),
            FieldPanel('cta_link'),
        ], heading="Call to Action"),
        
        MultiFieldPanel([
            FieldPanel('javascript_personalizado'),
        ], heading="JavaScript Personalizado"),
    ]

    def save(self, *args, **kwargs):
        if self.is_active:
            SemanaNavigation.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Navegação {'(Ativa)' if self.is_active else ''}"

    class Meta:
        verbose_name = "Configuração de Navegação"
        verbose_name_plural = "Configurações de Navegação"


# =============================================================================
# PÁGINAS PRINCIPAIS
# =============================================================================

class SemanaHomePage(Page):
    """Página inicial da Semana de Inovação - PÁGINA PRINCIPAL"""
    
    
    # Seção Banner/Hero
    banner_titulo = RichTextField("Título do Banner", blank=True)
    banner_subtitulo = models.CharField("Subtítulo do Banner", max_length=200, blank=True)
    banner_texto_botao = models.CharField("Texto do Botão", max_length=100, default="Saiba mais")
    logo_hero_stream = StreamField([
        ('imagem', ImageBlock()),
    ], blank=True, use_json_field=True)
    logo_hero_link = models.URLField("Link do Logo Hero", blank=True)
    banner_imagem = StreamField([
        ('banner_imagem', ImageBlock()),
    ], blank=True, use_json_field=True)
    
    # Seção de Destaques
    destaques_titulo = models.CharField("Título dos Destaques", max_length=200, default="Participantes em Destaque")
    participantes_destaques = StreamField([
        ('participante', ParticipanteBlock()),
    ], blank=True, use_json_field=True)
    
    # Seção de Vídeo
    video_titulo = models.CharField("Título do Vídeo", max_length=200, default="Assista ao vídeo")
    video_url = models.URLField("URL do Vídeo", blank=True)
    
    # Seção de Números/Estatísticas
    numeros_stats = StreamField([
        ('stat', StatBlock()),
    ], blank=True, use_json_field=True)
    
    # Seção de Certificado
    certificado_titulo = models.CharField("Título do Certificado", max_length=200, blank=True)
    certificado_texto = RichTextField("Texto do Certificado", blank=True)
    certificado_texto_botao = models.CharField("Texto do Botão", max_length=100, default="Baixar certificado")
    certificado_imagem = StreamField([
        ('certificado_imagem', ImageBlock()),
    ], blank=True, use_json_field=True)
    
    # Seção de Galeria
    galeria_titulo = models.CharField("Título da Galeria", max_length=200, default="Galeria")
    galeria_subtitulo = models.CharField("Subtítulo da Galeria", max_length=300, blank=True)
    galeria_stream = StreamField([
        ('foto', GaleriaFotoBlock()),
    ], blank=True, use_json_field=True)
    
    # Newsletter
    newsletter_stream = StreamField([
        ('imagem', ImageBlock()),
    ], blank=True, use_json_field=True)
    
    # Footer
    footer_stream = StreamField([
        ('imagem', ImageBlock()),
    ], blank=True, use_json_field=True)

    template = 'enap_designsystem/semana_inovacao/home.html'
    
    # 🎯 CONFIGURAÇÃO FUNDAMENTAL: Permite apenas páginas filhas específicas
    subpage_types = [
        'enap_designsystem.SemanaFAQPage',
        'enap_designsystem.SemanaProgramacaoPage', 
        'enap_designsystem.SemanaParticipantesPage',
        'enap_designsystem.SemanaLocalPage',
        'enap_designsystem.SemanaPatrocinadoresPage',
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('banner_titulo'),
            FieldPanel('banner_subtitulo'),
            FieldPanel('banner_texto_botao'),
            FieldPanel('logo_hero_stream'),
            FieldPanel('logo_hero_link'),
            FieldPanel('banner_imagem'),
        ], heading="Seção Banner"),
        
        MultiFieldPanel([
            FieldPanel('destaques_titulo'),
            FieldPanel('participantes_destaques'),
        ], heading="Seção Destaques"),
        
        MultiFieldPanel([
            FieldPanel('video_titulo'),
            FieldPanel('video_url'),
        ], heading="Seção Vídeo"),
        
        MultiFieldPanel([
            FieldPanel('numeros_stats'),
        ], heading="Seção Números"),
        
        MultiFieldPanel([
            FieldPanel('certificado_titulo'),
            FieldPanel('certificado_texto'),
            FieldPanel('certificado_texto_botao'),
            FieldPanel('certificado_imagem'),
        ], heading="Seção Certificado"),
        
        MultiFieldPanel([
            FieldPanel('galeria_titulo'),
            FieldPanel('galeria_subtitulo'),
            FieldPanel('galeria_stream'),
        ], heading="Seção Galeria"),
        
        MultiFieldPanel([
            FieldPanel('newsletter_stream'),
            FieldPanel('footer_stream'),
        ], heading="Newsletter e Footer"),
    ]

    def save(self, *args, **kwargs):
        """Criar páginas filhas automaticamente quando a página for salva pela primeira vez"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.create_child_pages()

    def create_child_pages(self):
        """Criar todas as páginas filhas automaticamente"""
        from django.utils.text import slugify
        
        # Lista de páginas filhas para criar
        child_pages_data = [
            {
                'model': SemanaFAQPage,
                'title': 'Perguntas Frequentes',
                'slug': 'faq',
                'extra_data': {
                    'intro_title': 'Perguntas',
                    'intro_subtitle': 'Frequentes'
                }
            },
            {
                'model': SemanaProgramacaoPage,
                'title': 'Programação',
                'slug': 'programacao',
                'extra_data': {}
            },
            {
                'model': SemanaParticipantesPage,
                'title': 'Participantes',
                'slug': 'participantes',
                'extra_data': {
                    'subtitulo': 'SI 2024',
                    'titulo': 'Participantes'
                }
            },
            {
                'model': SemanaLocalPage,
                'title': 'O Local',
                'slug': 'local',
                'extra_data': {
                    'enap_title': 'ENAP',
                    'hospitality_title': 'Hospitalidade',
                    'directions_title': 'Como Chegar'
                }
            },
            {
                'model': SemanaPatrocinadoresPage,
                'title': 'Patrocinadores',
                'slug': 'patrocinadores',
                'extra_data': {
                    'titulo': 'Nossos Patrocinadores'
                }
            },
        ]
        
        for page_data in child_pages_data:
            # Verificar se a página já existe
            if not self.get_children().filter(slug=page_data['slug']).exists():
                # Criar nova página filha
                child_page = page_data['model'](
                    title=page_data['title'],
                    slug=page_data['slug'],
                    **page_data['extra_data']
                )
                
                # Adicionar como filha
                self.add_child(instance=child_page)
                
                # Publicar automaticamente
                child_page.save_revision().publish()

    def get_participantes_destaques(self):
        """Retorna os participantes em destaque"""
        return self.participantes_destaques
    
    def get_active_branding(self):
        """Retorna o tema de branding ativo"""
        from .models import BrandingTheme
        return BrandingTheme.objects.filter(is_active=True).first()
    
    def get_active_event_info(self):
        """Retorna as informações do evento ativo"""
        from .models import EventInfo
        return EventInfo.objects.filter(is_active=True).first()
    
    def get_active_navigation(self):
        """Retorna a configuração de navegação ativa"""  
        from .models import SemanaNavigation
        return SemanaNavigation.objects.filter(is_active=True).first()

    class Meta:
        verbose_name = "Semana de Inovação - Site Principal"
        verbose_name_plural = "Semana de Inovação - Sites"

# =============================================================================
# PÁGINAS FILHAS (SÓ PODEM SER CRIADAS COMO FILHAS DA HOME)
# =============================================================================

class SemanaFAQPage(Page):
    """Página de Perguntas Frequentes"""
    
    intro_title = models.CharField("Título de Introdução", max_length=200, default="Perguntas")
    intro_subtitle = models.CharField("Subtítulo de Introdução", max_length=200, default="Frequentes")
    
    faq_tabs = StreamField([
        ('faq_tab', FAQTabBlock()),
    ], use_json_field=True)

    template = 'enap_designsystem/semana_inovacao/faq_semana.html'
    
    # 🎯 CONFIGURAÇÃO: Só pode ser filha da SemanaHomePage
    parent_page_types = ['enap_designsystem.SemanaHomePage']
    subpage_types = []  # Não permite filhas

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('intro_title'),
            FieldPanel('intro_subtitle'),
        ], heading="Introdução"),
        
        FieldPanel('faq_tabs'),
    ]

    class Meta:
        verbose_name = "FAQ da Semana"


class SemanaProgramacaoPage(Page):
    """Página de Programação"""
    
    # Atividades organizadas por data
    atividades = StreamField([
        ('atividade', AtividadeBlock()),
    ], use_json_field=True)

    template = 'enap_designsystem/semana_inovacao/programacao_semana.html'
    
    # 🎯 CONFIGURAÇÃO: Só pode ser filha da SemanaHomePage
    parent_page_types = ['enap_designsystem.SemanaHomePage']
    subpage_types = []  # Não permite filhas

    content_panels = Page.content_panels + [
        FieldPanel('atividades'),
    ]
    
    def get_atividades_por_data(self):
        """Retorna atividades organizadas por data"""
        atividades_dict = {}
        for block in self.atividades:
            if block.block_type == 'atividade':
                data = block.value['data']
                if data not in atividades_dict:
                    atividades_dict[data] = []
                atividades_dict[data].append(block.value)
        return atividades_dict
    
    def get_atividades_online(self):
        """Retorna apenas atividades online"""
        return [block.value for block in self.atividades if block.value.get('tipo') == 'online']
    
    def get_atividades_presenciais(self):
        """Retorna apenas atividades presenciais"""
        return [block.value for block in self.atividades if block.value.get('tipo') == 'presencial']

    class Meta:
        verbose_name = "Programação da Semana"


class SemanaParticipantesPage(Page):
    """Página de Participantes"""
    
    subtitulo = models.CharField("Subtítulo", max_length=200, default="SI 2024")
    titulo = models.CharField("Título", max_length=200, default="Participantes")
    introducao = RichTextField("Introdução", blank=True)
    
    participantes_stream = StreamField([
        ('participante', ParticipanteBlock()),
    ], use_json_field=True)
    
    # Newsletter (reutilizada)
    newsletter_stream = StreamField([
        ('imagem', ImageBlock()),
    ], blank=True, use_json_field=True)
    
    # Footer (reutilizado)
    footer_stream = StreamField([
        ('imagem', ImageBlock()),
    ], blank=True, use_json_field=True)

    template = 'enap_designsystem/semana_inovacao/participantes.html'
    
    # 🎯 CONFIGURAÇÃO: Só pode ser filha da SemanaHomePage
    parent_page_types = ['enap_designsystem.SemanaHomePage']
    subpage_types = []  # Não permite filhas

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('subtitulo'),
            FieldPanel('titulo'),
            FieldPanel('introducao'),
        ], heading="Cabeçalho"),
        
        FieldPanel('participantes_stream'),
        
        MultiFieldPanel([
            FieldPanel('newsletter_stream'),
            FieldPanel('footer_stream'),
        ], heading="Newsletter e Footer"),
    ]

    class Meta:
        verbose_name = "Participantes da Semana"


class SemanaLocalPage(Page):
    """Página O Local"""
    
    # Seção ENAP
    enap_image = StreamField([
        ('imagem', ImageBlock()),
    ], blank=True, use_json_field=True)
    enap_title = models.CharField("Título ENAP", max_length=200, default="ENAP")
    enap_description = RichTextField("Descrição ENAP", blank=True)
    
    # Seção Hospitalidade
    hospitality_title = models.CharField("Título Hospitalidade", max_length=200, default="Hospitalidade")
    hospitality_cards = StreamField([
        ('card', HospitalityCardBlock()),
    ], blank=True, use_json_field=True)
    
    # Seção Como Chegar
    directions_title = models.CharField("Título Como Chegar", max_length=200, default="Como Chegar")
    
    # Transporte - Metrô
    metro_title = models.CharField("Título Metrô", max_length=100, default="Metrô")
    metro_text = models.TextField("Texto Metrô", blank=True)
    
    # Transporte - Táxi
    taxi_title = models.CharField("Título Táxi", max_length=100, default="Táxi")
    taxi_text = models.TextField("Texto Táxi", blank=True)
    
    # Transporte - Ônibus
    bus_title = models.CharField("Título Ônibus", max_length=100, default="Ônibus")
    bus_text = models.TextField("Texto Ônibus", blank=True)
    
    # Transporte - Especial
    special_title = models.CharField("Título Especial", max_length=100, default="Transporte Especial")
    special_text = models.TextField("Texto Especial", blank=True)
    
    # Mapa
    map_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    template = 'enap_designsystem/semana_inovacao/local.html'
    
    # 🎯 CONFIGURAÇÃO: Só pode ser filha da SemanaHomePage
    parent_page_types = ['enap_designsystem.SemanaHomePage']
    subpage_types = []  # Não permite filhas

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('enap_image'),
            FieldPanel('enap_title'),
            FieldPanel('enap_description'),
        ], heading="Seção ENAP"),
        
        MultiFieldPanel([
            FieldPanel('hospitality_title'),
            FieldPanel('hospitality_cards'),
        ], heading="Seção Hospitalidade"),
        
        MultiFieldPanel([
            FieldPanel('directions_title'),
        ], heading="Como Chegar"),
        
        MultiFieldPanel([
            FieldPanel('metro_title'),
            FieldPanel('metro_text'),
        ], heading="Transporte - Metrô"),
        
        MultiFieldPanel([
            FieldPanel('taxi_title'),
            FieldPanel('taxi_text'),
        ], heading="Transporte - Táxi"),
        
        MultiFieldPanel([
            FieldPanel('bus_title'),
            FieldPanel('bus_text'),
        ], heading="Transporte - Ônibus"),
        
        MultiFieldPanel([
            FieldPanel('special_title'),
            FieldPanel('special_text'),
        ], heading="Transporte Especial"),
        
        FieldPanel('map_image'),
    ]

    class Meta:
        verbose_name = "O Local da Semana"


class SemanaPatrocinadoresPage(Page):
    """Página de Patrocinadores"""
    
    titulo = models.CharField("Título", max_length=200, default="Nossos Patrocinadores")
    
    patrocinadores = StreamField([
        ('patrocinador', ImageBlock()),
    ], use_json_field=True)

    template = 'enap_designsystem/semana_inovacao/patrocinadores.html'
    
    # 🎯 CONFIGURAÇÃO: Só pode ser filha da SemanaHomePage
    parent_page_types = ['enap_designsystem.SemanaHomePage']
    subpage_types = []  # Não permite filhas

    content_panels = Page.content_panels + [
        FieldPanel('titulo'),
        FieldPanel('patrocinadores'),
    ]

    class Meta:
        verbose_name = "Patrocinadores da Semana"