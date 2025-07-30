# semana_blocks.py - Blocks da Semana de Inovação
from django.db import models
from wagtail.blocks import (
    CharBlock, TextBlock, RichTextBlock, URLBlock, 
    StructBlock, ListBlock, BooleanBlock, IntegerBlock, 
    DateBlock, EmailBlock
)
from wagtail.images.blocks import ImageChooserBlock


# =============================================================================
# BLOCKS REUTILIZÁVEIS DA SEMANA DE INOVAÇÃO
# =============================================================================

class ImageBlock(StructBlock):
    """Block simples de imagem"""
    imagem = ImageChooserBlock(label="Imagem")
    alt_text = CharBlock(label="Texto Alternativo", required=False)

    class Meta:
        template = 'enap_designsystem/semana_inovacao/image_block.html'
        icon = 'image'
        label = 'Imagem'


class ParticipanteBlock(StructBlock):
    """Block de participante individual"""
    nome = CharBlock(label="Nome Completo")
    cargo = CharBlock(label="Cargo/Função", required=False)
    empresa = CharBlock(label="Empresa/Organização", required=False)
    foto = ImageChooserBlock(label="Foto do Participante")
    descricao = RichTextBlock(label="Biografia", required=False)
    
    # Redes sociais
    link_linkedin = URLBlock(label="LinkedIn", required=False)
    link_instagram = URLBlock(label="Instagram", required=False)
    link_twitter = URLBlock(label="Twitter/X", required=False)

    class Meta:
        template = 'enap_designsystem/semana_inovacao/participantes.html'
        icon = 'user'
        label = 'Participante'


class StatBlock(StructBlock):
    """Block para estatísticas/números"""
    valor = CharBlock(label="Valor", help_text="Ex: 129, 500+")
    descricao = CharBlock(label="Descrição", help_text="Ex: Atividades, Participantes")

    class Meta:
        template = 'enap_designsystem/semana_inovacao/stat_block.html'
        icon = 'plus'
        label = 'Estatística'


class GaleriaFotoBlock(StructBlock):
    """Block para foto da galeria"""
    imagem = ImageChooserBlock(label="Imagem")
    descricao = CharBlock(label="Descrição", required=False)

    class Meta:
        template = 'enap_designsystem/semana_inovacao/galeria_foto_block.html'
        icon = 'image'
        label = 'Foto da Galeria'


class FAQItemBlock(StructBlock):
    """Item individual de FAQ"""
    question = CharBlock(label="Pergunta")
    answer = RichTextBlock(label="Resposta")

    class Meta:
        template = 'enap_designsystem/semana_inovacao/faq_item_block.html'
        icon = 'help'
        label = 'Item FAQ'


class FAQTabBlock(StructBlock):
    """Aba de FAQ com múltiplos itens"""
    tab_name = CharBlock(label="Nome da Aba")
    faq_items = ListBlock(FAQItemBlock(), label="Itens do FAQ")

    class Meta:
        template = 'enap_designsystem/semana_inovacao/faq_tab_block.html'
        icon = 'folder-open-1'
        label = 'Aba FAQ'


class AtividadeBlock(StructBlock):
    """Block para atividade da programação"""
    horario_inicio = CharBlock(label="Horário de Início", help_text="Ex: 09:00")
    horario_fim = CharBlock(label="Horário de Fim", help_text="Ex: 10:00")
    titulo = CharBlock(label="Título da Atividade")
    descricao = TextBlock(label="Descrição", required=False)
    
    # Tipo de atividade
    TIPO_CHOICES = [
        ('online', 'Online'),
        ('presencial', 'Presencial'),
    ]
    tipo = CharBlock(label="Tipo", help_text="Digite: online ou presencial")
    
    # Local (para presencial) ou tag (para online)
    local_tag = CharBlock(label="Local/Tag", help_text="Ex: Sala 106, On-Line")
    
    # Data da atividade
    data = DateBlock(label="Data da Atividade")

    class Meta:
        template = 'enap_designsystem/semana_inovacao/atividade_block.html'
        icon = 'time'
        label = 'Atividade'


class HospitalityCardBlock(StructBlock):
    """Card de hospitalidade/serviços"""
    title = CharBlock(label="Título")
    text = RichTextBlock(label="Texto")
    image = ImageChooserBlock(label="Imagem")

    class Meta:
        template = 'enap_designsystem/semana_inovacao/hospitality_card_block.html'
        icon = 'home'
        label = 'Card de Hospitalidade'


class VideoBlock(StructBlock):
    """Block para vídeo"""
    titulo = CharBlock(label="Título do Vídeo")
    video_url = URLBlock(label="URL do Vídeo")
    descricao = TextBlock(label="Descrição", required=False)

    class Meta:
        template = 'enap_designsystem/semana_inovacao/video_block.html'
        icon = 'media'
        label = 'Vídeo'


class CertificadoBlock(StructBlock):
    """Block para seção de certificado"""
    titulo = CharBlock(label="Título")
    texto = RichTextBlock(label="Texto")
    texto_botao = CharBlock(label="Texto do Botão", default="Baixar certificado")
    imagem = ImageChooserBlock(label="Imagem do Certificado")

    class Meta:
        template = 'enap_designsystem/semana_inovacao/certificado_block.html'
        icon = 'doc-full'
        label = 'Certificado'


class NewsletterBlock(StructBlock):
    """Block para newsletter"""
    titulo = CharBlock(label="Título", default="ASSINE NOSSA NEWSLETTER")
    texto = RichTextBlock(label="Texto")
    imagem = ImageChooserBlock(label="Imagem", required=False)

    class Meta:
        template = 'enap_designsystem/semana_inovacao/newsletter_block.html'
        icon = 'mail'
        label = 'Newsletter'


class ContatoBlock(StructBlock):
    """Block para seção de contato"""
    titulo = CharBlock(label="Título", default="FALE CONOSCO")
    texto = RichTextBlock(label="Texto")

    class Meta:
        template = 'enap_designsystem/semana_inovacao/contato_block.html'
        icon = 'mail'
        label = 'Contato'


class FooterBlock(StructBlock):
    """Block para footer"""
    logo = ImageChooserBlock(label="Logo")
    texto_evento = RichTextBlock(label="Texto do Evento")
    logo_hero_link = URLBlock(label="Link do Logo", required=False)

    class Meta:
        template = 'enap_designsystem/semana_inovacao/footer_block.html'
        icon = 'list-ul'
        label = 'Footer'