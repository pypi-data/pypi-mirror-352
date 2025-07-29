import blinker  # type: ignore[import-untyped]
import inspect
import itertools
import weakref
from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    Tuple,
    Type,
    get_origin,
    get_args,
    TypeVar,
    Generic,
    Union,
)
from types import SimpleNamespace
import asyncio

_ReceiverCallable = Callable[..., Any]
T = TypeVar('T')

MAX_CACHE_SIZE = 1024
_dict_ns_cache = {}
_list_ns_cache = {}


_EMIT_MARKER = object()


def _memoized_dict_to_ns(obj: Any) -> Union[SimpleNamespace, Any]:
    obj_id = id(obj)
    if obj_id in _dict_ns_cache:
        return _dict_ns_cache[obj_id]  # type: ignore[misc]
    if not all(isinstance(k, str) for k in obj):  # type: ignore[misc]
        return obj  # type: ignore[misc]
    try:
        ns = SimpleNamespace(
            **{k: _CoolSignalBase._recursive_ns_memo(v) for k, v in obj.items()}  # type: ignore[misc]
        )
    except TypeError:
        ns = obj
    if len(_dict_ns_cache) >= MAX_CACHE_SIZE:  # type: ignore[misc]
        _dict_ns_cache.clear()
    _dict_ns_cache[obj_id] = ns
    return ns


def _memoized_list_to_ns(obj: Any) -> Union[list[Any], Any]:
    obj_id = id(obj)
    if obj_id in _list_ns_cache:
        return _list_ns_cache[obj_id]  # type: ignore[misc]
    ns_list = [_CoolSignalBase._recursive_ns_memo(v) for v in obj]  # type: ignore[misc]
    if len(_list_ns_cache) >= MAX_CACHE_SIZE:  # type: ignore[misc]
        _list_ns_cache.clear()
    _list_ns_cache[obj_id] = ns_list
    return ns_list  # type: ignore[misc]


class _CoolSignalBase(blinker.Signal, Generic[T]):  # type: ignore[misc]
    _send_counter: "itertools.count[int]"
    _receiver_map: "weakref.WeakKeyDictionary[_ReceiverCallable, _ReceiverCallable]"

    def __init__(self, doc: Optional[str] = None) -> None:
        super().__init__(doc)  # type: ignore[misc]
        self._send_counter = itertools.count()
        self._receiver_map = weakref.WeakKeyDictionary()

    def disconnect(
        self, receiver: _ReceiverCallable, sender: Any = blinker.ANY  # type: ignore[misc]
    ) -> None:
        wrapped_receiver = self._receiver_map.pop(receiver, None)
        if wrapped_receiver:
            super().disconnect(wrapped_receiver, sender=sender)  # type: ignore[misc]

    @staticmethod
    def _recursive_ns(value: Any) -> Any:
        return _CoolSignalBase._recursive_ns_memo(value)

    @staticmethod
    def _recursive_ns_memo(value: Any):
        if isinstance(value, dict):
            return _memoized_dict_to_ns(value)
        if isinstance(value, list):
            return _memoized_list_to_ns(value)
        return value

    @staticmethod
    def _build_param_converters(
        sig: inspect.Signature,
    ) -> Dict[str, Callable[[Any], Any]]:
        param_converters: Dict[str, Callable[[Any], Any]] = {}
        builtin_types = {
            str,
            int,
            float,
            bool,
            bytes,
            dict,
            list,
            tuple,
            set,
            type(None),
        }
        for param_name, param_obj in sig.parameters.items():
            ann = param_obj.annotation
            if ann is inspect.Parameter.empty or ann is Any:
                continue
            origin = get_origin(ann)
            args = get_args(ann)
            if origin is list and args:
                elem_type = args[0]
                if (
                    inspect.isclass(elem_type)
                    and elem_type not in builtin_types
                    and elem_type is not Any
                ):

                    def make_list_converter(
                        elem_cls: Type[Any],
                    ) -> Callable[[Any], Any]:
                        def _conv(value_list: Any) -> Any:
                            if isinstance(value_list, list):
                                converted_list = []
                                for item in value_list:  # type: ignore[misc]
                                    if isinstance(item, elem_cls):
                                        converted_list.append(item)  # type: ignore[misc]
                                    elif isinstance(item, dict):
                                        try:
                                            converted_list.append(elem_cls(**item))  # type: ignore[misc]
                                        except Exception:
                                            converted_list.append(  # type: ignore[misc]
                                                _CoolSignalBase._recursive_ns(item)
                                            )
                                    else:
                                        converted_list.append(item)  # type: ignore[misc]
                                return converted_list  # type: ignore[misc]
                            return value_list

                        return _conv

                    param_converters[param_name] = make_list_converter(elem_type)
                    continue
            if inspect.isclass(ann) and ann not in builtin_types and ann is not Any:

                def make_obj_converter(obj_cls: Type[Any]) -> Callable[[Any], Any]:
                    def _conv(value: Any) -> Any:
                        if isinstance(value, obj_cls):
                            return value
                        if isinstance(value, dict):
                            try:
                                return obj_cls(**value)
                            except Exception:
                                return _CoolSignalBase._recursive_ns(value)
                        return value

                    return _conv

                param_converters[param_name] = make_obj_converter(ann)
                continue
            param_converters[param_name] = _CoolSignalBase._recursive_ns
        return param_converters


class CoolSignal(_CoolSignalBase[T], Generic[T]):
    @staticmethod
    def _wrap_handler(func: _ReceiverCallable) -> _ReceiverCallable:
        sig = inspect.signature(func)
        func_accepts_kwargs: bool = any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
        )
        param_converters = _CoolSignalBase._build_param_converters(sig)
        has_sender_param = "sender" in sig.parameters
        is_bound_method = hasattr(func, "__self__") and getattr(func, "__self__", None) is not None  # type: ignore[misc]

        def wrapper(sender: Any, **kwargs: Any) -> Tuple[Optional[int], Any]:
            request_id: Optional[int] = kwargs.pop("_request_id", None)

            is_emit_call = kwargs.pop("_emit_marker", None) is _EMIT_MARKER
            emitted_value = kwargs.pop("_emit_payload", None) if is_emit_call else None

            original_kwargs_snapshot = kwargs.copy()
            final_kwargs = {}
            target_param_name = None

            if is_emit_call:

                valid_params = set(sig.parameters.keys())
                if has_sender_param:
                    valid_params -= {"sender"}
                if is_bound_method:
                    valid_params -= {"self"}

                if len(valid_params) == 1:
                    target_param_name = list(valid_params)[0]
                    kwargs[target_param_name] = emitted_value
                    original_kwargs_snapshot = kwargs.copy()
                elif len(valid_params) == 0 and func_accepts_kwargs:
                    target_param_name = "payload"
                    kwargs[target_param_name] = emitted_value
                    original_kwargs_snapshot = kwargs.copy()
                else:
                    raise TypeError(
                        f"emit() requires handler '{getattr(func, '__name__', repr(func))}' "
                        f"to accept exactly one payload argument (found {len(valid_params)}: {valid_params}) "
                        "or only **kwargs."
                    )

            converted_kwargs: Dict[str, Any] = {}
            for key, val in kwargs.items():
                converter = param_converters.get(key)
                if converter:
                    try:
                        converted_kwargs[key] = converter(val)
                    except Exception:
                        converted_kwargs[key] = _CoolSignalBase._recursive_ns(val)
                else:
                    converted_kwargs[key] = _CoolSignalBase._recursive_ns(val)

            if func_accepts_kwargs:
                final_kwargs = converted_kwargs
            else:
                valid_params = set(sig.parameters.keys())  # Always initialize valid_params
                if has_sender_param:
                    valid_params -= {"sender"}
                if is_bound_method:
                    valid_params -= {"self"}

                final_kwargs = {
                    k: v for k, v in converted_kwargs.items() if k in valid_params  # type: ignore[misc]
                }

            try:
                result: Any
                if has_sender_param:
                    result = func(sender, **final_kwargs)
                else:
                    result = func(**final_kwargs)
            except TypeError as e:
                call_pattern = (
                    "func(sender, **final_kwargs)"
                    if has_sender_param
                    else "func(**final_kwargs)"
                )
                err_msg = (
                    f"Error calling handler '{getattr(func, '__name__', repr(func))}': {e}.\\n"
                    f"  Handler Signature: {sig}\\n"
                    f"  Is bound: {is_bound_method}, Expects sender: {has_sender_param}\\n"
                    f"  Call pattern used: {call_pattern}\\n"
                    f"  Provided keyword args (original): {original_kwargs_snapshot}\\n"
                    f"  Processed/Filtered keyword args passed: {final_kwargs}"
                )
                raise TypeError(err_msg) from e

            return (request_id, result)

        setattr(wrapper, "_is_coolsignal_wrapped", True)
        return wrapper

    def connect(
        self, receiver: _ReceiverCallable, sender: Any = blinker.ANY, weak: bool = False  # type: ignore[misc]
    ) -> None:
        if receiver in self._receiver_map:
            return
        is_already_wrapped = getattr(receiver, "_is_coolsignal_wrapped", False)
        if not is_already_wrapped:
            wrapped_receiver = CoolSignal._wrap_handler(receiver)
            self._receiver_map[receiver] = wrapped_receiver
        else:
            wrapped_receiver = receiver
        super().connect(wrapped_receiver, sender=sender, weak=weak)  # type: ignore[misc]

    def send(self, sender: Optional[Any] = None, **kwargs: Any) -> Optional[Any]:
        request_id: int = next(self._send_counter)
        payload: Dict[str, Any] = kwargs.copy()
        payload["_request_id"] = request_id
        responses: list[tuple[_ReceiverCallable, tuple[Optional[int], Any]]] = (  # type: ignore[misc]
            super().send(sender, **payload)  # type: ignore[misc]
        )
        for _receiver_func, (rid, value) in responses:  # type: ignore[misc]
            if rid is not None and rid == request_id and value is not None:
                return value  # type: ignore[misc]
        return None

    def emit(self, value: T = None, *, sender: Optional[Any] = None) -> Optional[Any]:
        """Emits a signal with a single positional payload.

        The handler should expect exactly one argument (besides optional sender).
        The name of the handler's parameter will be used for the payload.
        """

        return self.send(sender=sender, _emit_payload=value, _emit_marker=_EMIT_MARKER)


class CoolSignalAsync(_CoolSignalBase[T], Generic[T]):
    @staticmethod
    def _wrap_handler(func: _ReceiverCallable) -> _ReceiverCallable:
        if not inspect.iscoroutinefunction(func):
            raise TypeError("CoolSignalAsync only supports async (coroutine) handlers.")
        sig = inspect.signature(func)
        # Remove unused variable
        # func_params: Set[str] = set(sig.parameters.keys())
        func_accepts_kwargs: bool = any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
        )
        param_converters = _CoolSignalBase._build_param_converters(sig)
        has_sender_param = "sender" in sig.parameters
        is_bound_method = hasattr(func, "__self__") and getattr(func, "__self__", None) is not None  # type: ignore[misc]

        async def wrapper(sender: Any, **kwargs: Any) -> Tuple[Optional[int], Any]:
            request_id: Optional[int] = kwargs.pop("_request_id", None)

            is_emit_call = kwargs.pop("_emit_marker", None) is _EMIT_MARKER
            emitted_value = kwargs.pop("_emit_payload", None) if is_emit_call else None

            original_kwargs_snapshot = kwargs.copy()
            final_kwargs = {}
            target_param_name = None

            if is_emit_call:

                valid_params = set(sig.parameters.keys())
                if has_sender_param:
                    valid_params -= {"sender"}
                if is_bound_method:
                    valid_params -= {"self"}

                if len(valid_params) == 1:
                    target_param_name = list(valid_params)[0]
                    kwargs[target_param_name] = emitted_value
                    original_kwargs_snapshot = kwargs.copy()
                elif len(valid_params) == 0 and func_accepts_kwargs:
                    target_param_name = "payload"
                    kwargs[target_param_name] = emitted_value
                    original_kwargs_snapshot = kwargs.copy()
                else:
                    raise TypeError(
                        f"emit() requires handler '{getattr(func, '__name__', repr(func))}' "
                        f"to accept exactly one payload argument (found {len(valid_params)}: {valid_params}) "
                        "or only **kwargs."
                    )

            converted_kwargs: Dict[str, Any] = {}
            for key, val in kwargs.items():
                converter = param_converters.get(key)
                if converter:
                    try:
                        converted_kwargs[key] = converter(val)
                    except Exception:
                        converted_kwargs[key] = _CoolSignalBase._recursive_ns(val)
                else:
                    converted_kwargs[key] = _CoolSignalBase._recursive_ns(val)

            if func_accepts_kwargs:
                final_kwargs = converted_kwargs
            else:
                valid_params = set(sig.parameters.keys())  # Always initialize valid_params
                if has_sender_param:
                    valid_params -= {"sender"}
                if is_bound_method:
                    valid_params -= {"self"}

                final_kwargs = {
                    k: v for k, v in converted_kwargs.items() if k in valid_params  # type: ignore[misc]
                }

            try:
                async_result: Any
                if has_sender_param:
                    async_result = await func(sender, **final_kwargs)
                else:
                    async_result = await func(**final_kwargs)
            except TypeError as e:
                call_pattern = (
                    "await func(sender, **final_kwargs)"
                    if has_sender_param
                    else "await func(**final_kwargs)"
                )
                err_msg = (
                    f"Error calling handler '{getattr(func, '__name__', repr(func))}': {e}.\\n"
                    f"  Handler Signature: {sig}\\n"
                    f"  Is bound: {is_bound_method}, Expects sender: {has_sender_param}\\n"
                    f"  Call pattern used: {call_pattern}\\n"
                    f"  Provided keyword args (original): {original_kwargs_snapshot}\\n"
                    f"  Processed/Filtered keyword args passed: {final_kwargs}"
                )
                raise TypeError(err_msg) from e

            return (request_id, async_result)

        setattr(wrapper, "_is_coolsignal_wrapped", True)
        return wrapper

    def connect(
        self, receiver: _ReceiverCallable, sender: Any = blinker.ANY, weak: bool = False  # type: ignore[misc]
    ) -> None:
        if receiver in self._receiver_map:
            return
        is_already_wrapped = getattr(receiver, "_is_coolsignal_wrapped", False)
        if not is_already_wrapped:
            wrapped_receiver = CoolSignalAsync._wrap_handler(receiver)
            self._receiver_map[receiver] = wrapped_receiver
        else:
            wrapped_receiver = receiver
        super().connect(wrapped_receiver, sender=sender, weak=weak)  # type: ignore[misc]

    async def send(self, sender: Optional[Any] = None, **kwargs: Any) -> Optional[Any]:
        request_id: int = next(self._send_counter)
        payload: Dict[str, Any] = kwargs.copy()
        payload["_request_id"] = request_id
        responses = await self._send_all(sender, **payload)  # type: ignore[misc]
        for _receiver_func, (rid, value) in responses:  # type: ignore[misc]
            if rid is not None and rid == request_id and value is not None:
                return value  # type: ignore[misc]
        return None

    async def emit(self, value: T = None, *, sender: Optional[Any] = None) -> Optional[Any]:
        """Emits an async signal with a single positional payload.

        The handler should expect exactly one argument (besides optional sender).
        The name of the handler's parameter will be used for the payload.
        """
        return await self.send(sender=sender, _emit_payload=value, _emit_marker=_EMIT_MARKER)

    async def _send_all(self, sender: Any, **payload: Any):  # type: ignore[misc]
        coros = []  # type: ignore[misc]
        for receiver in self.receivers_for(sender):  # type: ignore[misc]
            coros.append(receiver(sender, **payload))  # type: ignore[misc]
        results = await asyncio.gather(*coros)  # type: ignore[misc]
        return zip(self.receivers_for(sender), results)  # type: ignore[misc]
