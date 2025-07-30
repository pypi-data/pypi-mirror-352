"""The statistics module for the pCubit package.

"""

import cubit
import numpy as np
import scipy.spatial as sp
from scipy.special import factorial
from scipy.spatial.transform import Rotation
from .core import Particles, Pores


class Poisson:
    r"""The Poisson distribution or point process class.

    Calling an instance of the class with the number(s) of occurrences as the
    argument(s) returns the probability of those number(s) of occurrences.

    For :math:`M` disjoint intervals, the Poisson distribution describing
    the probability that there are :math:`n_j` occurrences
    in the :math:`j\mathrm{th}` th interval is

    .. math::
        P(\mathbf{n}) =
        \prod_{j=1}^M
            \frac{(\lambda s_j)^{n_j}}{n_j!}
            \, e^{\lambda s_j}
        ,

    where :math:`s_j` is size of the :math:`j\mathrm{th}` interval,
    and :math:`\lambda` is the Poisson process intensity.

    **Properties**

        Let the sum over the probabilities be denoted as

        .. math::
            \langle f\rangle \equiv
            \sum_{i=1}^M \sum_{n_i=0}^\infty
                P(\mathbf{n}) f(\mathbf{n})
            .

        The probability distribution is normalized,

        .. math::
            \langle 1 \rangle = 1
            ,

        and each expected number of occurences
        is intensity times multiplying the size,

        .. math::
            \langle n_k \rangle = \lambda s_k
            .

        If the sizes are relative to the total size,
        i.e. if the sizes are discrete probabilities,
        the expected total number of occurences is :math:`\lambda`.

    """
    @property
    def intensity(self):
        r"""The Poisson intensity, :math:`\lambda`.
        In certain cases, this is also the expectation value
        for the (total) number of occurrences.

        Returns:
            float: The intensity.

        """
        return self.__lambda

    @property
    def sizes(self):
        """The size(s) of the disjoint intervals.

        Returns:
            numpy.ndarray: The size(s).

        """
        return self.__s

    def __init__(self, intensity=None,
                 sizes=np.array([1]), seed=None):
        # assert intensity > 0
        self.__lambda = intensity
        self.__s = np.array(sizes)
        if seed is None:
            self.__sampler = np.random.default_rng().poisson
        else:
            self.__sampler = np.random.default_rng(seed=seed).poisson

    def __call__(self, occurrences):
        n_vec = np.array(occurrences)
        # assert len(n_vec) == len(self.__s)
        probability = 1
        for i, s_i in enumerate(self.__s):
            probability *= (self.__lambda*s_i)**n_vec[i] * \
                np.exp(-s_i*self.__lambda)/factorial(n_vec[i])
        return probability

    def __repr__(self):
        return f'Poisson(intensity={self.intensity}, sizes={self.sizes})'

    def sample(self, num_samples=1):
        """Draw samples from the distribution.

        Args:
            num_samples (int, optional, default=1):
                The number of samples to draw.

        Returns:
            numpy.ndarray: The samples.

        """
        Lambda = self.__lambda*self.sizes
        return np.squeeze(
            self.__sampler(
                lam=Lambda, size=(num_samples, len(Lambda))
            )
        )


class Statistics:
    """A class for the statistics of pores/particles.

    """
    @property
    def location(self):
        """The statistics for the location of the particles/pores.

        Returns:
            object: The location statistics.

        """
        return self.__location

    @property
    def radii(self):
        """The statistics for the radii of the particles/pores.

        Returns:
            object: The radii statistics.

        """
        return self.__radii

    @property
    def angles(self):
        """The statistics for the angles of the particles/pores.

        Returns:
            object: The angles statistics.

        """
        return self.__angles

    def __init__(self, location=None, radii=None, angles=None):
        self.__location = location
        self.__radii = radii
        self.__angles = angles

    def __call__(self):
        return self.location, self.radii, self.angles

    def __repr__(self):
        return 'Statistics(' + \
            f'location={self.location}, ' + \
            f'radii={self.radii}, ' + \
            f'angles={self.angles})'


class Generator:
    """A class for generating particles/pores based on given statistics.

    Calling an instance of the class with the numbers of particles and/or pores
    as the keyword arguments ``num_particles`` and ``num_pores`` will generate
    and return the particles and/or pores
    (i.e. instances of :class:`~.Particles` and/or :class:`~.Pores`).

    When a :class:`Generator` is instantiated with a target particle/pore
    volume fraction, a :class:`Poisson` point process governs the number
    of each size of the particles/pores being generated.
    In this case, the number of particles/pores is not specified when calling.

    Note:
        Discrete particle/pore ``radii`` statistics must be utilized
        when specifying a target particle/pore volume fraction,
        due to the :class:`~.Poisson` point process being used.

    Warning:
        The volume fraction calculation currently ignores variations
        due to boundary/particle/pore overlap removal.
        If particles/pores are unlikely to overlap during placement
        and a buffer is used, this will not be an issue.

    """
    @property
    def hull(self):
        """The convex hull in which particles/pores will be generated.

        Returns:
            scipy.spatial.Delaunay: The convex hull.

        """
        return self.__hull

    @property
    def hull_volume(self):
        """The volume fo the convex hull.

        Returns:
            float: The volume.

        """
        return self.__hull_volume

    @property
    def particle_statistics(self):
        """The statistics for generating particles.

        Returns:
            Statistics: The statistics.

        """
        return self.__particle_statistics

    @property
    def pore_statistics(self):
        """The statistics for generating pores.

        Returns:
            Statistics: The statistics.

        """
        return self.__pore_statistics

    @property
    def target_particle_volume_fraction(self):
        """The target volume fraction for particle generation.

        Returns:
            float: The volume fraction.

        """
        return self.__phi_particles_target

    @property
    def target_pore_volume_fraction(self):
        """The target volume fraction for pore generation.

        Returns:
            float: The volume fraction.

        """
        return self.__phi_pores_target

    @property
    def bounding_box(self):
        """The bounding box of the convex hull, i.e. of :attr:`hull`.

        Returns:
            numpy.ndarray: The bounding box.

        """
        return self.__bounding_box

    def __init__(self, buffer=None, hull='automatic', hull_rel_tol=3e-2,
                 particle_statistics=None, pore_statistics=None,
                 target_particle_volume_fraction=None,
                 target_pore_volume_fraction=None,
                 seed=None):
        self.__hull_rel_tol = hull_rel_tol
        self.__particle_statistics = particle_statistics
        self.__pore_statistics = pore_statistics
        self.__phi_particles_target = target_particle_volume_fraction
        self.__phi_pores_target = target_pore_volume_fraction
        if seed is None:
            self.__rng_seed = None
            self.__rng_location = np.random.default_rng()
            self.__rng_angles = np.random.default_rng()
        else:
            self.__rng_seed = seed
            self.__rng_location = np.random.default_rng(seed=self.__rng_seed)
            self.__rng_angles = np.random.default_rng(seed=self.__rng_seed)
        if hull == 'automatic':
            hull = self.__auto_cube_hull()
        self.buffer = buffer
        if not isinstance(hull, sp.Delaunay):
            self.__hull = sp.Delaunay(hull)
        else:
            self.__hull = hull
        self.__hull_volume = sp.ConvexHull(self.__hull.points).volume
        self.__get_bounding_box()

    def __call__(self, num_particles=None, num_pores=None, **kwargs):
        if self.target_particle_volume_fraction is None:
            if num_particles is not None:
                particles = self.__generate(
                    Particles(**kwargs),
                    num_particles,
                    self.particle_statistics
                )
            else:
                particles = Particles(**kwargs)
        elif self.target_particle_volume_fraction is not None:
            if num_particles is None:
                target_volume = self.hull_volume * \
                    self.target_particle_volume_fraction
                radiis, probabilities = self.particle_statistics.radii
                # assert np.isclose(np.sum(probabilities), 1)
                volumes = 4*np.pi/3*np.prod(radiis, axis=1)
                numbers = Poisson(
                    seed=self.__rng_seed,
                    intensity=target_volume/np.dot(probabilities, volumes),
                    sizes=probabilities
                ).sample()
                particles = Particles(**kwargs)
                for i, number in enumerate(numbers):
                    self.__generate(
                        particles, number, self.particle_statistics,
                        radii=lambda: radiis[i]
                    )
        if self.target_pore_volume_fraction is None:
            if num_pores is not None:
                pores = self.__generate(
                    Pores(**kwargs),
                    num_pores,
                    self.pore_statistics
                )
            else:
                pores = Pores(**kwargs)
        elif self.target_pore_volume_fraction is not None:
            if num_pores is None:
                target_volume = self.hull_volume * \
                    self.target_pore_volume_fraction
                radiis, probabilities = self.pore_statistics.radii
                # assert np.isclose(np.sum(probabilities), 1)
                volumes = 4*np.pi/3*np.prod(radiis, axis=1)
                numbers = Poisson(
                    seed=self.__rng_seed,
                    intensity=target_volume/np.dot(probabilities, volumes),
                    sizes=probabilities
                ).sample()
                pores = Pores(**kwargs)
                for i, number in enumerate(numbers):
                    self.__generate(
                        pores, number, self.pore_statistics,
                        radii=lambda: radiis[i]
                    )
        if len(particles()) > 0 and len(pores()) > 0:
            return particles, pores
        if len(particles()) > 0 and len(pores()) == 0:
            return particles
        if len(particles()) == 0 and len(pores()) > 0:
            return pores
        return ()

    def __repr__(self):
        pass

    def __get_bounding_box(self):
        bounding_box = [[0, 0], [0, 0], [0, 0]]
        for p_x, p_y, p_z in self.hull.points:
            if p_x < bounding_box[0][0]:
                bounding_box[0][0] = p_x
            elif p_x > bounding_box[0][1]:
                bounding_box[0][1] = p_x
            if p_y < bounding_box[1][0]:
                bounding_box[1][0] = p_y
            elif p_y > bounding_box[1][1]:
                bounding_box[1][1] = p_y
            if p_z < bounding_box[2][0]:
                bounding_box[2][0] = p_z
            elif p_z > bounding_box[2][1]:
                bounding_box[2][1] = p_z
        self.__bounding_box = np.array(bounding_box)

    def __generate(self, family, num_children, statistics, radii=None):
        if num_children > 0:
            if statistics.location == 'uniform random':
                location = self.__uniform_random_location
            else:
                location = statistics.location
            if statistics.angles == 'uniform random':
                def angles():
                    return Rotation.random(
                        random_state=self.__rng_angles
                    ).as_euler('zyx')
            else:
                angles = statistics.angles
            if radii is None:
                radii = statistics.radii
            for _ in range(num_children):
                family.spawn(
                    location=location(),
                    radii=radii(),
                    angles=angles()
                )
        return family

    def __uniform_random_location(self):
        if self.buffer is not None:
            kd_tree = sp.KDTree(self.hull.points)
        location = None
        while location is None:
            trial_location = self.bounding_box[:, 0] + \
                np.diff(self.bounding_box)[:, 0] * \
                self.__rng_location.random(size=3)
            if self.hull.find_simplex(trial_location) >= 0:
                if self.buffer is None:
                    location = trial_location
                elif kd_tree.query(trial_location)[0] > self.buffer:
                    location = trial_location
        return location

    def __auto_cube_hull(self):
        bbox = np.array(
            cubit.get_total_bounding_box(
                'volume', cubit.get_entities('volume'))[0:9]
            ).reshape(3, 3)[:, :2]
        num_points = int(1/self.__hull_rel_tol)
        l_x = np.linspace(bbox[0, 0], bbox[0, 1], num_points)
        l_y = np.linspace(bbox[1, 0], bbox[1, 1], num_points)
        l_z = np.linspace(bbox[2, 0], bbox[2, 1], num_points)
        x_xy, y_xy = np.meshgrid(l_x, l_y)
        x_xz, z_xz = np.meshgrid(l_x, l_z)
        y_yz, z_yz = np.meshgrid(l_y, l_z)
        zer = 0*x_xy
        return np.vstack((
            np.array([
                x_xy.ravel(), y_xy.ravel(), (zer + l_z[0]).ravel()
            ]).T,
            np.array([
                x_xy.ravel(), y_xy.ravel(), (zer + l_z[-1]).ravel()
            ]).T,
            np.array([
                x_xz.ravel(), (zer + l_y[0]).ravel(), z_xz.ravel()
            ]).T,
            np.array([
                x_xz.ravel(), (zer + l_y[-1]).ravel(), z_xz.ravel()
            ]).T,
            np.array([
                (zer + l_x[0]).ravel(), y_yz.ravel(), z_yz.ravel()
            ]).T,
            np.array([
                (zer + l_x[-1]).ravel(), y_yz.ravel(), z_yz.ravel()
            ]).T,
        ))
