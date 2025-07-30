"""The core module for the pCubit package.

"""

import cubit
import numpy as np
from .base import EllipsoidBase, EllipsoidsBase


def cubit_cmd(string, silent=True):
    """Sends arbitrary commands to Cubit, asserting their success.

    Args:
        string (str): The command string.
        silent (bool, optional, default=True): Whether to silence Cubit.

    """
    if silent:
        assert cubit.silent_cmd(string)
    else:
        assert cubit.cmd(string)


def cubit_init(offscreen_graphics=False):
    """Starts a instance of Cubit, quietly, with developer settings on.

    Args:
        offscreen_graphics (bool, optional, default=False):
            Whether to enable graphics (offscreen) for things like screenshots.

    """
    if offscreen_graphics:
        cubit.init([
            'cubit', '-driver', 'offscreen', '-nojournal', '-noecho',
            '-warning', 'off', '-information', 'off'
        ])
        cubit_cmd('graphics window create')
    else:
        cubit.init([
            'cubit', '-nographics', '-nojournal', '-noecho',
            '-warning', 'off', '-information', 'off'
        ])
    cubit_cmd('reset')
    cubit_cmd('set developer on')


class Ellipsoid(EllipsoidBase):
    """The core class for an ellipsoid.

    Attributes:
        placed (bool): Whether or not the ellipsoid has placed in the geometry.

    """
    def __init__(self, **kwargs):
        EllipsoidBase.__init__(self, **kwargs)
        self.placed = False

    def __repr__(self):
        return self.__class__.__name__ + \
            f'(id={self.get_id()}, ' + \
            f'adopted={self.adopted}, ' + \
            f'placed={self.placed}, ' + \
            f'location={self.location}, ' + \
            f'radii={self.radii}, ' + \
            f'angles={self.angles})'

    def place(self, block_id=None):
        """Places the ellipsoid in an existing geometry.

        The ellipsoid is placed by subtracting the portion of
        any volumes that overlap with the ellipsoid volume.
        If the ellipsoid is a pore, the ellipsoid volume is then deleted.
        Otherwise, the ellipsoid volume is added to a new element block.

        Args:
            block_id (int, optional, default=None):
                The id for the element block that the ellipsoid will be
                added to, if not a pore. If an id is not specified,
                the ellipsoid will be added to a new element block.

        Example:
            Place an single particle in a unit cube:

                >>> from pcubit import cubit_cmd, cubit_init, Particle
                >>> cubit_init()
                >>> cubit_cmd('brick x 1')
                >>> cubit_cmd('block 1 volume 1')
                >>> particle = Particle(
                ...     location=[0, 0, 0],
                ...     radii=[0.23, 0.55, 0.3],
                ...     angles=[0, 1, 2]
                ... )
                >>> particle.place()

        """
        assert self.placed is False
        original_volume_id_list = list(cubit.get_entities('volume'))
        cubit_cmd('create sphere radius 1')
        ellipsoid_volume_id = cubit.get_last_id('volume')
        cubit_cmd(
            f'volume {ellipsoid_volume_id} ' +
            f'scale x {self.radii[0]} y {self.radii[1]} z {self.radii[2]}'
        )
        axis = self.axis_angle[0]
        angle = np.degrees(self.axis_angle[1])
        cubit_cmd(
            f'rotate volume {ellipsoid_volume_id} ' +
            f'about {axis[0]} {axis[1]} {axis[2]} angle {angle}'
        )
        cubit_cmd(
            f'move volume {ellipsoid_volume_id} location ' +
            f'{self.location[0]} {self.location[1]} {self.location[2]}'
        )
        if self.__class__.__name__ == 'Particle':
            if block_id is None:
                block_id = max(cubit.get_entities('block')) + 1
            cubit_cmd(f'block {block_id} add volume {ellipsoid_volume_id}')
        new_volume_id = cubit.get_last_id('volume')
        for volume_id in original_volume_id_list:
            volume_block_id = cubit.get_block_id('volume', volume_id)
            cubit_cmd(
                f'remove overlap volume {ellipsoid_volume_id} {volume_id}' +
                f'modify volume {volume_id}'
            )
            check_new_volume_id = cubit.get_last_id('volume')
            matrix_ellipsoid_surface_id = cubit.get_last_id('surface')
            if check_new_volume_id != new_volume_id:
                new_volume_id = check_new_volume_id
                cubit_cmd(
                    f'block {volume_block_id} add volume {new_volume_id}'
                )
        if self.__class__.__name__ == 'Pore':
            cubit_cmd(f'delete volume {ellipsoid_volume_id}')
        else:
            cubit.set_entity_name('volume', ellipsoid_volume_id, self.name)
            ellipsoid_surface_ids = \
                cubit.get_relatives('volume', ellipsoid_volume_id, 'surface')
            assert len(ellipsoid_surface_ids) == 1
            ellipsoid_surface_id = ellipsoid_surface_ids[0]
            cubit.cmd(
                f'merge surface {ellipsoid_surface_id}' +
                f'with surface {matrix_ellipsoid_surface_id}'
            )
        self.placed = True


class Particle(Ellipsoid):
    """The core class for a particle.

    """
    def __init__(self, **kwargs):
        Ellipsoid.__init__(self, **kwargs)


class Pore(Ellipsoid):
    """The core class for a pore.

    """
    def __init__(self, **kwargs):
        Ellipsoid.__init__(self, **kwargs)


class Ellipsoids(EllipsoidsBase):
    """The core class for a set of ellipsoids.

    """
    @property
    def child_class(self):
        """The :class:`Ellipsoid` class considered to be the child class.

        Returns:
            Ellipsoid: The child class.

        """
        return Ellipsoid

    def __init__(self, **kwargs):
        EllipsoidsBase.__init__(self, **kwargs)

    def place(self, **kwargs):
        """Sequentially places the ellipsoids in an existing geometry.

        A new element block is created using the next available block id,
        and each ellipsoid is added to that element block during placement.

        Args:
            kwargs: Arbitrary keyword arguments.
                Passed to :meth:`~.Ellipsoid.place`.

        """
        block_id = max(cubit.get_entities('block')) + 1
        cubit_cmd(f'create block {block_id}')
        cubit_cmd(f'block {block_id} name "{self.name}"')
        for child in self():
            self.child_class.place(
                child, block_id=block_id, **kwargs
            )


class Particles(Ellipsoids):
    """The core class for a set of particles.

    """
    @property
    def child_class(self):
        """The :class:`Particle` class considered to be the child class.

        Returns:
            Particle: The child class.

        """
        return Particle

    def __init__(self, **kwargs):
        Ellipsoids.__init__(self, **kwargs)


class Pores(Ellipsoids):
    """The core class for a set of pores.

    """
    @property
    def child_class(self):
        """The :class:`Pore` class considered to be the child class.

        Returns:
            Pore: The child class.

        """
        return Pore

    def __init__(self, **kwargs):
        Ellipsoids.__init__(self, **kwargs)
