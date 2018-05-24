"""The base command."""

class Base(object):
    """A base command."""

    newInstance = []

    def __init__(self, options, *args, **kwargs):
        Base.session = [] 
        Base.values = {}
        self.options = options
        self.args = args
        self.kwargs = kwargs

    def run(self):
        raise NotImplementedError('You must implement the run() method yourself!')

    @classmethod
    def hold_server(cls, newInstance):
        cls.newInstance = newInstance
        return cls.newInstance
