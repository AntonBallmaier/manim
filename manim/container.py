"""
Abstract base class for several objects used by manim.  In particular, both
:class:`~.Scene` and :class:`~.Mobject` inherit from Container.
"""


__all__ = ["Container"]


from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Union

from .utils.simple_functions import get_parameters
from . import logger

Updater = Union[Callable[["Container"], None], Callable[["Container", float], None]]


class Container(ABC):
    """Abstract base class for several objects used by manim.  In particular, both
    :class:`~.Scene` and :class:`~.Mobject` inherit from Container.

    Parameters
    ----------
    kwargs : Any

    """

    def __init__(self, **kwargs):
        if kwargs:
            logger.debug("Container received extra kwargs: %s", kwargs)

        if hasattr(self, "CONFIG"):
            logger.error(
                "CONFIG has been removed from ManimCommunity. Please use keyword arguments instead."
            )

        self.updaters = []
        self.time_based_updaters = 0

    @abstractmethod
    def add(self, *items):
        """Abstract method to add items to Container.

        Parameters
        ----------
        items : Any
            Objects to be added.
        """

    @abstractmethod
    def remove(self, *items):
        """Abstract method to remove items from Container.

        Parameters
        ----------
        items : Any
            Objects to be added.
        """

    def add_updater(
        self,
        updater: Updater,
        *,
        use_time_difference: Optional[bool] = None,
        index: Optional[int] = None,
        call_updater: bool = False,
    ) -> "Container":
        """Add an update function to this container.

        Update functions, or updaters in short, are functions that are applied to the
        Container in every frame.

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
        :class:`Container`
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

        # Wrap updaters to allow calling all of them using container and dt as parameter
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

    def clear_updaters(self) -> "Container":
        """Remove every updater.

        Returns
        -------
        :class:`Container`
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

    def remove_updater(self, updater: Updater) -> "Container":
        """Remove an updater.

        If the same updater is applied multiple times, every instance gets removed.

        Parameters
        ----------
        updater
            The update function to be removed.


        Returns
        -------
        :class:`Container`
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

    def apply_updaters(self, dt: float = 0) -> "Container":
        """Apply all updaters.

        Parameters
        ----------
        dt
            The parameter ``dt`` to pass to the update functions. Usually this is the
            time in seconds since the last call of ``apply_updaters``.

        Returns
        -------
        :class:`Container`
            ``self``

        See Also
        --------
        :meth:`add_updater`
        :meth:`get_updaters`

        """
        for updater in self.updaters:
            updater(self, dt)
        return self
