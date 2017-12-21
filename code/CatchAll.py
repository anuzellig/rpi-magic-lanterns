# A fake module that pretends to support any method and attribute. Always returns None


class CatchAll(object):
    def __getattr__(self, name):
        def method(*args, **kwargs):
            _ = args
            _ = kwargs

        return method
