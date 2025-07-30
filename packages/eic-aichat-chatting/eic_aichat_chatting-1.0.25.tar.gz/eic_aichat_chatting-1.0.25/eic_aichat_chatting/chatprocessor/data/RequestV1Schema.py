from pip_services4_commons.convert import TypeCode
from pip_services4_data.validate import ObjectSchema

class RequestV1Schema(ObjectSchema):
    """
    Schema to validate RequestV1 defined object.
    """

    def __init__(self):
        """
        Creates an instance of schema.
        """
        super().__init__()

        self.with_required_property('prompt', TypeCode.String)
        self.with_required_property('model_id', TypeCode.String)
        self.with_required_property('model_name', TypeCode.String)
        self.with_required_property('topic_id', TypeCode.String)