from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def back_button():
    back_html = """
    <button onclick="goBack()", class="my-back-button">Go Back</button>
    <script>
    function goBack() {
        window.history.back();
    }
    </script>
    """
    return mark_safe(back_html)