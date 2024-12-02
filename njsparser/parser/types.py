from typing import Any

# https://github.com/vercel/next.js/blob/965fe24d91d08567751339756e51f2cf9d0e3188/packages/next/src/server/app-render/types.ts#L224-L243
class InitialRSCPayload:
    def __init__(
        self,
        b: str,
        # p: str,
        # c: list[str],
        # i: bool,
        # f: Any, # list[FlightDataPath],
        # m: set[str] | None,
        # G: None, # [React.ComponentType<any>, React.ReactNode | undefined]
        # s: bool,
        # S: bool,
        **kwargs,
    ) -> None:
        self._b = b

    @property
    def build_id(self):
        """The Build ID.

        Returns:
            str: The build id.
        """
        return self._b