"""The base module for the pCubit package.

"""

import numpy as np
import numpy.linalg as la
from scipy.spatial.transform import Rotation


class OrientationBase:
    """The base class for object orientation.

    """
    @property
    def location(self):
        """The location of the object.

        Returns:
            numpy.ndarray: The three-dimensional coordinates.

        """
        return self.__location

    @property
    def angles(self):
        """The Euler angles of the object.

        Returns:
            numpy.ndarray: The three Euler angles.

        """
        return self.__angles

    @property
    def rotation(self):
        """The rotation matrix of the object.

        Returns:
            numpy.ndarray: The three-dimensional rotation matrix.

        """
        return self.__rotation

    @property
    def vector(self):
        """The rotation vector of the object.

        Returns:
            numpy.ndarray: The three-dimensional rotation vector.

        """
        return self.__vector

    @property
    def axis_angle(self):
        """The rotation axis and angle of the object.

        Returns:
            tuple:

                - (*numpy.ndarray*) -
                  The three-dimensional rotation axis.
                - (*numpy.ndarray*) -
                  The angle of rotation about the axis.

        """
        return self.__axis_angle

    def __init__(self, location=None, angles=None):
        self.__location = location
        if angles is None:
            self.__angles = np.array([0, 0, 0])
        else:
            self.__angles = np.array(angles)
        self.__rotation = Rotation.from_euler('zyx', self.__angles)
        self.__vector = self.__rotation.as_rotvec()
        angle = la.norm(self.__vector)
        if angle == 0:
            self.__axis_angle = np.array([0, 0, 0]), 0
        else:
            self.__axis_angle = self.__vector/angle, angle


class EllipsoidBase(OrientationBase):
    """The base class for an ellipsoid.

    Attributes:
        adopted (bool): Whether or not the ellipsoid has been adopted
            by an instance of :class:`EllipsoidsBase`.

    """
    @property
    def radii(self):
        """The radii of the ellipsoid.

        Returns:
            numpy.ndarray: The three radii.

        """
        return self.__radii

    @property
    def volume(self):
        """The volume of the ellipsoid.

        Returns:
            float: The volume.

        """
        return 4*np.pi/3*np.prod(self.__radii)

    @property
    def data(self):
        """The full data of the ellipsoid (location, radii, angles).

        Returns:
            numpy.ndarray: The ellipsoid data.

        """
        return self.__data

    @property
    def name(self):
        """The name of the ellipsoid, based on the id.

        Returns:
            str: The name of the ellipsoid.

        """
        return self.__name

    def __init__(self, radii=None, **kwargs):
        OrientationBase.__init__(self, **kwargs)
        self.__radii = np.array(radii)
        self.__name = self.__class__.__name__ + '_' + str(self.get_id())
        self.adopted = False
        self.__data = [self.location, self.radii, self.angles]

    def __call__(self):
        return self

    def __repr__(self):
        return self.__class__.__name__ + \
            f'(id={self.get_id()}, ' + \
            f'adopted={self.adopted}, ' + \
            f'location={self.location}, ' + \
            f'radii={self.radii}, ' + \
            f'angles={self.angles})'

    def get_id(self):
        """Get the unique id (the Python object id).

        Returns:
            int: The unique id.

        """
        return id(self)


class ParticleBase(EllipsoidBase):
    """The base class for a particle.

    """
    def __init__(self, **kwargs):
        EllipsoidBase.__init__(self, **kwargs)


class PoreBase(EllipsoidBase):
    """The base class for a pore.

    """
    def __init__(self, **kwargs):
        EllipsoidBase.__init__(self, **kwargs)


class EllipsoidsBase:
    """The base class for a set of ellipsoids.

    """
    @property
    def children(self):
        """The adopted instances of :class:`EllipsoidBase`.

        Returns:
            tuple: The children.

        """
        return self.__children

    @property
    def child_class(self):
        """The :class:`EllipsoidBase` class considered to be the child class.

        Returns:
            EllipsoidBase: The child class.

        """
        return EllipsoidBase

    @property
    def name(self):
        """The name of the set of ellipsoids, based on the id.

        Returns:
            str: The name of the set of ellipsoids.

        """
        return self.__name

    def __init__(self):
        self.__children = ()
        self.__name = self.__class__.__name__ + '_' + str(self.get_id())

    def __call__(self):
        return self.__children

    def __repr__(self):
        string = self.__class__.__name__ + '('
        if len(self.__children) == 0:
            string += '\n\tnone'
        else:
            for child in self.__children:
                string += '\n\t' + child. __repr__()
        return string + '\n)'

    def get_id(self):
        """Get the unique id (the Python object id).

        Returns:
            int: The unique id.

        """
        return id(self)

    def get_ids(self):
        """Get the unique ids (the Python object ids) of all children.

        Returns:
            list: The unique ids.

        """
        ids = []
        for child in self.__children:
            ids.append(child.get_id())
        return ids

    def get_data(self):
        """Get the data of all children.

        Returns:
            numpy.ndarray: The data.

        """
        data = []
        for child in self.__children:
            data.append(child.data)
        return np.array(data)

    def adopt(self, orphans):
        """Adopt orphan ellipsoids.

        Args:
            orphans (EllipsoidBase): A tuple of orphan ellipsoids.

        """
        if isinstance(orphans, tuple) is False:
            orphans = (orphans,)
        for orphan in orphans:
            assert type(orphan) is self.child_class
            assert orphan.get_id() not in self.get_ids()
            assert orphan.adopted is False
            self.__children += (orphan,)
            orphan.adopted = True

    def disown(self, children):
        """Disown children ellipsoids.

        Args:
            children (EllipsoidBase): A tuple of children ellipsoids.

        """
        if isinstance(children, tuple) is False:
            children = (children,)
        for child in children:
            assert type(child) is self.child_class
            assert child.get_id() in self.get_ids()
            assert child.adopted is True
            remaining_children = list(self.__children)
            remaining_children.remove(child)
            self.__children = tuple(remaining_children)
            child.adopted = False

    def spawn(self, data=None, **kwargs):
        """Spawn and automatically adopt ellipsoids.

        Args:
            - data (numpy.ndarray): The data for a set of ellipsoids.
            - kwargs (foo): Arbitrary keyword arguments.
                Passed to the constructor for the child class if no data.

        """
        if data is not None:
            for row in data:
                self.adopt(self.child_class(
                    location=row[0:3], radii=row[3:6], angles=row[6:9]
                ))
        else:
            self.adopt(self.child_class(**kwargs))


class ParticlesBase(EllipsoidsBase):
    """The base class for a set of particles.

    """
    @property
    def child_class(self):
        """The :class:`ParticleBase` class considered to be the child class.

        Returns:
            ParticleBase: The child class.

        """
        return ParticleBase

    def __init__(self, **kwargs):
        EllipsoidsBase.__init__(self, **kwargs)


class PoresBase(EllipsoidsBase):
    """The base class for a set of pores.

    """
    @property
    def child_class(self):
        """The :class:`PoreBase` class considered to be the child class.

        Returns:
            PoreBase: The child class.

        """
        return PoreBase

    def __init__(self, **kwargs):
        EllipsoidsBase.__init__(self, **kwargs)
