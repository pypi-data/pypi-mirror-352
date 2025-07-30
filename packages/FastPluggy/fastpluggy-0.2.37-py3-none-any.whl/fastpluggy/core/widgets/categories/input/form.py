from typing import List, Dict, Any, Optional, Type

from wtforms import Form

from fastpluggy.core.models_tools.shared import ModelToolsShared
from fastpluggy.core.view_builer.components import FieldHandlingView
from fastpluggy.core.view_builer.form_builder import FormBuilder
from fastpluggy.core.widgets.base import AbstractWidget


class FormWidget(AbstractWidget, FieldHandlingView):
    """
    Unified form widget that combines the original FormWidget and FormView capabilities.
    Can be instantiated either by passing a WTForms-compatible `fields` mapping (for manual field definitions)
    or by providing a SQLAlchemy-backed `model` (to auto-generate fields).
    """

    widget_type = "form"
    macro_name = "render_form"
    render_method = "macro"

    template_name = "widgets/input/form.html.j2"
    category = "input"
    description = "Form component with validation and submission handling"
    icon = "wpforms"

    form: Optional[Form] = None

    def __init__(
        self,
        # For auto-generated forms from a SQLAlchemy model (old behavior):
        model: Optional[Type[Any]] = None,
        exclude_fields: Optional[List[str]] = None,
        readonly_fields: Optional[List[str]] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        # For manual form definitions (new behavior):
        fields: Optional[Dict[str, Any]] = None,
        # Common form attributes:
        action: str = "",
        method: str = "POST",
        title: Optional[str] = None,
        submit_label: Optional[str] = "Submit",
        # Extra kwargs forwarded to AbstractWidget / FieldHandlingView
        **kwargs
    ):
        """
        Initialize a combined FormWidget.

        Args:
            model: If provided, a SQLAlchemy model class (or similar) to auto-generate the form.
            exclude_fields: List of field names to exclude when auto-generating.
            readonly_fields: List of field names to render as read-only when auto-generating.
            additional_fields: Dict[str, Any] of extra fields to add to an auto-generated form.
            data: SQLAlchemy instance or dict to populate initial form data.
            fields: Dict[str, Any] of manual WTForms Field classes (callable or field instance).
                    If `fields` is provided, the auto-generation via `model` is skipped.
            action: URL where the form submits.
            method: HTTP method for the form ("POST" by default).
            title: Optional title text for the form (rendered by the template).
            submit_label: Label text for the submit button.
            **kwargs: Other parameters forwarded to the parent classes.
        """
        # Keep track of form‐generation parameters
        self.model = model
        self.exclude_fields = exclude_fields or []
        self.readonly_fields = readonly_fields or []
        self.additional_fields = additional_fields or {}
        self.data = (
            ModelToolsShared.extract_model_data(
                data, fields=None, exclude=self.exclude_fields
            )
            if data
            else {}
        )

        # Manual WTForms field definitions (if provided)
        self.fields = fields or {}

        # Common form metadata
        self.action = action
        self.method = method.upper()
        self.title = title
        self.submit_label = submit_label

        # Initialize parent classes after setting attributes
        super().__init__(**kwargs)

        # Placeholder for the WTForms Form instance
        self.form = None

    def _generate_form_class(self) -> Type[Form]:
        """
        Create a dynamic WTForms `Form` subclass based on either:
          - `self.fields`: a dict of field-name → field-class/instance
          - or, if `self.fields` is empty, auto-generate from `self.model` via FormBuilder.
        """
        # If manual fields are defined, build a custom Form class
        if self.fields:
            form_fields = {
                name: (field() if callable(field) else field)
                for name, field in self.fields.items()
            }
            form_name = (
                self.model.__name__ + "ManualForm"
                if self.model
                else "ManualForm"
            )
            return type(form_name, (Form,), form_fields)

        # Otherwise, require a model to auto-generate the form
        if not self.model:
            raise ValueError("Either `fields` or `model` must be provided to build a form.")

        return FormBuilder.generate_form(
            model=self.model,
            exclude_fields=self.exclude_fields,
            additional_fields=self.additional_fields,
            readonly_fields=self.readonly_fields,
        )

    def get_form(self, form_data=None) -> Form:
        """
        Return a WTForms Form instance, populating it with `form_data` (e.g., request.form)
        and `self.data` (e.g., model instance or dict).

        If the form class has not yet been instantiated, generate it first.
        """
        # Normalize the list of fields to exclude (handles wildcard or nested names if needed)
        self.exclude_fields = self.process_fields_names(self.exclude_fields or [])

        if self.form is None:
            FormClass = self._generate_form_class()
            # `formdata=form_data` binds POST data; `data=self.data` populates initial values
            self.form = FormClass(formdata=form_data, data=self.data)
        else:
            # Re-process an existing form (e.g., after validation fails)
            self.form.process(formdata=form_data, data=self.data)

        return self.form

    def process(self, form_data=None, **kwargs) -> None:
        """
        Top-level hook invoked during rendering/processing. Ensures that
        the WTForms form is instantiated and ready for template rendering.

        Args:
            form_data: Typically `request.form` or dictionary of POSTed data.
            **kwargs: Additional parameters that might be used by FieldHandlingView.
        """
        # Update exclude_fields if dynamic overrides were passed in via kwargs
        self.exclude_fields = self.process_fields_names(self.exclude_fields or [])

        # Instantiate or re-populate the form
        self.get_form(form_data)

        # Any additional processing inherited from FieldHandlingView
        # (e.g., attaching errors or handling special field logic)
        super().process(**kwargs)
