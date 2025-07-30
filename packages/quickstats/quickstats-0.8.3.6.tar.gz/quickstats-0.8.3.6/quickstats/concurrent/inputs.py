from typing import Union, Optional, Callable

# sentinel object to indicate a parameter is not supplied
class _NOTSET_TYPE:
    pass

NOTSET = _NOTSET_TYPE()

class Input:

    _counter = 0  # non-atomically increasing counter used for ordering parameters.

    def __init__(self, dtype: Union[type, str], required: bool = False,
                 default: Optional[Any] = NOTSET,
                 default_factory: Optional[Callable] = NOTSET,
                 description: Optional[str] = None):

        if default is not NOTSET and default_factory is not NOTSET:
            raise ValueError('Cannot specify both default and default_factory.')
            
        self._default = default
        self.description = description

    def _get_value(self, task_name, param_name):
        for value, warn in self._value_iterator(task_name, param_name):
            if value != _no_value:
                if warn:
                    warnings.warn(warn, DeprecationWarning)
                return value
        return _no_value

    def _value_iterator(self, task_name, param_name):
        """
        Yield the parameter values, with optional deprecation warning as second tuple value.

        The parameter value will be whatever non-_no_value that is yielded first.
        """
        cp_parser = CmdlineParser.get_instance()
        if cp_parser:
            dest = self._parser_global_dest(param_name, task_name)
            found = getattr(cp_parser.known_args, dest, None)
            yield (self._parse_or_no_value(found), None)
        yield (self._get_value_from_config(task_name, param_name), None)
        if self._config_path:
            yield (self._get_value_from_config(self._config_path['section'], self._config_path['name']),
                   'The use of the configuration [{}] {} is deprecated. Please use [{}] {}'.format(
                       self._config_path['section'], self._config_path['name'], task_name, param_name))
        yield (self._default, None)

    def has_task_value(self, task_name, param_name):
        return self._get_value(task_name, param_name) != _no_value

    def task_value(self, task_name, param_name):
        value = self._get_value(task_name, param_name)
        if value == _no_value:
            raise MissingParameterException("No default specified")
        else:
            return self.normalize(value)

    def _is_batchable(self):
        return self._batch_method is not None

    def parse(self, x):
        """
        Parse an individual value from the input.

        The default implementation is the identity function, but subclasses should override
        this method for specialized parsing.

        :param str x: the value to parse.
        :return: the parsed value.
        """
        return x  # default impl

    def _parse_list(self, xs):
        """
        Parse a list of values from the scheduler.

        Only possible if this is_batchable() is True. This will combine the list into a single
        parameter value using batch method. This should never need to be overridden.

        :param xs: list of values to parse and combine
        :return: the combined parsed values
        """
        if not self._is_batchable():
            raise NotImplementedError('No batch method found')
        elif not xs:
            raise ValueError('Empty parameter list passed to parse_list')
        else:
            return self._batch_method(map(self.parse, xs))

    def serialize(self, x):
        """
        Opposite of :py:meth:`parse`.

        Converts the value ``x`` to a string.

        :param x: the value to serialize.
        """
        return str(x)

    def _warn_on_wrong_param_type(self, param_name, param_value):
        if self.__class__ != Parameter:
            return
        if not isinstance(param_value, str):
            warnings.warn('Parameter "{}" with value "{}" is not of type string.'.format(param_name, param_value))

    def normalize(self, x):
        """
        Given a parsed parameter value, normalizes it.

        The value can either be the result of parse(), the default value or
        arguments passed into the task's constructor by instantiation.

        This is very implementation defined, but can be used to validate/clamp
        valid values. For example, if you wanted to only accept even integers,
        and "correct" odd values to the nearest integer, you can implement
        normalize as ``x // 2 * 2``.
        """
        return x  # default impl

    def next_in_enumeration(self, value):
        """
        If your Parameter type has an enumerable ordering of values. You can
        choose to override this method. This method is used by the
        :py:mod:`luigi.execution_summary` module for pretty printing
        purposes. Enabling it to pretty print tasks like ``MyTask(num=1),
        MyTask(num=2), MyTask(num=3)`` to ``MyTask(num=1..3)``.

        :param value: The value
        :return: The next value, like "value + 1". Or ``None`` if there's no enumerable ordering.
        """
        return None

    def _parse_or_no_value(self, x):
        if not x:
            return _no_value
        else:
            return self.parse(x)

    @staticmethod
    def _parser_global_dest(param_name, task_name):
        return task_name + '_' + param_name

    @classmethod
    def _parser_kwargs(cls, param_name, task_name=None):
        return {
            "action": "store",
            "dest": cls._parser_global_dest(param_name, task_name) if task_name else param_name,
        }