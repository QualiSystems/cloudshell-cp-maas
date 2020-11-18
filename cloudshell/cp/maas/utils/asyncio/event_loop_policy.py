import asyncio


def set_asyncio_any_thread_event_loop_policy():
    asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())


class AnyThreadEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    """Event loop policy that allows loop creation on any thread."""

    def get_event_loop(self):
        try:
            return super().get_event_loop()
        except (RuntimeError, AssertionError):
            loop = self.new_event_loop()
            self.set_event_loop(loop)
            return loop
