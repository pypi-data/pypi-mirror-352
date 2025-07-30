from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder
from pathlib import Path
from oarepo_model_builder.utils.python_name import module_to_path


class InvenioRDMExtDraftBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "invenio_rdm_ext_draft"
    section = "ext"
    template = "rdm-ext-draft"

    def finish(self, **extra_kwargs):
        super().finish()
        if not self.generate:
            return

        module = self._get_output_module()
        python_path = Path(module_to_path(module) + ".py")

        self.process_template(
            python_path,
            self.template,
            current_module=module,
            vars=self.vars,
            **extra_kwargs,
        )
