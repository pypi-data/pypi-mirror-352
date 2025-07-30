from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder


class InvenioRDMDraftRecordBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "invenio_record"
    section = "record"
    template = "rdm-draft-record"

    def finish(self, **extra_kwargs):
        super().finish()