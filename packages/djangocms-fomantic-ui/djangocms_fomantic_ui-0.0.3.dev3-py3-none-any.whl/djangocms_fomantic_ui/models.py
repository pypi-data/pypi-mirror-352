from cms.models import CMSPlugin, ValidationError
from django import forms
from django.apps import apps
from django.db import models
from django.templatetags.static import static
from django.utils.translation import gettext as _
from filer.fields.file import FilerFileField
from filer.fields.image import FilerImageField

# HTMLField is a custom field that allows to use a rich text editor
# Probe for djangocms_text first, then for djangocms_text_ckeditor
# and finally fallback to a simple textarea
if (
    apps.is_installed("djangocms_text")
    or apps.is_installed("djangocms_text.contrib.text_ckeditor4")
    or apps.is_installed("djangocms_text.contrib.text_ckeditor5")
    or apps.is_installed("djangocms_text.contrib.text_quill")
    or apps.is_installed("djangocms_text.contrib.text_tinymce")
):
    from djangocms_text.fields import HTMLField
elif apps.is_installed("djangocms_text_ckeditor"):
    from djangocms_text_ckeditor.fields import HTMLField
else:

    class HTMLField(models.TextField):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault("widget", forms.Textarea)
            super().__init__(*args, **kwargs)


SIZES = [
    ('mini', _('mini')),
    ('tiny', _('tiny')),
    ('small', _('small')),
    ('medium', _('medium')),
    ('large', _('large')),
    ('big', _('big')),
    ('huge', _('huge')),
    ('massive', _('massive')),
]
FLIP_AXES = [
    ('', _('none')),
    ('horizontally', _('horizontally')),
    ('vertically', _('vertically')),
]
ROTATION = [
    ('', _('none')),
    ('clockwise', _('clockwise')),
    ('counterclockwise', _('counterclockwise')),
]
COLOURS = [
    ('primary', _('Primary')),
    ('secondary', _('Secondary')),
    ('red', _('Red')),
    ('orange', _('Orange')),
    ('yellow', _('Yellow')),
    ('olive', _('Olive')),
    ('green', _('Green')),
    ('teal', _('Teal')),
    ('blue', _('Blue')),
    ('violet', _('Violet')),
    ('purple', _('Purple')),
    ('pink', _('Pink')),
    ('brown', _('Brown')),
    ('grey', _('Grey')),
    ('black', _('Black')),
]
NR_COLUMNS = [(x, x) for x in range(1, 17)]

NUMBER_TO_ENGLISH = {
    1: 'one',
    2: 'two',
    3: 'three',
    4: 'four',
    5: 'five',
    6: 'six',
    7: 'seven',
    8: 'eight',
    9: 'nine',
    10: 'ten',
    11: 'eleven',
    12: 'twelve',
    13: 'thirteen',
    14: 'fourteen',
    15: 'fifteen',
    16: 'sixteen',
}
FLOATING_DIRECTIONS = [
    ('left', _('left')),
    ('right', _('right')),
]
TEXT_ALIGNMENTS = [
    ('left', _('left')),
    ('center', _('centre')),
    ('right', _('right')),
]
TARGETS = [
    ('_self', _('_self')),
    ('_blank', _('_blank')),
    ('_parent', _('_parent')),
    ('_top', _('_top')),
]


class ColouredComponent(CMSPlugin):
    colour = models.CharField(
        blank=True,
        # default='',
        max_length=9,
        choices=COLOURS,
        verbose_name=_('colour'),
    )

    class Meta:
        abstract = True


class FloatedComponent(CMSPlugin):
    floated = models.CharField(
        blank=True, max_length=5, choices=FLOATING_DIRECTIONS
    )

    class Meta:
        abstract = True


class AlignedComponent(CMSPlugin):
    text_alignment = models.CharField(
        blank=True, max_length=6, choices=TEXT_ALIGNMENTS
    )

    class Meta:
        abstract = True

    def __str__(self):
        return _('Aligned Component')


class TabsContainerPluginModel(CMSPlugin):
    """Tabs container"""
    colour = models.CharField(
        blank=True,
        max_length=9,
        choices=COLOURS,
        default="primary",
        verbose_name=_('Background colour'),
    )
    inverted = models.BooleanField(
        default=True,
        verbose_name=_('inverted'),
        help_text=_('coloured background')
    )

    def __str__(self):
        return _('Tabs')

    def get_classes(self):
        """ CSS classes"""
        classes = ['ui top attached']
        if self.inverted:
            classes.append('inverted')
        classes.append(f'{self.colour} tabular menu')
        return ' '.join(classes)


class TabPluginModel(CMSPlugin):
    """A tab in a tab container"""
    name = models.CharField(max_length=100, verbose_name=_('name'))
    content = HTMLField(blank=True, verbose_name=_('content'))
    active = models.BooleanField(
        default=False,
        verbose_name=_('active'),
        help_text=_('Visible after page has loaded?')
    )

    def __str__(self):
        return self.name


class Accordion(CMSPlugin):
    styled = models.BooleanField(default=True)
    fluid = models.BooleanField(default=True)
    inverted = models.BooleanField(default=False)
    # Semantic UI CSS differentiates between active and hover in terms of background colour, here we don’t:
    highlighted_background_colour_choice = models.CharField(
        blank=True,
        max_length=9,
        choices=COLOURS,
        default='primary',
        verbose_name=_(
            'Background colour (CSS definition, not Semantic UI) of highlighted title (active or hover)'
        ),
    )
    highlighted_background_colour = models.CharField(
        blank=True,
        max_length=20,
        verbose_name=_('CSS compliant Colour code or name')
    )

    def __str__(self):
        return '{} {} {} accordion'.format(
            'styled' if self.styled else '',
            'fluid' if self.fluid else '',
            'inverted' if self.inverted else '',
        )

    def clean(self):
        if self.highlighted_background_colour and self.highlighted_background_colour_choice:
            raise ValidationError(
                _('Please only set either colour choice or text field.')
            )

    def get_classes(self):
        """ CSS classes"""
        classes = ['ui']
        if self.styled:
            classes.append('styled')
        if self.fluid:
            classes.append('fluid')
        if self.inverted:
            classes.append('inverted')
        classes.append('accordion')
        return ' '.join(classes)

    def get_highlighted_background_colour(self):
        return self.highlighted_background_colour or self.highlighted_background_colour_choice


class AccordionSection(CMSPlugin):
    # section = models.ForeignKey(AccordionSection, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name=_('name'))
    content = HTMLField(blank=True, verbose_name=_('content'))
    active = models.BooleanField(
        default=False,
        verbose_name=_('active'),
        help_text=_('Visible after page has loaded?')
    )

    def __str__(self):
        return self.title

    def get_classes(self):
        """ CSS classes"""
        classes = []
        if self.active:
            classes.append('active')
        classes.append('title')
        return ' '.join(classes)


class CardsContainerPluginModel(CMSPlugin):
    def __str__(self):
        return _('Cards')


class Card(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('name'))
    content = HTMLField(blank=True, verbose_name=_('content'))

    def __str__(self):
        return self.name


class CardPluginModel(CMSPlugin):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)

    def __str__(self):
        return self.card.name


class Icon(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Semantic UI icon name',
        help_text='See https://semantic-ui.com/elements/icon.html'
    )
    disabled = models.BooleanField(default=False, verbose_name=_('disabled'))
    loading = models.BooleanField(default=False, verbose_name=_('loading'))
    fitted = models.BooleanField(default=False, verbose_name=_('fitted'))
    size = models.CharField(
        max_length=7, blank=True, choices=SIZES, verbose_name=_('size')
    )
    link = models.BooleanField(default=False, verbose_name=_('link'))
    flipped = models.CharField(
        max_length=12, blank=True, choices=FLIP_AXES, verbose_name=_('flipped')
    )
    rotated = models.CharField(
        max_length=17, blank=True, choices=ROTATION, verbose_name=_('rotated')
    )
    circular = models.BooleanField(default=False, verbose_name=_('circular'))
    bordered = models.BooleanField(default=False, verbose_name=_('bordered'))
    colour = models.CharField(
        max_length=9, blank=True, choices=COLOURS, verbose_name=_('colour')
    )

    def __str__(self):
        return '{} {} {} {} {} {} {} {} {} {}'.format(
            'disabled' if self.disabled else '',
            'loading' if self.disabled else '',
            'fitted' if self.disabled else '', self.size,
            'link' if self.link else '',
            f'{self.flipped} flipped' if self.flipped else '',
            f'{self.rotated} rotated' if self.rotated else '',
            'circular' if self.circular else '', self.colour, self.name
        )


class IconPluginModel(CMSPlugin):
    icon = models.ForeignKey(Icon, on_delete=models.CASCADE)

    def __str__(self):
        return self.icon.name


class StepsContainerModel(CMSPlugin):
    ATTACHMENTS = [
        ('', _('none')),
        ('top', _('top')),
        ('bottom', _('bottom')),
    ]
    ordered = models.BooleanField(default=False, verbose_name=_('ordered'))
    vertical = models.BooleanField(default=False, verbose_name=_('vertical'))
    stackable = models.BooleanField(default=False, verbose_name=_('stackable'))
    tablet_stackable = models.BooleanField(
        default=False, verbose_name=_('tablet stackable')
    )
    unstackable = models.BooleanField(
        default=False, verbose_name=_('unstackable')
    )
    fluid = models.BooleanField(default=False, verbose_name=_('fluid'))
    attached = models.CharField(max_length=6, blank=True, choices=ATTACHMENTS)
    size = models.CharField(
        max_length=7, blank=True, choices=SIZES, verbose_name=_('size')
    )

    def __str__(self):
        return self.get_classes()

    def get_classes(self):
        """ CSS classes"""
        classes = ['ui']
        if self.ordered:
            classes.append('ordered')
        if self.vertical:
            classes.append('vertical')
        if self.stackable:
            classes.append('stackable')
        if self.tablet_stackable:
            classes.append('tablet stackable')
        if self.unstackable:
            classes.append('unstackable')
        if self.fluid:
            classes.append('fluid')
        if self.attached:
            classes.append(f'{self.attached} attached')
        if self.size:
            classes.append(self.size)
        classes.append('steps')
        return ' '.join(classes)


class StepModel(CMSPlugin):
    icon_name = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='Semantic UI icon name',
        help_text='See https://semantic-ui.com/elements/icon.html'
    )
    title = models.CharField(blank=True, max_length=50, verbose_name=_('title'))
    description = models.CharField(
        blank=True, max_length=200, verbose_name=_('description')
    )
    link = models.URLField(blank=True, default='')
    active = models.BooleanField(default=False, verbose_name=_('active'))
    completed = models.BooleanField(default=False, verbose_name=_('completed'))
    disabled = models.BooleanField(default=False, verbose_name=_('disabled'))
    tab_text = HTMLField(blank=True, default='')

    def __str__(self):
        return f'{self.icon_name} {self.title}'

    def get_classes(self):
        classes = ['ui']
        if self.active:
            classes.append('active')
        if self.completed:
            classes.append('completed')
        if self.disabled:
            classes.append('disabled')
        classes.append('step')
        return ' '.join(classes)

    def get_on_click(self):
        if self.tab_text:
            return f'onclick="show(\'#step-{self.id}\')"'
        else:
            return ''

    def get_opening_tag(self):
        if self.link:
            return '<a id="step-{}" href="{}" class="{}" {} title="{}">'.format(
                self.id, self.link, self.get_classes(), self.get_on_click(),
                _('Click to open link')
            )
        else:
            return '<div id="step-{}" class="{}" {} title="{}">'.format(
                self.id, self.get_classes(), self.get_on_click(),
                _('Click to see this text section')
            )

    def get_closing_tag(self):
        if self.link:
            return '</a>'
        else:
            return '</div>'


class Embed(CMSPlugin):
    SOURCES = [
        ('youtube', 'Youtube'),
        ('vimeo', 'Vimeo'),
        ('', _('custom')),
    ]
    LENGTH_UNITS = [('%', '%'), ('px', 'px')]
    title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('title'),
        help_text=_('Currently only displayed for editors. ')
    )
    source = models.CharField(
        max_length=7,
        blank=True,
        choices=SOURCES,
        default='youtube',
        verbose_name=_('source')
    )
    medium_id = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('medium id'),
        help_text=_('id of Youtube or Vimeo video')
    )
    hash = models.CharField(
        blank=True,
        max_length=10,
        verbose_name=_('hash'),
        help_text=_('Hash for Vimeo, 10 hex digits after “h=”')
    )
    external_url = models.URLField(
        blank=True,
        verbose_name=_('URL to be embedded'),
        help_text=_('Fill in unless you choose a predefined data source.')
    )
    placeholder_image = FilerImageField(
        null=True,
        blank=True,
        related_name='placeholder_image_embed',
        on_delete=models.CASCADE,
        verbose_name=_('placeholder image')
    )
    use_placeholder = models.BooleanField(
        default=True,
        verbose_name=_(
            'Show placeholder image instead of loading code immediately'
        ),
        help_text=_(
            'A placeholder image is shown until users click on it to load the code.'
        )
    )
    video_file = FilerFileField(
        null=True,
        blank=True,
        related_name='video_file_embed',
        on_delete=models.CASCADE,
        verbose_name=_('video file'),
        help_text=_(
            'You can upload a video file instead of linking an external resource'
        )
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('play icon'),
        help_text=_(
            'Choose name from https://semantic-ui.com/elements/icon.html or '
            'leave empty for standard play circle icon.'
        )
    )
    width_value = models.PositiveSmallIntegerField(
        null=True, blank=True, default=640, verbose_name=_('width')
    )
    width_unit = models.CharField(
        max_length=2, choices=LENGTH_UNITS, default='px'
    )
    height_value = models.PositiveSmallIntegerField(
        null=True, blank=True, default=360, verbose_name=_('height')
    )
    height_unit = models.CharField(
        max_length=2, choices=LENGTH_UNITS, default='px'
    )

    def __str__(self):
        if self.source:
            if self.title:
                return f'{self.get_source_display()} {self.title}'
            else:
                return f'{self.get_source_display()} {self.medium_id}'
        else:
            if self.title:
                return self.title
            else:
                return self.url

    @property
    def width(self):
        if self.width_value:
            return f'{self.width_value}{self.width_unit}'
        else:
            return ''

    @property
    def height(self):
        if self.height_value:
            return f'{self.height_value}{self.height_unit}'
        else:
            return ''

    @property
    def url(self):
        if self.video_file:
            return self.video_file.url
        else:
            return self.external_url

    def get_placeholder_image_url(self):
        if self.placeholder_image:
            return self.placeholder_image.url
        else:
            return static(
                'djangocms_fomantic_ui/images/Stellaris_Clapper-board.svg'
            )

    def get_style(self):
        styles = []
        if self.width:
            styles.append(f'width: {self.width};')
        if self.height:
            styles.append(f'height: {self.height};')
        return ' '.join(styles)

    def clean(self):
        # TODO: Adopt more and check for video file
        if self.medium_id == '' and self.url == '' and self.video_file is None:
            raise ValidationError(
                _('Either medium id or url or video file must tbe defined.')
            )
        elif self.medium_id == '' and self.url != '':
            self.source = ''  # custom url
        elif self.medium_id != '' and self.url != '':
            raise ValidationError(
                _('You can’t specify both medium id and url.')
            )
        if self.source == '' and self.url == '':
            raise ValidationError(
                _('For a custom source you must specify a URL.')
            )
        if self.source == '' and self.medium_id != '':
            raise ValidationError(
                _(
                    'For a custom source you must specify a URL, but no medium id.'
                )
            )
        if self.source == 'vimeo' and self.hash == '':
            raise ValidationError(_('Vimeo videos require a hash.'))
        if self.placeholder_image and not self.use_placeholder:
            raise ValidationError(
                _(
                    'When a placeholder image is chosen, “Show placeholder image…” must be checked.'
                )
            )


class Reveal(CMSPlugin):
    EFFECTS = [
        ('fade', _('fade')),
        ('move', _('move left')),
        ('move right', _('move right')),
        ('move up', _('move up')),
        ('move down', _('move down')),
        ('circular rotate', _('circular rotate right')),
        ('circular rotate left', _('circular rotate left')),
    ]
    visible_image = FilerImageField(
        null=True,  # temporarily
        related_name='visible_image_reveal',
        on_delete=models.CASCADE,
        verbose_name=_('visible image'),
        help_text=_('Image is visible after loading.')
    )
    hidden_image = FilerImageField(
        null=True,  # temporarily
        related_name='hidden_image_reveal',
        on_delete=models.CASCADE,
        verbose_name=_('hidden image'),
        help_text=_(
            'Image is hidden after loading and becomes visible after hovering.'
        )
    )
    image_size = models.CharField(
        blank=True,
        max_length=7,
        choices=SIZES,
        default='medium',
        verbose_name=_('size')
    )
    effect = models.CharField(
        max_length=20,
        choices=EFFECTS,
        default='fade',
        verbose_name=_('effect')
    )

    def __str__(self):
        return f'{self.visible_image} {self.effect} → {self.hidden_image}'


class Grid(CMSPlugin):
    nr_columns = models.PositiveSmallIntegerField(
        choices=NR_COLUMNS,
        null=True,
        blank=True,
        default=None,
        verbose_name=_('number of grid columns'),
        help_text=_(
            'Number of grid columns, usually you should leave this blank for getting a standard grid.'
        )
    )
    DIVIDED_OPTIONS = [
        ('divided', _('horizontally divided')),
        ('vertically divided', _('vertically divided')),
    ]
    divided = models.CharField(
        blank=True,
        default='',
        max_length=18,
        choices=DIVIDED_OPTIONS,
        verbose_name=_('divided'),
        help_text=_(
            'Horizontally divided: dividers between columns, requires rows; vertically divided: '
            'dividers between rows.'
        )
    )
    CELLED_OPTIONS = [
        ('celled', _('celled')), ('internally celled', _('internally celled'))
    ]
    celled = models.CharField(
        blank=True,
        max_length=17,
        default='',
        choices=CELLED_OPTIONS,
        verbose_name=_('celled'),
    )
    padded = models.BooleanField(default=False, verbose_name=_('padded'))
    relaxed = models.BooleanField(default=False, verbose_name=_('relaxed'))
    stackable = models.BooleanField(default=True, verbose_name=_('stackable'))
    text_alignment = models.CharField(
        blank=True, default='', max_length=6, choices=TEXT_ALIGNMENTS
    )
    equal_width = models.BooleanField(
        default=False, verbose_name=_('equal width')
    )
    centered = models.BooleanField(default=False, verbose_name=_('centered'))
    container = models.BooleanField(default=False, verbose_name=_('container'))

    class Meta:
        verbose_name = _('grid')

    def __str__(self):
        return self.get_classes()

    def get_classes(self):
        classes = ['ui']
        if self.divided:
            classes.append(self.divided)
        if self.celled:
            classes.append(self.celled)
        if self.padded:
            classes.append('padded')
        if self.relaxed:
            classes.append('relaxed')
        if self.text_alignment:
            classes.append(self.text_alignment)
        if self.stackable:
            classes.append('stackable')
        if self.equal_width:
            classes.append('equal width')
        if self.centered:
            classes.append('centered')
        if self.nr_columns:
            classes.append(f'{NUMBER_TO_ENGLISH[self.nr_columns]} column')
        classes.append('grid')
        if self.container:
            classes.append('container')
        return ' '.join(classes)


class Row(CMSPlugin):
    nr_columns = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=NR_COLUMNS,
        default=None,
        verbose_name=_('number of grid columns'),
        help_text=_(
            'Number of grid column units, Actual number of columns can be smaller.'
        )
    )
    stretched = models.BooleanField(
        default=False,
        verbose_name=_('stretched'),
        help_text=_(
            'A row can stretch its contents to take up the entire column height'
        )
    )
    colour = models.CharField(
        blank=True,
        default='',
        max_length=9,
        choices=COLOURS,
        verbose_name=_('colour'),
        help_text=_('only with padded grid')
    )
    text_alignment = models.CharField(
        blank=True, default='', max_length=6, choices=TEXT_ALIGNMENTS
    )
    doubling = models.BooleanField(default=False, verbose_name=_('doubling'))

    class Meta:
        verbose_name = _('row')

    def __str__(self):
        return ''  # self.get_classes()

    def get_classes(self):
        classes = []
        if self.nr_columns:
            classes.append(f'{NUMBER_TO_ENGLISH[self.nr_columns]} column')
        if self.colour:
            classes.append(self.colour)
        if self.text_alignment:
            classes.append(f'{self.text_alignment} aligned')
        if self.doubling:
            classes.append('doubling')
        classes.append('row')
        return ' '.join(classes)


class Column(CMSPlugin):
    width = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=NR_COLUMNS,
        default=None,
        verbose_name=_('column width'),
        help_text=_(
            'number of grid units for this column, eg. 4 out of 12 for one third.'
        )
    )
    colour = models.CharField(
        blank=True,
        default='',
        max_length=9,
        choices=COLOURS,
        verbose_name=_('colour'),
        help_text=_('only with padded grid')
    )
    floated = models.CharField(
        blank=True, default='', max_length=5, choices=FLOATING_DIRECTIONS
    )
    text_alignment = models.CharField(
        blank=True, default='', max_length=6, choices=TEXT_ALIGNMENTS
    )
    no_padding = models.BooleanField(
        default=False, verbose_name=_('no padding')
    )
    hide_on_mobile = models.BooleanField(
        default=False, verbose_name=_('Hide on mobile devices')
    )

    def __str__(self):
        return self.get_classes()

    def get_classes(self):
        classes = []
        if self.colour:
            classes.append(self.colour)
        if self.floated:
            classes.append(f'{self.floated} floated')
        if self.text_alignment:
            classes.append(f'{self.text_alignment} aligned')
        if self.width:
            classes.append(f'{NUMBER_TO_ENGLISH[self.width]} wide')
        if self.hide_on_mobile:
            classes.append('computer only')
        classes.append('column')
        return ' '.join(classes)

    def get_style(self):
        if self.no_padding:
            return 'padding: 0;'
        else:
            return ''

    class Meta:
        verbose_name = _('column')


class Segment(ColouredComponent):  # , FloatedComponent, AlignedComponent
    raised = models.BooleanField(
        default=False,
        verbose_name=_('raised'),
        help_text=_('A segment may be formatted to raise above the page.')
    )
    stacked = models.BooleanField(
        default=False,
        verbose_name=_('stacked'),
        help_text=_(
            'A segment can be formatted to show it contains multiple pages.'
        )
    )
    piled = models.BooleanField(
        default=False,
        verbose_name=_('piled'),
        help_text=_('A segment can be formatted to look like a pile of pages')
    )
    vertical = models.BooleanField(
        default=False,
        verbose_name=_('vertical'),
        help_text=_(
            'A vertical segment formats content to be aligned as part of a vertical group.'
        )
    )
    disabled = models.BooleanField(
        default=False,
        verbose_name=_('disabled'),
        help_text=_('A segment may show its content is disabled.')
    )
    loading = models.BooleanField(
        default=False,
        verbose_name=_('loading'),
        help_text=_('A segment may show its content is being loaded.')
    )
    inverted = models.BooleanField(
        default=False,
        verbose_name=_('inverted'),
        help_text=_('A segment can have its colours inverted for contrast.')
    )
    ATTACHED_OPTIONS = [
        ('top attached', _('top attached')),
        ('attached', _('attached')),
        ('bottom attached', _('bottom attached')),
    ]
    attached = models.CharField(
        blank=True,
        # default='',
        max_length=15,
        choices=ATTACHED_OPTIONS,
        verbose_name=_('attached'),
    )
    padded = models.BooleanField(
        default=False, verbose_name=_('stacked'), help_text=_('padded')
    )
    compact = models.BooleanField(
        default=False,
        verbose_name=_('compact'),
    )

    inverted = models.BooleanField(
        default=False,
        verbose_name=_('inverted'),
    )
    EMPHASIS_OPTIONS = [
        ('secondary', _('secondary')), ('tertiary', _('tertiary'))
    ]
    emphasis = models.CharField(
        blank=True,
        max_length=9,
        choices=EMPHASIS_OPTIONS,
        verbose_name=_('emphasis'),
    )
    circular = models.BooleanField(
        default=False,
        verbose_name=_('circular'),
    )
    clearing = models.BooleanField(
        default=False,
        verbose_name=_('clearing'),
        help_text=_('clear floated content')
    )
    floated = models.CharField(
        blank=True, max_length=5, choices=FLOATING_DIRECTIONS
    )
    text_alignment = models.CharField(
        blank=True,
        # default='',
        max_length=6,
        choices=TEXT_ALIGNMENTS
    )
    basic = models.BooleanField(
        default=False, verbose_name=_('stacked'), help_text=_('basic')
    )

    def __str__(self):
        return ''  # self.get_classes()

    def get_classes(self):
        classes = ['ui segment']
        if self.raised:
            classes.append('raised')
        if self.stacked:
            classes.append('stacked')
        if self.piled:
            classes.append('piled')
        if self.vertical:
            classes.append('vertical')
        if self.disabled:
            classes.append('disabled')
        if self.loading:
            classes.append('loading')
        if self.inverted:
            classes.append('inverted')
        if self.attached:
            classes.append(self.attached)
        if self.padded:
            classes.append('padded')
        if self.compact:
            classes.append('compact')
        if self.colour:
            classes.append(self.colour)
        if self.emphasis:
            classes.append(self.emphasis)
        if self.circular:
            classes.append('circular')
        if self.clearing:
            classes.append('clearing')
        if self.floated:
            classes.append(f'{self.floated} floated')
        if self.text_alignment:
            classes.append(f'{self.text_alignment} aligned')
        if self.basic:
            classes.append('basic')
        return ' '.join(classes)


class Message(CMSPlugin):
    header = models.CharField(
        blank=True, max_length=100, verbose_name=_('name')
    )
    icon_name = models.CharField(
        blank=True,
        max_length=50,
        verbose_name='Semantic UI icon name',
        help_text='See https://semantic-ui.com/elements/icon.html'
    )
    dismissable = models.BooleanField(
        default=False,
        verbose_name=_('dismissable'),
        help_text=_('Can be closed by the user.')
    )
    hidden = models.BooleanField(default=False, verbose_name=_('hidden'))
    visible = models.BooleanField(default=False, verbose_name=_('visible'))
    floating = models.BooleanField(default=False, verbose_name=_('floating'))
    compact = models.BooleanField(default=False, verbose_name=_('compact'))
    attached = models.BooleanField(default=False, verbose_name=_('attached'))
    TYPES = [
        ('warning', _('Warning')),
        ('info', _('Info')),
        ('positive', _('Positive')),
        ('success', _('Success')),
        ('negative', _('Negative')),
        ('error', _('Error')),
    ]
    MESSAGE_COLOURS = COLOURS.copy()
    MESSAGE_COLOURS.extend(TYPES)
    colour = models.CharField(
        blank=True,
        default='',
        max_length=9,
        choices=MESSAGE_COLOURS,
        verbose_name=_('colour'),
    )
    size = models.CharField(
        max_length=7, blank=True, choices=SIZES, verbose_name=_('size')
    )
    content = HTMLField(blank=True, verbose_name=_('content'))

    def __str__(self):
        return self.get_classes()

    def get_classes(self):
        classes = ['ui']
        if self.colour:
            classes.append(self.colour)
        if self.dismissable:
            classes.append('dismissable')
        if self.hidden:
            classes.append('hidden')
        if self.visible:
            classes.append('visible')
        if self.floating:
            classes.append('floating')
        if self.compact:
            classes.append('compact')
        if self.attached:
            classes.append('attached')
        # if self.type:
        # 	classes.append(self.type)
        if self.icon_name:
            classes.append('icon')
        if self.size:
            classes.append(self.size)
        classes.append('message')
        return ' '.join(classes)


class Container(CMSPlugin):
    def __str__(self):
        return ''

    def get_classes(self):
        return 'ui container'


BACKGROUND_COLOURS = [
    ('#FFFFFF', 'White'), ('#F0F8FF', 'AliceBlue'), ('#F0FFFF', 'Azure'),
    ('#F5F5DC', 'Beige'), ('#FFF8DC', 'Cornsilk '), ('#FFFAF0', 'FloralWhite'),
    ('#D3D3D3', 'LightGrey'), ('#FFFAFA', 'Snow'), ('#F5F5F5', 'WhiteSmoke'),
    ('#f5f6f8', '#f5f6f8')
]


class Div(CMSPlugin):
    """HTML div with background colour"""

    background_colour_text = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Background colour name or value'),
        help_text=_('In CSS notation like "#789abc88" or decimal')
    )
    background_colour_choice = models.CharField(
        max_length=9,
        blank=True,
        choices=BACKGROUND_COLOURS,
        verbose_name=_('or choose'),
        help_text=_('Here are some predefined colours.')
    )

    def __str__(self):
        return f'{self.get_background_colour_name()}'

    def clean(self):
        if self.background_colour_text and self.background_colour_choice:
            raise ValidationError(
                _(
                    'Please either fill in a value or choose a predefined colour, not both.'
                )
            )

    @property
    def background_colour(self):
        return self.background_colour_text or self.background_colour_choice

    def get_background_colour_name(self):
        return self.background_colour_text or self.get_background_colour_choice_display(
        ) or ''

    def get_classes(self):
        return ''


class DivContainer(Div):
    """HTML div with background colour with container inside"""
    pass


class Button(CMSPlugin):
    text = models.CharField(blank=True, max_length=50)
    link = models.URLField(blank=True)
    target = models.CharField(blank=True, max_length=7, choices=TARGETS)
    BUTTON_COLOURS = COLOURS.copy()
    PRIMARY_SECONDARY = [
        ('primary', _('Primary')),
        ('secondary', _('Secondary')),
    ]
    SOCIAL = [
        ('facebook', _('Facebook')),
        ('twitter', _('Twitter')),
        ('google', _('Google')),
        ('vk', _('VK')),
        ('linkedin', _('Linkedin')),
        ('instagram', _('Instagram')),
        ('youtube', _('Youtube')),
    ]
    BUTTON_COLOURS.extend(PRIMARY_SECONDARY)
    BUTTON_COLOURS.extend(SOCIAL)
    colour = models.CharField(
        blank=True,
        default='',
        max_length=9,
        choices=COLOURS,
        verbose_name=_('colour'),
    )
    visible_content = models.CharField(
        blank=True, max_length=50, verbose_name=_('Visible content')
    )  # TODO icon
    hidden_content = models.CharField(
        blank=True, max_length=50, verbose_name=_('Hidden content')
    )  # dito
    # TODO: label maybe as child plugin
    basic = models.BooleanField(verbose_name=_('Basic'))
    inverted = models.BooleanField(verbose_name=_('Inverted'))
    # TODO buttons group, groups of icons, conditionals
    STATES = [
        ('active', _('Active')),
        ('disabled', _('Disabled')),
        ('loading', _('Loading')),
    ]
    state = models.CharField(blank=True, max_length=8, choices=STATES)
    size = models.CharField(
        max_length=7, blank=True, choices=SIZES, verbose_name=_('size')
    )

    def __str__(self):
        return f'{self.get_classes()} {self.text}'

    def get_classes(self):
        classes = ['ui']
        if self.size:
            classes.append(self.size)
        if self.colour:
            classes.append(self.colour)
        if self.visible_content or self.hidden_content:
            classes.append('animated')
        if self.state:
            classes.append(self.state)
        if self.basic:
            classes.append('basic')
        if self.inverted:
            classes.append('inverted')
        if self.state:
            classes.append(self.state)
        classes.append('button')
        return ' '.join(classes)


class Buttons(CMSPlugin):
    icon_buttons = models.BooleanField(verbose_name=_('Icon buttons'))

    def __str__(self):
        return self.get_classes()

    def get_classes(self):
        classes = ['ui']
        if self.icon_buttons:
            classes.append('icon')
        classes.append('buttons')


class Statistic(ColouredComponent):
    value_int = models.IntegerField(
        null=True, blank=True, verbose_name=_('Value as integer')
    )
    value_float = models.FloatField(
        null=True, blank=True, verbose_name=_('Value as floating number')
    )
    value_text = models.CharField(
        blank=True, max_length=50, verbose_name=_('Value as text')
    )
    label = models.CharField(max_length=50, verbose_name=_('Label'))
    horizontal = models.BooleanField(verbose_name=_('Horizontal'))
    inverted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.get_value()} {self.label}'

    def get_value(self):
        return self.value_int or self.value_float or self.value_text

    def get_classes(self):
        classes = ['ui']
        if self.horizontal:
            classes.append('horizontal')
        if self.colour:
            classes.append(self.colour)
        if self.inverted:
            classes.append('inverted')
        classes.append('statistic')
        return ' '.join(classes)

    def clean(self):
        if self.value_int and self.value_float or self.value_int and self.value_text or \
                self.value_float and self.value_text:
            raise ValidationError(
                'Please specify either Value as integer, as float or as text!'
            )


class Statistics(CMSPlugin):
    horizontal = models.BooleanField(
        default=False, verbose_name=_('horizontal')
    )

    def __str__(self):
        return self.get_classes()

    def get_classes(self):
        classes = ['ui']
        if self.horizontal:
            classes.append('horizontal')
        classes.append('statistics')
        return ' '.join(classes)
