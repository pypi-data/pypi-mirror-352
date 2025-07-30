# fastpluggy/core/view_builder/builder.py - Backward Compatible Version

from fastapi import Request
from loguru import logger
import traceback
from typing import List, Any, Dict, Optional, Union

from fastpluggy.core.config import FastPluggyConfig
from fastpluggy.core.flash import FlashMessage
from fastpluggy.core.global_registry import GlobalRegistry
from fastpluggy.core.widgets import DebugPanelWidget
from fastpluggy.core.widgets.fastpluggy_integration import FastPluggyWidgets


class ViewBuilder:
    """
    Enhanced ViewBuilder with FastPluggy widget registry integration.
    Supports both old 'items' and new 'widgets' parameter for backward compatibility.
    """

    def __init__(self):
        self.templates = None

    def generate(
        self,
        request: Request,
        widgets: Optional[List[Any]] = None,
        *,  # Force keyword-only arguments after this
        items: Optional[List[Any]] = None,  # OLD parameter name for compatibility
        title: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Generate the response for the given request and widgets/items.

        Args:
            request: The current HTTP request
            widgets: List of widget instances to render (NEW parameter name)
            items: List of component instances to render (OLD parameter name - deprecated)
            title: Page title
            **kwargs: Additional context data

        Note:
            - Use 'widgets' parameter for new code
            - 'items' parameter is deprecated but supported for backward compatibility
            - When 'items' is used, a migration alert will be shown (unless disabled)
        """
        GlobalRegistry.clear_globals_key('migration_alert')
        # Handle backward compatibility
        if widgets is None and items is not None:
            # Old parameter used
            widgets = items
            logger.warning(
                "ViewBuilder.generate() called with deprecated 'items' parameter. "
                "Please update to use 'widgets' parameter for new widget system."
            )
            GlobalRegistry.extend_globals('migration_alert',['Update your ViewBuilder calls to use <code>widgets=</code> instead of <code>items=</code> for the new widget system benefits.'])
        elif widgets is None and items is None:
            # No widgets provided
            widgets = []
        elif widgets is not None and items is not None:
            # Both provided - prioritize new parameter
            logger.warning(
                "ViewBuilder.generate() called with both 'widgets' and 'items' parameters. "
                "Using 'widgets' parameter and ignoring 'items'."
            )

        self._create_migration_alert(request)

        debug = FastPluggyConfig().debug
        if debug:
            debug_panel = DebugPanelWidget(
                items=widgets,
                show_attributes=True,
                show_warnings=True,
                auto_expand=False
            )
            widgets.insert(0, debug_panel)

        # Get widget registry data for templates
        widget_registry = FastPluggyWidgets.get_widget_registry()
        
        # Build template context
        context = {
            "request": request,
            "title": title,
            **self._build_widget_context(widget_registry),
            **kwargs  # Additional context from caller
        }
        
        # Process widgets
        rendered_widgets = []

        # Process all widgets
        for widget in widgets:
            try:
                processed_widget = self._process_widget(widget, request, **kwargs)
                rendered_widgets.append(processed_widget)
                
            except Exception as e:
                logger.exception(f"Failed to process widget {widget}: {e}", exc_info=True)
                rendered_widgets.append(self._generate_error_widget(widget, e))
        
        # Support both old and new variable names in templates
        context["widget_views"] = rendered_widgets  # NEW variable name

        return self.templates.TemplateResponse(
            "generic_page.html.j2", context
        )

    @staticmethod
    def _create_migration_alert(request) -> None:
        """Create a migration alert widget when old 'items' parameter is used."""
        migration_alerts = GlobalRegistry.get_global('migration_alert', default=[])
        if migration_alerts:
            # Build a list of messages returned from the registry
            items_html = "".join(f"<li><i class=\"fas fa-info-circle me-1\"></i>{msg}</li>" for msg in migration_alerts)
            message = f"""
                <strong>Migration Notice:</strong> This page is using the old component system.
                <br>
                <small class="text-muted">
                    <ul class="mb-0">
                        {items_html}
                    </ul>
                </small>
            """
            FlashMessage.add(request, message, "warning")

    def _process_widget(self, widget: Any, request: Request, **kwargs) -> Any:
        """Process an individual widget/component."""
        
        # Inject request and db if available
        if hasattr(widget, "request"):
            widget.request = request
        
        # Try to inject database if available
        try:
            from fastpluggy.core.database import get_db
            if hasattr(widget, "db"):
                widget.db = next(get_db())
        except (ImportError, Exception):
            pass  # Database not available or failed
        
        # Process the widget
        if hasattr(widget, "process"):
            widget.process(request=request, **kwargs)

        return widget
    
    def _build_widget_context(self, widget_registry: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Build template context from widget registry."""
        widget_templates = {}
        widget_macros = {}
        
        for widget_type, widget_info in widget_registry.items():
            template_name = widget_info.get('template_name')
            macro_name = widget_info.get('macro_name')
            
            if template_name:
                widget_templates[widget_type] = template_name
            elif macro_name:
                widget_macros[widget_type] = macro_name
        
        return {
            'widget_templates': widget_templates,
            'widget_macros': widget_macros,
            'registered_widget_types': list(widget_registry.keys()),
            'widget_registry': widget_registry,
        }
    
    @staticmethod
    def _generate_error_widget(widget, error):
        """Generate error widget for failed widgets."""
        error_message = str(error)
        return {
            "widget_type": "error",
            "type": "error",  # For compatibility
            "title": f"Error in {type(widget).__name__}",
            "error_message": error_message,
            "traceback_str": ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        }
