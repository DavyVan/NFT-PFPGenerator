from .Context import Context


class ContextManager:
    def __init__(self):
        self.contexts = dict()  # type: dict[str, Context]  # For now, the key is fixed, so it is like a non-dict variable
        self.max_count = 1  # type: int

    def new_context(self, context_id: str, jsonstr: str) -> Context:
        # if len(self.contexts) >= self.max_count:
        #     raise OverflowError("Not enough slot for new collection.")
        if len(self.contexts) == 1 and self.contexts[context_id].executing is True:
            raise OverflowError("There is a executing process.")
        _new = Context(jsonstr)
        self.contexts[context_id] = _new
        return _new

    def new_and_start_context(self, context_id: str, jsonstr: str, enable_render: bool, enable_metadata: bool, enable_excel: bool):
        _new = self.new_context(context_id, jsonstr)
        _new.run(enable_render, enable_metadata, enable_excel)

    def get_context(self, context_id: str) -> Context:
        return self.contexts[context_id]

    def del_cotext(self, context_id: str):
        del self.contexts[context_id]

    def get_progress(self, context_id: str) -> (bool, bool, str, int, int):
        """

        :param context_id:
        :return: (success, executing, error_msg, progress, total)
        """
        c = self.contexts[context_id]
        progress, total = c.collection.get_progress()
        return c.success, c.executing, c.error_msg, progress, total
