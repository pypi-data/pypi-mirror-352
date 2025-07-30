class RequestV1:
    """
    Request data object.
    """

    def __init__(self, user_id: str = None, prompt: str = None, model_id: str = None, model_name: str = None, topic_id: str = None):
        """
        Initializes a new instance of RequestV1.

        :param value: Request value.
        """
        self.user_id = user_id
        self.prompt = prompt
        self.model_id = model_id
        self.model_name = model_name
        self.topic_id = topic_id