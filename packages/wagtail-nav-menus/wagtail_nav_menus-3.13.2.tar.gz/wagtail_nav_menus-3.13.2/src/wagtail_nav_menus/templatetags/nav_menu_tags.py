from typing import TypedDict

from django import template
from django.http import HttpRequest
from wagtail.fields import StreamField
from wagtail.models import Page, Site

from ..models import NavMenu

register = template.Library()


class NavMenuContext(TypedDict):
    calling_page: template.Context
    menu_items: StreamField
    menu_name: str
    request: HttpRequest


@register.inclusion_tag("nav_menus/tags/menu.html", takes_context=True)
def get_nav_menu(
    context: template.Context, menu_name: str, calling_page: Page = None
) -> NavMenuContext:
    assert hasattr(context, "request")
    site = Site.find_for_request(context.request)
    nav_menu = NavMenu.objects.get_or_create(name=menu_name, site=site)[0]
    return {
        "calling_page": calling_page,
        "menu_items": nav_menu.menu,
        "menu_name": nav_menu.name,
        "request": context["request"],
    }


@register.simple_tag(takes_context=True)
def get_nav_menu_json(context: template.Context, menu_name: str) -> str:
    assert hasattr(context, "request")
    site = Site.find_for_request(context.request)
    nav_menu = NavMenu.objects.get_or_create(name=menu_name, site=site)[0]
    return nav_menu.to_json()
