from django.conf import settings
from django.forms import widgets
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class BaseSelectWidget(widgets.Select):
    """Base widget for all select fields with Select2 integration.

    This widget provides:
    - Select2 integration with AJAX search
    - Dark mode by default
    - Automatic value handling
    - Error handling
    """

    template_name = "django/forms/widgets/select.html"
    option_template_name = "django/forms/widgets/select_option.html"

    def __init__(self, attrs=None, choices=()):
        attrs = attrs or {}
        # Add base classes for styling
        base_classes = ['admin-autocomplete']
        if 'class' in attrs:
            base_classes.append(attrs['class'])
        attrs['class'] = ' '.join(base_classes)
        
        # Set default attributes
        attrs.update({
            'data-ajax-url': None,
            'data-placeholder': 'Search...',
            'data-minimum-input-length': '2',
            'data-theme': 'admin-dark',  # Set dark theme by default
            'data-width': '100%',
            'data-dark-mode': 'true',    # Additional flag for dark mode
        })
        super().__init__(attrs=attrs, choices=choices)

    def get_context(self, name, value, attrs):
        """Get context for rendering the widget."""
        context = super().get_context(name, value, attrs)

        # Set AJAX URL
        context["widget"]["attrs"]["data-ajax-url"] = self.get_url()

        # Add initial value if exists
        if value:
            try:
                obj = self.get_object_by_id(value)
                if obj:
                    # Add to choices for initial render
                    choice_value = str(value)
                    choice_label = self.format_choice(obj)
                    context["widget"]["choices"] = [(choice_value, choice_label)]
                    
                    # Store initial data for JavaScript
                    widget_id = attrs.get('id', f'id_{name}')
                    # Move script to a separate block
                    context["widget"]["initial_data"] = {
                        'id': widget_id,
                        'value': choice_value,
                        'label': choice_label
                    }
            except Exception as e:
                if settings.DEBUG:
                    print(f"Error getting object: {str(e)}")

        return context

    def render(self, name, value, attrs=None, renderer=None):
        """Custom render method to handle Select2 initialization."""
        context = self.get_context(name, value, attrs)
        
        # Render select element
        select_html = super().render(name, value, attrs, renderer)
        
        # Add initialization script if we have initial data
        if initial_data := context["widget"].get("initial_data"):
            script = (
                '<script type="text/javascript">\n'
                '  window.WIDGET_INITIAL_DATA = '
                'window.WIDGET_INITIAL_DATA || {};\n'
                f'  window.WIDGET_INITIAL_DATA["{initial_data["id"]}"] = '
                f'{{"id": "{initial_data["value"]}", '
                f'"text": "{initial_data["label"]}"}};\n'
                '</script>'
            )
            return format_html(
                '<div class="select-container">\n{}\n{}\n</div>',
                select_html,
                mark_safe(script)
            )
        
        return format_html(
            '<div class="select-container">\n{}\n</div>',
            select_html
        )

    def get_url(self):
        """Get URL for autocomplete API endpoint."""
        raise NotImplementedError("Subclasses must implement get_url()")

    def get_object_by_id(self, value):
        """Retrieve object by its ID from database."""
        raise NotImplementedError("Subclasses must implement get_object_by_id()")

    def format_choice(self, obj):
        """Format object for display in select widget."""
        raise NotImplementedError("Subclasses must implement format_choice()")
