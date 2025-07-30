from pip_services4_commons.convert import TypeCode
from pip_services4_data.validate import ObjectSchema


class TopicV1Schema(ObjectSchema):
    def __init__(self):
        super().__init__()

        self.with_optional_property('id', TypeCode.String)
        self.with_optional_property('owner_id', TypeCode.String)
        self.with_optional_property('name', TypeCode.String)
        self.with_optional_property('access_list', TypeCode.Array)
        self.with_optional_property('created_time', TypeCode.DateTime)
        self.with_optional_property('updated_time', TypeCode.DateTime)
        self.with_optional_property('model_id', TypeCode.String)
        self.with_optional_property('tailored_model_id', TypeCode.String)