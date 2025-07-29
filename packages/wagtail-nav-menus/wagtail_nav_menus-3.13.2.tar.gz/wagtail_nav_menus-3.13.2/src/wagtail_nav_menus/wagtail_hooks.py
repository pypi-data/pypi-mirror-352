from collections.abc import Callable

from django.utils.translation import gettext_lazy as _
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register

from .models import NavMenu


class NavMenuAdmin(ModelAdmin):
    model = NavMenu  # type: ignore[assignment]
    menu_label = _("Nav Menu")  # type: ignore[assignment]
    menu_icon = "link"  # type: ignore[assignment]
    menu_order = 5000  # type: ignore[assignment] # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = True  # or True to add your model to the Settings sub-menu
    list_display = ("name", "site")  # type: ignore[assignment]


_modeladmin_register: Callable[[type[ModelAdmin]], type[ModelAdmin]] = (
    modeladmin_register
)

_modeladmin_register(NavMenuAdmin)
