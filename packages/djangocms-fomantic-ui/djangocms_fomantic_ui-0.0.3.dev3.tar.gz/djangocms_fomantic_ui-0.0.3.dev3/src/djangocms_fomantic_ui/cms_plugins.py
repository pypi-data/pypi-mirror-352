from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.conf import settings
from django.utils.translation import gettext as _

from .models import (
    Accordion,
    AccordionSection,
    Button,
    Buttons,
    CardPluginModel,
    CardsContainerPluginModel,
    Column,
    Container,
    Div,
    Embed,
    Grid,
    IconPluginModel,
    Message,
    Reveal,
    Row,
    Segment,
    Statistic,
    Statistics,
    StepModel,
    StepsContainerModel,
    TabPluginModel,
    TabsContainerPluginModel,
)


@plugin_pool.register_plugin
class TabsContainerPluginModelPublisher(CMSPluginBase):
    model = TabsContainerPluginModel

    module = _('Fomantic UI')
    name = _('Tabs')  # name of the plugin in the interface
    render_template = 'djangocms_fomantic_ui/tabs.html'

    allow_children = True
    child_classes = ['TabPluginPublisher']

    def render(self, context, instance, placeholder):
        # context.update({'instance': instance})
        context = super().render(context, instance, placeholder)
        return context


@plugin_pool.register_plugin
class TabPluginPublisher(CMSPluginBase):
    model = TabPluginModel

    module = _('Fomantic UI')
    name = _('Tab')  # name of the plugin in the interface
    render_template = 'djangocms_fomantic_ui/tab.html'

    require_parent = True
    parent_classes = ['TabsContainerPluginModelPublisher']
    allow_children = True

    def render(self, context, instance, placeholder):
        # context.update({'instance': instance}) # alt?
        context = super().render(context, instance, placeholder)  # neu?
        return context


@plugin_pool.register_plugin
class AccordionPluginModelPublisher(CMSPluginBase):
    model = Accordion

    module = _('Fomantic UI')
    name = _('Accordion')  # name of the plugin in the interface
    render_template = 'djangocms_fomantic_ui/accordion.html'

    allow_children = True
    child_classes = ['AccordionSectionPluginPublisher']

    def render(self, context, instance, placeholder):
        # context.update({'instance': instance})
        context = super().render(context, instance, placeholder)
        return context


@plugin_pool.register_plugin
class AccordionSectionPluginPublisher(CMSPluginBase):
    model = AccordionSection

    module = _('Fomantic UI')
    name = _('Accordion Section')  # name of the plugin in the interface
    render_template = 'djangocms_fomantic_ui/accordion_section.html'

    require_parent = True
    parent_classes = ['AccordionPluginModelPublisher']
    allow_children = True

    def render(self, context, instance, placeholder):
        # context.update({'instance': instance})
        context = super().render(context, instance, placeholder)
        return context


@plugin_pool.register_plugin
class CardsContainerPluginModelPublisher(CMSPluginBase):
    model = CardsContainerPluginModel

    module = _('Fomantic UI')
    name = _('Cards')  # name of the plugin in the interface
    render_template = 'djangocms_fomantic_ui/cards.html'

    allow_children = True
    child_classes = ['CardPluginPublisher', 'EmployeePublisher']

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context


@plugin_pool.register_plugin
class CardPluginPublisher(CMSPluginBase):
    model = CardPluginModel

    module = _('Fomantic UI')
    name = _('Card')  # name of the plugin in the interface
    render_template = 'djangocms_fomantic_ui/card.html'

    require_parent = True
    parent_classes = ['CardsContainerPluginModelPublisher']

    def render(self, context, instance, placeholder):
        # context.update({'instance': instance})
        context = super().render(context, instance, placeholder)
        return context


@plugin_pool.register_plugin
class IconPluginPublisher(CMSPluginBase):
    model = IconPluginModel
    text_enabled = True
    module = _('Fomantic UI')
    name = _('Icon')  # name of the plugin in the interface
    render_template = 'djangocms_fomantic_ui/icon.html'

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        # context = super(IconPluginPublisher, self).render(context, instance, placeholder)
        return context

    def icon_src(self, instance):
        return settings.STATIC_URL + "images/semantic_ui.png"


@plugin_pool.register_plugin
class StepsContainerPluginPublisher(CMSPluginBase):
    model = StepsContainerModel
    module = _('Fomantic UI')
    name = _('Steps Container')
    render_template = 'djangocms_fomantic_ui/steps.html'
    allow_children = True
    child_classes = ['StepPluginPublisher']

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context


@plugin_pool.register_plugin
class StepPluginPublisher(CMSPluginBase):
    model = StepModel
    module = _('Fomantic UI')
    name = _('Step')
    render_template = 'djangocms_fomantic_ui/step.html'

    require_parent = True
    parent_classes = ['StepsContainerPluginPublisher']

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context


@plugin_pool.register_plugin
class EmbedPublisher(CMSPluginBase):
    model = Embed
    module = _('Fomantic UI')
    name = _('Embed')
    render_template = 'djangocms_fomantic_ui/embed.html'

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context


@plugin_pool.register_plugin
class RevealPublisher(CMSPluginBase):
    model = Reveal
    module = _('Fomantic UI')
    name = _('Reveal')
    render_template = 'djangocms_fomantic_ui/reveal.html'
    allow_children = True  # We just want to have one or no link, not two or more.
    child_classes = ['LinkPlugin']

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context


@plugin_pool.register_plugin
class GridPublisher(CMSPluginBase):
    model = Grid
    module = _('Fomantic UI')
    name = _('Grid')
    render_template = 'djangocms_fomantic_ui/generic_plugin.html'
    allow_children = True
    child_classes = ['RowPublisher', 'ColumnPublisher']

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context


@plugin_pool.register_plugin
class RowPublisher(CMSPluginBase):
    model = Row
    module = _('Fomantic UI')
    name = _('Row')
    render_template = 'djangocms_fomantic_ui/row.html'
    require_parent = True
    parent_classes = ['GridPublisher']
    allow_children = True
    child_classes = ['ColumnPublisher']

    def __str__(self):
        return _('row')

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context


@plugin_pool.register_plugin
class ColumnPublisher(CMSPluginBase):
    model = Column
    module = _('Fomantic UI')
    name = _('Column')
    render_template = 'djangocms_fomantic_ui/column.html'
    require_parent = True
    parent_classes = ['GridPublisher', 'RowPublisher']
    allow_children = True

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context


@plugin_pool.register_plugin
class SegmentPublisher(CMSPluginBase):
    model = Segment
    module = _('Fomantic UI')
    name = _('Segment')
    allow_children = True
    render_template = "djangocms_fomantic_ui/segment.html"
    cache = False  # ?


@plugin_pool.register_plugin
class MessagePublisher(CMSPluginBase):
    model = Message  # CMSPlugin
    module = _('Fomantic UI')
    name = _('Message')
    allow_children = True
    render_template = "djangocms_fomantic_ui/message.html"
    cache = False  # ?


@plugin_pool.register_plugin
class ContainerPublisher(CMSPluginBase):
    model = Container
    module = _('Fomantic UI')
    name = _('Container')
    render_template = 'djangocms_fomantic_ui/generic_plugin.html'
    allow_children = True

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context


@plugin_pool.register_plugin
class DivPublisher(CMSPluginBase):
    model = Div
    module = _('Fomantic UI')
    name = _('Div')
    render_template = 'djangocms_fomantic_ui/div.html'
    allow_children = True

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context


@plugin_pool.register_plugin
class DivContainerPublisher(CMSPluginBase):
    model = Div
    module = _('Fomantic UI')
    name = _('Div container')
    render_template = 'djangocms_fomantic_ui/div_container.html'
    allow_children = True

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context


@plugin_pool.register_plugin
class ButtonPublisher(CMSPluginBase):
    model = Button
    module = _('Fomantic UI')
    name = _('Button')
    text_enabled = True
    render_template = 'djangocms_fomantic_ui/button.html'
    allow_children = True
    child_classes = ['LinkPlugin', 'IconPluginPublisher']

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context


# def icon_src(self, instance):
# 	return settings.STATIC_URL + "images/semantic_ui.png"
#
# def icon_alt(self, instance):
# 	return 'Icon: {} - {}'.format(force_text(self.name), force_text(instance))


@plugin_pool.register_plugin
class ButtonsPublisher(CMSPluginBase):
    model = Buttons
    module = _('Fomantic UI')
    name = _('Buttons')
    text_enabled = True
    render_template = 'djangocms_fomantic_ui/buttons.html'
    allow_children = True
    child_classes = ['ButtonPublisher']

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context


@plugin_pool.register_plugin
class StatisticPublisher(CMSPluginBase):
    model = Statistic
    module = _('Fomantic UI')
    name = _('Statistic')
    # text_enabled = True
    render_template = 'djangocms_fomantic_ui/statistic.html'

    # allow_children = False

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context


@plugin_pool.register_plugin
class StatisticsPublisher(CMSPluginBase):
    model = Statistics
    module = _('Fomantic UI')
    name = _('Statistics')
    # text_enabled = True
    render_template = 'djangocms_fomantic_ui/generic_plugin.html'
    allow_children = True
    child_classes = ['StatisticPublisher']

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context
