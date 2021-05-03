"""Fading in and out of view.

.. manim:: Fading

    class Fading(Scene):
        def construct(self):
            tex_in = Tex("Fade", "In").scale(3)
            tex_out = Tex("Fade", "Out").scale(3)
            self.play(FadeIn(tex_in, shift=DOWN, scale=0.66))
            self.play(ReplacementTransform(tex_in, tex_out))
            self.play(FadeOut(tex_out, shift=DOWN * 2, scale=1.5))

"""


__all__ = [
    "FadeOut",
    "FadeIn",
    "FadeInFrom",
    "FadeOutAndShift",
    "FadeOutToPoint",
    "FadeInFromPoint",
    "FadeInFromLarge",
    "VFadeIn",
    "VFadeOut",
    "VFadeInThenOut",
]

from typing import Callable, Optional, Union

import numpy as np

from ..animation.transform import Transform
from ..constants import DOWN, ORIGIN
from ..mobject.mobject import Mobject
from ..scene.scene import Scene
from ..utils.deprecation import deprecated
from ..utils.rate_functions import there_and_back


class _Fade(Transform):
    """Fade in a :class:`~.Mobject` in or out.

    Parameters
    ----------
    mobject
        The mobject to be faded in.
    shift
        The vector by which the mobject shifts while beeing faded.
    target_position
        The position to/from which the mobject moves while beeing faded in. In case
        another mobject is given as target position, its center is used.
    scale
        The factor by which the mobject is scaled initially before beeing rescaling to
        its original size while beeing faded in.

    """

    def __init__(
        self,
        mobject: Mobject,
        shift: Optional[np.ndarray] = None,
        target_position: Optional[Union[np.ndarray, Mobject]] = None,
        scale: float = 1,
        **kwargs
    ) -> None:
        self.point_target = False
        if shift is None:
            if target_position is not None:
                if isinstance(target_position, Mobject):
                    target_position = target_position.get_center()
                shift = target_position - mobject.get_center()
                self.point_target = True
            else:
                shift = ORIGIN
        self.shift_vector = shift
        print(self.shift_vector)
        self.scale_factor = scale
        super().__init__(mobject, **kwargs)

    def _create_faded_mobject(self, fadeIn: bool) -> Mobject:
        """Create a faded, shifted and scaled copy of the mobject.

        Parameters
        ----------
        fadeIn
            Whether the faded mobject is used to fade in.

        Returns
        -------
        Mobject
            The faded, shifted and scaled copy of the mobject.
        """
        faded_mobject = self.mobject.copy()
        faded_mobject.set_opacity(0)
        direction_modifier = -1 if fadeIn and not self.point_target else 1
        faded_mobject.shift(self.shift_vector * direction_modifier)
        faded_mobject.scale(self.scale_factor)
        return faded_mobject


class FadeIn(_Fade):
    """Fade in a :class:`~.Mobject`.

    Parameters
    ----------
    mobject
        The mobject to be faded in.
    shift
        The vector by which the mobject shifts while beeing faded in.
    target_position
        The position from which the mobject starts while beeing faded in. In case
        another mobject is given as target position, its center is used.
    scale
        The factor by which the mobject is scaled initially before beeing rescaling to
        its original size while beeing faded in.

    """

    def create_target(self):
        return self.mobject

    def create_starting_mobject(self):
        return self._create_faded_mobject(fadeIn=True)


class FadeOut(_Fade):
    """Fade out a :class:`~.Mobject`.

    Parameters
    ----------
    mobject
        The mobject to be faded out.
    shift
        The vector by which the mobject shifts while beeing faded out.
    target_position
        The position to which the mobject moves while beeing faded out. In case another
        mobject is given as target position, its center is used.
    scale
        The factor by which the mobject is scaled while beeing faded out.

    """

    def __init__(self, mobject: Mobject, **kwargs) -> None:
        super().__init__(mobject, remover=True, **kwargs)

    def create_target(self):
        return self._create_faded_mobject(fadeIn=False)

    def clean_up_from_scene(self, scene: Scene = None) -> None:
        super().clean_up_from_scene(scene)
        self.interpolate(0)


@deprecated(
    since="v0.6.0",
    until="v0.8.0",
    replacement="FadeIn",
    message="You can set a shift amount there.",
)
class FadeInFrom(FadeIn):
    def __init__(
        self, mobject: "Mobject", direction: np.ndarray = DOWN, **kwargs
    ) -> None:
        super().__init__(mobject, shift=-direction, **kwargs)


@deprecated(
    since="v0.6.0",
    until="v0.8.0",
    replacement="FadeOut",
    message="You can set a shift amount there.",
)
class FadeOutAndShift(FadeIn):
    def __init__(
        self, mobject: "Mobject", direction: np.ndarray = DOWN, **kwargs
    ) -> None:
        super().__init__(mobject, shift=direction, **kwargs)


@deprecated(
    since="v0.6.0",
    until="v0.8.0",
    replacement="FadeOut",
    message="You can set a target position there.",
)
class FadeOutToPoint(FadeOut):
    def __init__(
        self, mobject: "Mobject", point: Union["Mobject", np.ndarray] = ORIGIN, **kwargs
    ) -> None:
        super().__init__(mobject, target_position=point, **kwargs)


@deprecated(
    since="v0.6.0",
    until="v0.8.0",
    replacement="FadeIn",
    message="You can set a target position and scaling factor there.",
)
class FadeInFromPoint(FadeIn):
    def __init__(
        self, mobject: "Mobject", point: Union["Mobject", np.ndarray], **kwargs
    ) -> None:
        super().__init__(mobject, target_position=point, scale=0, **kwargs)


@deprecated(
    since="v0.6.0",
    until="v0.8.0",
    replacement="FadeIn",
    message="You can set a scaling factor there.",
)
class FadeInFromLarge(FadeIn):
    def __init__(self, mobject: "Mobject", scale_factor: float = 2, **kwargs) -> None:
        super().__init__(mobject, scale=scale_factor, **kwargs)


@deprecated(since="v0.6.0", until="v0.8.0", replacement="FadeIn")
class VFadeIn(FadeIn):
    def __init__(self, mobject: "Mobject", **kwargs) -> None:
        super().__init__(mobject, **kwargs)


@deprecated(since="v0.6.0", until="v0.8.0", replacement="FadeOut")
class VFadeOut(FadeOut):
    def __init__(self, mobject: "Mobject", **kwargs) -> None:
        super().__init__(mobject, **kwargs)


@deprecated(since="v0.6.0", until="v0.8.0")
class VFadeInThenOut(FadeIn):
    def __init__(
        self,
        mobject: "Mobject",
        rate_func: Callable[[float], float] = there_and_back,
        **kwargs
    ):
        super().__init__(mobject, remover=True, rate_func=rate_func, **kwargs)
