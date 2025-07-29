from django.contrib import admin

from .models import Card, Embed, Icon, Reveal

# @admin.register(Tab)
# class TabAdmin(admin.ModelAdmin):
# 	pass
#

# @admin.register(Accordion)
# class AccordionAdmin(admin.ModelAdmin):
# 	pass
#
#
# @admin.register(AccordionSection)
# class AccordionSectionAdmin(admin.ModelAdmin):
# 	pass


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    pass


@admin.register(Icon)
class IconAdmin(admin.ModelAdmin):
    pass


# @admin.register(Steps_Container)
# class StepsAdmin(admin.ModelAdmin):
# 	pass
#
#
# @admin.register(Step)
# class StepAdmin(admin.ModelAdmin):
# 	pass

# @admin.register(SiteIcon)
# class SiteIconAdmin(admin.ModelAdmin):
# 	pass


@admin.register(Embed)
class EmbedAdmin(admin.ModelAdmin):
    fields = [
        ('title'), ('source', 'medium_id'), ('external_url'),
        ('placeholder_image', 'icon'), ('width_value', 'width_unit'),
        ('height_value', 'height_unit')
    ]


@admin.register(Reveal)
class RevealAdmin(admin.ModelAdmin):
    fields = [('visible_image', 'hidden_image'), ('image_size'), ('effect')]


# @admin.register(Grid)
# class GridAdmin(admin.ModelAdmin):
# 	pass
#
#
# @admin.register(Row)
# class RowAdmin(admin.ModelAdmin):
# 	pass
#
#
# @admin.register(Column)
# class GridColumnAdmin(admin.ModelAdmin):
# 	pass

# @admin.register(StaffMember)
# class StaffMemberAdmin(TranslatableAdmin):
#     list_display = ['title', 'first_name', 'last_name', 'order', 'publish']
#     list_display_links = ['first_name', 'last_name']
#     fields = [
#         ('publish'), ('title', 'first_name', 'last_name', 'order'), ('picture'),
#         ('info_text')
#     ]
