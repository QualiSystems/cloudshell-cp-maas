


class CSSSHKey:
    def __init__(self, key):
        self.key = key

    async def delete(self):
        """Delete this partition."""
        await self.key._handler.delete(
            id=self.key.id,
        )
