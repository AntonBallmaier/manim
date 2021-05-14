"""Abstract base class for updatable objects.

Updater functions can be attached to Updatables. These get called for every frame of an
animation. 

In particular, both :class:`~.Scene` and :class:`~.Mobject` inherit from Updatable.
"""


__all__ = ["Updatable"]


from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Union

from .utils.simple_functions import get_parameters
from . import logger

Updater = Union[Callable[["Updatable"], None], Callable[["Updatable", float], None]]


class Updatable(ABC):
    """Abstract base class for updatable objects.

    Updater functions can be attached to Updatables. These get called for every frame of
    an animation.

    In particular, both :class:`~.Scene` and :class:`~.Mobject` inherit from Updatable.

    Parameters
    ----------
    kwargs : Any
        Unused kwargs passed from subclass constructors. They are logged as debug
        message.

    """

    def __init__(self, **kwargs):
        if kwargs:
            logger.debug("Updatable received extra kwargs: %s", kwargs)

        if hasattr(self, "CONFIG"):
            logger.error(
                "CONFIG has been removed from ManimCommunity. Please use keyword arguments instead."
            )

        self.updaters = []
        self.time_based_updaters = 0

    def add_updater(
        self,
        updater: Updater,
        *,
        use_time_difference: Optional[bool] = None,
        index: Optional[int] = None,
        call_updater: bool = False,
    ) -> "Updatable":
        """Add an update function to this updatable.

        Update functions, or updaters in short, are functions that are applied to the
        Updatable in every frame.

        Parameters
        ----------
        updater
            The update function to be added. Whenever :meth:`update` is called, this
            updater gets called using ``self`` as the first parameter. The updater can
            have a second parameter ``dt``. If it uses this parameter, it gets called
            using a second value ``dt``, usually representing the time in seconds since
            the last call of :meth:`update`.
        index
            The index at which the new updater should be added in ``self.updaters``. In
            case ``index`` is ``None`` the updater will be added at the end.
        call_updater
            Wheather or not to call the updater initially. If ``True``, the updater will
            be called using ``dt=0``.

        Returns
        -------
        :class:`Updatable`
            ``self``

        See also
        --------
        :meth:`get_updaters`
        :meth:`remove_updater`
        """

        # Test if updater is time based and wheather to use time difference
        parameters = list(get_parameters(updater).keys())
        time_based = len(parameters) > 1
        if time_based:
            if parameters[1] not in ["t", "time"] and use_time_difference is None:
                use_time_difference = True
            use_time_difference = bool(use_time_difference)

        # Wrap updaters to allow calling all of them using updatable and dt as parameter
        if time_based:
            if use_time_difference:
                unified_updater = updater
            else:

                def unified_updater(mob, dt):
                    unified_updater.total_time += dt
                    updater(mob, unified_updater.total_time)

                unified_updater.total_time = 0
        else:
            unified_updater = lambda mob, dt: updater(mob)

        unified_updater.time_based = time_based
        unified_updater.base_func = updater  # used to enable removing

        self.time_based_updaters += time_based

        if index is None:
            self.updaters.append(unified_updater)
        else:
            self.updaters.insert(index, unified_updater)

        if call_updater:
            unified_updater(self, 0)

        return self

    def clear_updaters(self) -> "Updatable":
        """Remove every updater.

        Returns
        -------
        :class:`Updatable`
            ``self``

        See also
        --------
        :meth:`remove_updater`
        :meth:`add_updater`
        :meth:`get_updaters`

        """
        self.updaters = []
        self.time_based_updaters = 0
        return self

    def remove_updater(self, updater: Updater) -> "Updatable":
        """Remove an updater.

        If the same updater is applied multiple times, every instance gets removed.

        Parameters
        ----------
        updater
            The update function to be removed.


        Returns
        -------
        :class:`Updatable`
            ``self``

        See also
        --------
        :meth:`clear_updaters`
        :meth:`add_updater`
        :meth:`get_updaters`

        """

        filtered = []

        for wrapped_updater in self.updaters:
            if wrapped_updater.base_func is not updater:
                filtered.append(wrapped_updater)
            else:
                self.time_based_updaters -= wrapped_updater.time_based
        self.updaters = filtered
        return self

    def get_updaters(self) -> List[Updater]:
        """Return all updaters.

        Returns
        -------
        List[:class:`Callable`]
            The list of updaters.

        See Also
        --------
        :meth:`add_updater`

        """
        return self.updaters

    def has_time_based_updater(self) -> bool:
        """Test if ``self`` has a time based updater.

        Returns
        -------
        class:`bool`
            ``True`` if at least one updater uses a time parameter, ``False`` otherwise.

        """
        return bool(self.time_based_updaters)

    def apply_updaters(self, dt: float = 0) -> "Updatable":
        """Apply all updaters.

        Parameters
        ----------
        dt
            The parameter ``dt`` to pass to the update functions. Usually this is the
            time in seconds since the last call of ``apply_updaters``.

        Returns
        -------
        :class:`Updatable`
            ``self``

        See Also
        --------
        :meth:`add_updater`
        :meth:`get_updaters`

        """
        for updater in self.updaters:
            updater(self, dt)
        return self
