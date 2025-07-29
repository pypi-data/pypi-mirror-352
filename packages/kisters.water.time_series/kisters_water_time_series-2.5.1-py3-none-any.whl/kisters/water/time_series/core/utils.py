from __future__ import annotations

import asyncio
import itertools
from collections.abc import Awaitable, Callable, Iterable
from typing import Any, Literal, TypeVar

import pandas as pd
from pydantic import BaseModel

BaseModelT = TypeVar("BaseModelT", bound=BaseModel)

try:
    from pydantic import ConfigDict, Field, field_validator, model_validator, v1  # noqa: F401

    class Model(BaseModel):
        model_config = ConfigDict(
            extra="forbid",
            use_enum_values=True,
            coerce_numbers_to_str=True,  # So str types behave the same as in pydantic v1
        )

    class AllowExtraModel(Model):
        model_config = ConfigDict(extra="allow")

    class ArbitraryExtraModel(AllowExtraModel):
        model_config = ConfigDict(arbitrary_types_allowed=True)

    def model_validate(model: type[BaseModelT] | BaseModelT, obj: Any) -> BaseModelT:
        return model.model_validate(obj)

    def model_dump(model: BaseModelT, **kwargs: Any) -> dict[str, Any]:
        return model.model_dump(**kwargs)

    def model_copy(model: BaseModelT, **kwargs: Any) -> BaseModelT:
        return model.model_copy(**kwargs)

except ImportError:
    from pydantic import Extra, Field, root_validator, validator

    class Model(BaseModel):  # type: ignore
        class Config:
            # Forbid by default to avoid common errors such as misnamed fields
            extra = Extra.forbid
            # Makes serialization clearer
            use_enum_values = True

    class AllowExtraModel(Model):  # type: ignore
        class Config:
            extra = Extra.allow

    class ArbitraryExtraModel(AllowExtraModel):  # type: ignore
        class Config:
            arbitrary_types_allowed = True
            underscore_attrs_are_private = True

    def field_validator(  # type: ignore
        __field: str,
        *fields: str,
        mode: Literal["before", "after"] = "after",
        check_fields: bool | None = None,
    ) -> Callable[[Any], Any]:
        return validator(__field, *fields, pre=mode != "after", always=True)

    def model_validator(  # type: ignore
        *,
        mode: Literal["wrap", "before", "after"],
    ) -> Any:
        return root_validator(pre=mode != "after")  # type: ignore

    def model_validate(model: type[BaseModelT] | BaseModelT, obj: Any) -> BaseModelT:
        return model.parse_obj(obj)

    def model_dump(model: BaseModelT, **kwargs: Any) -> dict[str, Any]:
        return model.dict(**kwargs)

    def model_copy(model: BaseModelT, **kwargs: Any) -> BaseModelT:
        return model.copy(**kwargs)


def make_iterable(value: Any) -> Iterable[Any]:
    """Make an infinite iterable if it's not iterable, or it's string."""
    if not isinstance(value, Iterable) or isinstance(value, (str, pd.DataFrame)):
        return itertools.repeat(value)
    return value


T = TypeVar("T")


async def bulk_concurrent(
    awaitables: Iterable[Awaitable[T]],
    concurrency_limit: int = 32,
    error_handling: Literal["default", "return", "raise"] = "default",
    default_value: Any = None,
    default_factory: Callable[[], Any] | None = None,
) -> list[T | Exception]:
    """
    Utility method to asyncio gather awaitables without exceeding the concurrency_limit.

    Args:
        awaitables: The list of awaitables.
        concurrency_limit: The maximum concurrency tolerated.
        error_handling: If "default" return a default value, if "return" will return error objects
          and if "raise" will raise on first encountered error.
        default_value: The default value.
        default_factory: The default factory provider.

    Returns:
        The list of results.
    """
    sem = asyncio.Semaphore(concurrency_limit)

    async def task_wrapper(task: Awaitable[Any]) -> Any:
        try:
            result = await task
        except Exception as e:
            if error_handling == "raise":
                raise  # Python catches here this raise, then executes finally then raises this
            if error_handling == "return":
                result = e
            elif error_handling == "default":
                result = default_factory() if default_factory is not None else default_value
        finally:
            sem.release()
        return result

    tasks = []
    for awaitable in awaitables:
        await sem.acquire()
        tasks.append(asyncio.create_task(task_wrapper(awaitable)))

    for _ in range(concurrency_limit):
        await sem.acquire()
    return [t.result() for t in tasks]


__all__ = [
    "Field",
    "field_validator",
    "model_copy",
    "model_validate",
    "model_dump",
    "bulk_concurrent",
    "make_iterable",
    "model_validator",
    "Model",
    "AllowExtraModel",
    "ArbitraryExtraModel",
]
