from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder


class InvenioRDMRecordBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "invenio_record"
    section = "record"
    template = "rdm-record"

    def finish(self, **extra_kwargs):
        if self.current_model.profile == 'record':

            super().finish()
