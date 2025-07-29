from django.views.generic.base import TemplateResponseMixin


class HtmxTemplateResponseMixin(TemplateResponseMixin):
    """Renders :py:attr:`partial_template_name` instead of :py:attr:`template_name` when an htmx request is received."""

    content_type = "text/html"
    partial_template_name = None

    def render_to_response(self, context, **response_kwargs):
        """Checks the request headers and renders :py:attr:`partial_template_name` if necessary."""
        htmx_request = bool(self.request.headers.get("HX-Request"))
        boosted = bool(self.request.headers.get("HX-Boosted"))

        if self.partial_template_name and htmx_request and not boosted:
            self.template_name = self.partial_template_name
        return super().render_to_response(context, **response_kwargs)
