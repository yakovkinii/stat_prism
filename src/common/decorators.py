import inspect
import logging

level = 0


def log_method(method):
    """
    A decorator to log the name of a class method when it is executed.
    """

    def wrapper(self, *args, **kwargs):
        global level
        class_name = self.__class__.__name__
        ident = "⋅ " * level

        logger = logging.getLogger()
        source_file = inspect.getsourcefile(method)
        line_number = inspect.getsourcelines(method)[1]
        lr = logger.makeRecord(
            logger.name,
            logging.DEBUG,
            source_file,
            line_number,
            ident + f"{class_name}.{method.__name__}",
            {},
            None,
            "",
        )
        logger.handle(lr)

        level += 1
        if args or kwargs:
            result = method(self, *args, **kwargs)
        else:
            result = method(self)
        level -= 1
        # logging.debug(ident+f"<{class_name}.{method.__name__}")
        return result

    return wrapper


def log_method_noarg(method):
    """
    A decorator to log the name of a class method when it is executed.
    Signature is without extra arguments is enforced.
    To use when Qt passes different number of arguments depending on signature.
    """

    def wrapper(self):
        global level
        class_name = self.__class__.__name__
        ident = "⋅ " * level

        logger = logging.getLogger()
        source_file = inspect.getsourcefile(method)
        line_number = inspect.getsourcelines(method)[1]
        lr = logger.makeRecord(
            logger.name,
            logging.DEBUG,
            source_file,
            line_number,
            ident + f"{class_name}.{method.__name__}",
            {},
            None,
            "",
        )
        logger.handle(lr)

        level += 1
        result = method(self)
        level -= 1
        # logging.debug(ident+f"<{class_name}.{method.__name__}")
        return result

    return wrapper
