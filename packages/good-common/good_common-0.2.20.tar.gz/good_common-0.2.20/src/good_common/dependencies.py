import copy
import typing
import asyncio
from fast_depends.library import CustomField
from loguru import logger
import inspect

T = typing.TypeVar("T")


class BaseProvider(CustomField, typing.Generic[T]):
    __override_class__: typing.ClassVar = None

    @classmethod
    def provide(cls, *args, **kwargs) -> T:
        _kwargs = kwargs.copy()
        _target_cls = cls.__override_class__ or cls.__bases__[1]

        _args = inspect.getfullargspec(_target_cls.__init__)

        if not _args.varkw:
            _remove_args = set()
            for k, v in kwargs.items():
                if k not in _args.args:
                    # logger.debug(f"Removing {k}")
                    _remove_args.add(k)
                    _kwargs.pop(k)

            if _remove_args:
                logger.debug(f"Removing {len(_remove_args)} args: {_remove_args}")

        kwargs = _kwargs

        if cls.__override_class__ is not None:
            return cls.__override_class__(*args, **kwargs)
        else:
            return cls.__bases__[1](*args, **kwargs)

    def __init__(self, *args, _debug: bool = False, **kwargs):
        super().__init__(cast=False)
        self._args = args
        self._kwargs = kwargs
        self._debug = _debug

    def initializer(
        self,
        cls_args: typing.Tuple[typing.Any, ...],
        cls_kwargs: typing.Dict[str, typing.Any],
        fn_kwargs: typing.Dict[str, typing.Any],
    ):
        return cls_args, (cls_kwargs or {}) | (fn_kwargs or {})

    def use(self, /, **kwargs: typing.Dict[str, typing.Any]):
        if self._debug:
            logger.debug(f"Using {self.__class__.__name__}: {kwargs}")
        kwargs = super().use(**kwargs)
        if self.param_name:
            _args, _kwargs = self.initializer(
                cls_args=copy.copy(self._args),
                cls_kwargs=copy.copy(self._kwargs),
                fn_kwargs=kwargs,
            )
            kwargs[self.param_name] = self.provide(*_args, **_kwargs)  # type: ignore
        return kwargs

    def get(self, **kwargs) -> T:
        self.param_name = "_default"
        return self.use(**kwargs).get(self.param_name)  # type: ignore


class AsyncBaseProvider(CustomField, typing.Generic[T]):
    __override_class__: typing.ClassVar = None

    # def get(self, **kwargs) -> T:
    #     self.param_name = "_default"

    #     try:
    #         loop = asyncio.get_running_loop()

    #         return loop.run_until_complete(self.use(**kwargs)).get(self.param_name)  # type: ignore
    #     except RuntimeError:
    #         return asyncio.run(self.use(**kwargs)).get(self.param_name)

    async def get(self, **kwargs) -> T:
        self.param_name = "_default"
        return (await self.use(**kwargs)).get(self.param_name)

    @classmethod
    async def provide(cls, *args, **kwargs) -> T:
        if cls.__override_class__ is not None:
            return cls.__override_class__(*args, **kwargs)
        else:
            return cls.__bases__[1](*args, **kwargs)

    def __init__(self, *args, _debug: bool = False, **kwargs):
        super().__init__(cast=False)
        self._args = args
        self._kwargs = kwargs
        self._debug = _debug

    def initializer(
        self,
        cls_args: typing.Tuple[typing.Any, ...],
        cls_kwargs: typing.Dict[str, typing.Any],
        fn_kwargs: typing.Dict[str, typing.Any],
    ):
        return cls_args, cls_kwargs

    async def use(self, /, **kwargs: typing.Dict[str, typing.Any]):
        if self._debug:
            logger.debug(f"Using {self.__class__.__name__}: {kwargs}")
        kwargs = super().use(**kwargs)
        if self.param_name:
            _args, _kwargs = self.initializer(
                cls_args=copy.copy(self._args),
                cls_kwargs=copy.copy(self._kwargs),
                fn_kwargs=kwargs,
            )
            kwargs[self.param_name] = await self.provide(*_args, **_kwargs)  # type: ignore

        await self.on_initialize(
            kwargs[self.param_name],
            **{k: v for k, v in _kwargs.items() if k != self.param_name},
        )
        return kwargs

    async def on_initialize(self, instance, **kwargs):
        pass

    # async def get(self, **kwargs) -> T:
    #     self.param_name = "_default"
    #     return (await self.use(**kwargs)).get(self.param_name)  # type: ignore
