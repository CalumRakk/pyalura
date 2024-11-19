class TextArea:
    def __init__(self, value=None, disabled=False):
        self.value = value
        self.disabled = disabled

    @property
    def is_disabled(self):
        return self.disabled

    def toggle(self):
        self.disabled = not self.disabled

    def disable(self):
        self.disabled = True

    def enable(self):
        self.disabled = False

    def __repr__(self):
        return self.value
