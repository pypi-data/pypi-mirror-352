import asyncio
import functools
import inspect


def retry_forever(start_message: str, error_message: str, delay: int = 10):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            sig = inspect.signature(func)
            parameters = {
                param.name: kwargs.get(param.name) for param in sig.parameters.values()
            }
            formatted_start_message = start_message.format(**parameters)
            self.logger.debug(formatted_start_message)
            while True:
                try:
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    self.logging_error(e, error_message)
                await asyncio.sleep(delay)

        return wrapper

    return decorator
