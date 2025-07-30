from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder


class InvenioRDMRecordMetadataBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "invenio_record_metadata"
    section = "record-metadata"
    template = "rdm-record-metadata"