from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder


class InvenioRDMExtBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "invenio_rdm_ext"
    section = "ext"
    template = "rdm-ext"
