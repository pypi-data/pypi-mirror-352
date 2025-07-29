import pytest
from src.signalkit.core import CoolSignalAsync, CoolSignal
from tests.test_models import MyHandlerClass
import random
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


def test_send_returns_value_from_simple_handler() -> None:
    # arrange
    signal = CoolSignal()

    def handler(sender: Any) -> str:
        return "ok"

    signal.connect(handler)

    # act
    response = signal.send(signal)

    # assert
    assert response == "ok"


def test_send_returns_none_when_handler_returns_none() -> None:
    # arrange
    signal = CoolSignal()

    def handler(sender: Any, **kwargs: Any) -> None:
        return None

    signal.connect(handler)

    # act
    response = signal.send(signal, data="test")

    # assert
    assert response is None


def test_send_returns_a_non_none_value_among_multiple_handlers() -> None:
    # arrange
    signal = CoolSignal()

    results: List[str] = []

    def handler1(sender: Any, value: int) -> None:
        results.append(f"h1_received_{value}")
        return None

    def handler2(sender: Any, value: int) -> str:
        results.append(f"h2_received_{value}")
        return f"ok_{value}"

    def handler3(sender: Any, value: int) -> str:
        results.append(f"h3_received_{value}")
        return f"not_reached_{value}"

    signal.connect(handler1)
    signal.connect(handler2)
    signal.connect(handler3)
    # act
    response = signal.send(signal, value=123)

    # assert
    possible_responses: Set[str] = {"ok_123", "not_reached_123"}
    assert response in possible_responses
    assert set(results) == {"h1_received_123", "h2_received_123", "h3_received_123"}


def test_handler_receives_correct_args_kwargs() -> None:
    # arrange
    signal = CoolSignal()
    received_args: Optional[Tuple[Any, ...]] = None
    received_kwargs: Optional[Dict[str, Any]] = None

    def handler(
        sender: Any,
        pos1: str = None,
        pos2: str = None,
        kw1: Optional[str] = None,
        kw2: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        nonlocal received_args, received_kwargs
        received_args = (pos1, pos2)
        received_kwargs = {"kw1": kw1, "kw2": kw2, **kwargs}
        return "received"

    signal.connect(handler)

    # act
    response = signal.send(
        sender=signal, pos1="p1_val", pos2="p2_val", kw1="kw1_val", kw2="kw2_val"
    )

    # assert
    assert response == "received"
    assert received_args == ("p1_val", "p2_val")
    assert received_kwargs == {"kw1": "kw1_val", "kw2": "kw2_val"}


def test_bound_method_handler() -> None:
    # arrange
    signal = CoolSignal()
    instance = MyHandlerClass()

    signal.connect(instance.method_handler)
    # act
    response = signal.send(signal, value_to_set=42)

    # assert
    assert response == "set_42"
    assert instance.handled_value == 42


def test_send_with_no_handlers_returns_none() -> None:
    # arrange
    signal = CoolSignal()

    # act
    response = signal.send(signal, data="no_handlers")

    # assert
    assert response is None


def test_handler_raises_exception() -> None:
    # arrange
    signal = CoolSignal()

    def handler(sender: Any) -> None:
        raise ValueError("handler error")

    signal.connect(handler)

    # act/assert
    with pytest.raises(ValueError):
        signal.send(signal)


def test_duplicate_handler_connection() -> None:
    # arrange
    signal = CoolSignal()
    call_count: Dict[str, int] = {"count": 0}

    def handler(sender: Any) -> str:
        call_count["count"] += 1
        return "ok"

    signal.connect(handler)
    signal.connect(handler)

    # act
    response = signal.send(signal)

    # assert
    assert response == "ok"
    assert call_count["count"] == 1


def test_disconnect_non_connected_handler() -> None:
    # arrange
    signal = CoolSignal()

    def handler(sender: Any) -> str:
        return "ok"

    signal.disconnect(handler)
    signal.connect(handler)

    # act
    response = signal.send(signal)

    # assert
    assert response == "ok"


def test_handler_with_wrong_signature() -> None:
    # arrange
    signal = CoolSignal()

    def handler(sender: Any, required_arg: Any) -> str:
        return "should not be called"

    signal.connect(handler)

    # act/assert
    with pytest.raises(TypeError):
        signal.send(signal)


@pytest.mark.parametrize(
    "falsy_value, expected_type",
    [
        (False, bool),
        (0, int),
        ("", str),
    ],
    ids=[
        "Test with 'False' (boolean)",
        "Test with '0' (integer)",
        "Test with '' (empty string)",
    ],
)
def test_handler_returns_falsy_value(falsy_value: Any, expected_type: type) -> None:
    """Verify signal returns the correct falsy value and type."""
    # arrange
    signal = CoolSignal()

    def handler(sender: Any) -> Any:
        return falsy_value

    # act
    signal.connect(handler)
    result = signal.send(signal)

    # assert
    assert result == falsy_value
    assert type(result) is expected_type
    if isinstance(falsy_value, bool):
        assert result is falsy_value


@pytest.fixture
def dynamic_handlers_setup() -> Dict[str, Any]:
    signal = CoolSignal()
    num_handlers: int = 100
    handlers_info: List[Tuple[Callable[..., Any], Optional[str]]] = []
    expected_responses_initial: Set[str] = set()
    target_value: str = "target_handler_result"
    target_handler_func: Optional[Callable[..., Any]] = None
    for i in range(num_handlers):
        return_value: Optional[str] = None
        if i == num_handlers // 2:
            return_value = target_value
        elif random.random() < 0.1:
            return_value = f"handler_{i}_result"

        def create_handler(rv: Optional[str]) -> Callable[..., Any]:
            def handler(sender: Any, **kwargs: Any) -> Optional[str]:
                return rv

            handler.__name__ = f"generated_handler_{i}_rv_{rv}"
            return handler

        handler_func = create_handler(return_value)
        handlers_info.append((handler_func, return_value))
        if return_value is not None:
            expected_responses_initial.add(return_value)
            if return_value == target_value:
                target_handler_func = handler_func
    for handler_func, _ in handlers_info:
        signal.connect(handler_func)
    return {
        "signal": signal,
        "handlers_info": handlers_info,
        "expected_responses_initial": expected_responses_initial,
        "target_handler_func": target_handler_func,
        "target_value": target_value,
        "num_handlers": num_handlers,
    }


def test_mass_handler_connect_and_send(dynamic_handlers_setup: Dict[str, Any]) -> None:
    # arrange
    signal = dynamic_handlers_setup["signal"]
    expected_responses: Set[str] = dynamic_handlers_setup["expected_responses_initial"]

    # act
    response = signal.send(signal, data="initial")

    # assert
    if not expected_responses:
        assert response is None
    else:
        assert response in expected_responses


def test_mass_handler_random_disconnect(dynamic_handlers_setup: Dict[str, Any]) -> None:
    # arrange
    signal = dynamic_handlers_setup["signal"]
    handlers_info: List[Tuple[Callable[..., Any], Optional[str]]] = (
        dynamic_handlers_setup["handlers_info"]
    )
    num_handlers: int = dynamic_handlers_setup["num_handlers"]
    all_handler_funcs: List[Callable[..., Any]] = [info[0] for info in handlers_info]
    handlers_to_disconnect_funcs: List[Callable[..., Any]] = random.sample(
        all_handler_funcs, num_handlers // 2
    )
    disconnected_handlers_set: Set[Callable[..., Any]] = set(
        handlers_to_disconnect_funcs
    )
    for handler_func in handlers_to_disconnect_funcs:
        signal.disconnect(handler_func)
    remaining_expected_responses: Set[str] = set()
    for handler_func, expected_rv in handlers_info:
        if handler_func not in disconnected_handlers_set:
            if expected_rv is not None:
                remaining_expected_responses.add(expected_rv)

    # act
    response = signal.send(signal, data="after_disconnect")

    # assert
    if not remaining_expected_responses:
        assert response is None
    else:
        assert response in remaining_expected_responses


def test_mass_handler_target_disconnect(dynamic_handlers_setup: Dict[str, Any]) -> None:
    # arrange
    signal = dynamic_handlers_setup["signal"]
    handlers_info: List[Tuple[Callable[..., Any], Optional[str]]] = (
        dynamic_handlers_setup["handlers_info"]
    )
    num_handlers: int = dynamic_handlers_setup["num_handlers"]
    target_handler_func: Optional[Callable[..., Any]] = dynamic_handlers_setup[
        "target_handler_func"
    ]
    all_handler_funcs: List[Callable[..., Any]] = [info[0] for info in handlers_info]
    handlers_to_disconnect_funcs: List[Callable[..., Any]] = random.sample(
        all_handler_funcs, num_handlers // 2
    )
    disconnected_handlers_set: Set[Callable[..., Any]] = set(
        handlers_to_disconnect_funcs
    )
    for handler_func in handlers_to_disconnect_funcs:
        signal.disconnect(handler_func)
    target_was_connected_initially: bool = target_handler_func is not None
    target_removed_randomly: bool = target_handler_func in disconnected_handlers_set
    disconnect_target_explicitly: bool = (
        target_was_connected_initially and not target_removed_randomly
    )
    if disconnect_target_explicitly and target_handler_func is not None:
        signal.disconnect(target_handler_func)
        disconnected_handlers_set.add(target_handler_func)
    final_expected_responses: Set[str] = set()
    for handler_func, expected_rv in handlers_info:
        if handler_func not in disconnected_handlers_set:
            if expected_rv is not None:
                final_expected_responses.add(expected_rv)

    # act
    response = signal.send(signal, data="after_target_disconnect")

    # assert
    if not final_expected_responses:
        assert response is None
    else:
        assert response in final_expected_responses


def test_emit_calls_handler_with_payload():
    # arrange
    signal = CoolSignal()
    received = {}

    def handler(payload):
        received["value"] = payload
        return payload

    signal.connect(handler)

    # act
    result = signal.emit(123)
    # assert
    assert received["value"] == 123
    assert result == 123


def test_emit_with_sender():
    # arrange
    signal = CoolSignal()
    received = {}

    def handler(sender, payload):
        received["sender"] = sender
        received["payload"] = payload
        return payload

    signal.connect(handler)

    # act
    result = signal.emit(42, sender="my_sender")
    # assert
    assert received["sender"] == "my_sender"
    assert received["payload"] == 42
    assert result == 42


def test_emit_multiple_handlers():
    # arrange
    signal = CoolSignal()
    called = []

    def handler1(payload):
        called.append(("h1", payload))
        return "one"

    def handler2(payload):
        called.append(("h2", payload))
        return "two"

    signal.connect(handler1)
    signal.connect(handler2)
    # act
    result = signal.emit(99)
    # assert
    assert ("h1", 99) in called
    assert ("h2", 99) in called
    assert result in ("one", "two")


def test_emit_complex_object():
    # arrange
    signal = CoolSignal()
    param = MyHandlerClass()

    def handler(param: MyHandlerClass):
        return 'ok'

    signal.connect(handler)

    # act
    result = signal.emit(param)


    # assert
    assert result == "ok"

# --- Async Tests ---


@pytest.mark.asyncio
async def test_async_send_returns_value_from_simple_handler() -> None:
    # arrange
    signal = CoolSignalAsync()

    async def handler(sender: Any) -> str:
        return "ok"

    # act
    signal.connect(handler)
    response = await signal.send(signal)
    # assert
    assert response == "ok"


@pytest.mark.asyncio
async def test_async_send_returns_none_when_handler_returns_none() -> None:
    # arrange
    signal = CoolSignalAsync()

    async def handler(sender: Any, **kwargs: Any) -> None:
        return None

    # act
    signal.connect(handler)
    response = await signal.send(signal, data="test")
    # assert
    assert response is None


@pytest.mark.asyncio
async def test_async_send_returns_a_non_none_value_among_multiple_handlers() -> None:
    # arrange
    signal = CoolSignalAsync()
    results: List[str] = []

    async def handler1(sender: Any, value: int) -> None:
        results.append(f"h1_received_{value}")
        return None

    async def handler2(sender: Any, value: int) -> str:
        results.append(f"h2_received_{value}")
        return f"ok_{value}"

    async def handler3(sender: Any, value: int) -> str:
        results.append(f"h3_received_{value}")
        return f"not_reached_{value}"

    # act
    signal.connect(handler1)
    signal.connect(handler2)
    signal.connect(handler3)
    response = await signal.send(signal, value=123)
    # assert
    possible_responses: Set[str] = {"ok_123", "not_reached_123"}
    assert response in possible_responses
    assert set(results) == {"h1_received_123", "h2_received_123", "h3_received_123"}


@pytest.mark.asyncio
async def test_async_handler_receives_correct_args_kwargs() -> None:
    # arrange
    signal = CoolSignalAsync()
    received_args: Optional[Tuple[Any, ...]] = None
    received_kwargs: Optional[Dict[str, Any]] = None

    async def handler(
        sender: Any,
        pos1: str = None,
        pos2: str = None,
        kw1: Optional[str] = None,
        kw2: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        nonlocal received_args, received_kwargs
        received_args = (pos1, pos2)
        received_kwargs = {"kw1": kw1, "kw2": kw2, **kwargs}
        return "received"

    # act
    signal.connect(handler)
    response = await signal.send(
        sender=signal, pos1="p1_val", pos2="p2_val", kw1="kw1_val", kw2="kw2_val"
    )
    # assert
    assert response == "received"
    assert received_args == ("p1_val", "p2_val")
    assert received_kwargs == {"kw1": "kw1_val", "kw2": "kw2_val"}


@pytest.mark.asyncio
async def test_async_bound_method_handler() -> None:
    # arrange
    signal = CoolSignalAsync()
    instance = MyHandlerClass()
    # act
    signal.connect(
        instance.async_method_handler
    )  # Assuming MyHandlerClass has an async version
    response = await signal.send(signal, value_to_set=42)
    # assert
    assert response == "async_set_42"
    assert instance.handled_value == 42


@pytest.mark.asyncio
async def test_async_send_with_no_handlers_returns_none() -> None:
    # arrange
    signal = CoolSignalAsync()
    # act
    response = await signal.send(signal, data="no_handlers")
    # assert
    assert response is None


@pytest.mark.asyncio
async def test_async_handler_raises_exception() -> None:
    # arrange
    signal = CoolSignalAsync()

    async def handler(sender: Any) -> None:
        raise ValueError("handler error")

    # act
    signal.connect(handler)

    # assert
    with pytest.raises(ValueError):
        await signal.send(signal)


@pytest.mark.asyncio
async def test_async_duplicate_handler_connection() -> None:
    # arrange
    signal = CoolSignalAsync()
    call_count: Dict[str, int] = {"count": 0}

    async def handler(sender: Any) -> str:
        call_count["count"] += 1
        return "ok"

    # act
    signal.connect(handler)
    signal.connect(handler)
    response = await signal.send(signal)
    # assert
    assert response == "ok"
    assert call_count["count"] == 1


@pytest.mark.asyncio
async def test_async_disconnect_non_connected_handler() -> None:
    # arrange
    signal = CoolSignalAsync()

    async def handler(sender: Any) -> str:
        return "ok"

    # act
    signal.disconnect(handler)
    signal.connect(handler)
    response = await signal.send(signal)
    # assert
    assert response == "ok"


@pytest.mark.asyncio
async def test_async_connect_sync_handler_raises_error() -> None:
    # arrange
    signal = CoolSignalAsync()

    def sync_handler(sender: Any) -> None:
        pass

    # act & assert
    with pytest.raises(TypeError, match="only supports async"):
        signal.connect(sync_handler)


@pytest.mark.asyncio
async def test_async_emit_calls_handler_with_payload():
    # arrange
    signal = CoolSignalAsync()
    received = {}

    async def handler(payload):
        received["value"] = payload
        return payload

    signal.connect(handler)

    # act
    result = await signal.emit("hello")

    # assert
    assert received["value"] == "hello"
    assert result == "hello"


@pytest.mark.asyncio
async def test_async_emit_with_sender():
    # arrange
    signal = CoolSignalAsync()
    received = {}

    async def handler(sender, payload):
        received["sender"] = sender
        received["payload"] = payload
        return payload

    signal.connect(handler)

    # act
    result = await signal.emit("async", sender="async_sender")

    # assert
    assert received["sender"] == "async_sender"
    assert received["payload"] == "async"
    assert result == "async"
