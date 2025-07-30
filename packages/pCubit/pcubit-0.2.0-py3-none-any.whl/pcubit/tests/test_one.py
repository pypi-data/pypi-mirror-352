"""

"""

import unittest
import numpy as np
from scipy.special import factorial
from ..core import cubit_cmd, cubit_init
from ..core import Ellipsoid, Ellipsoids, Particle, Particles, Pore, Pores
from ..stats import Poisson


class One(unittest.TestCase):
    """

    """
    def main(self):
        """Main function for module-level testing functionality.

        """
        self.test_successful_adoption_0()
        self.test_successful_adoption_1()
        self.test_failed_adoption_0()
        self.test_failed_adoption_1()
        self.test_failed_adoption_2()
        self.test_failed_adoption_3()
        self.test_successful_disowning_0()
        self.test_successful_disowning_1()
        self.test_failed_disowning_0()
        self.test_failed_disowning_1()
        self.test_failed_disowning_2()
        self.test_successful_placement_0()
        self.test_successful_placement_1()
        self.test_poisson_normalization()
        self.test_poisson_expectation()
        self.test_poisson_moments()

    def test_successful_adoption_0(self):
        """Test the successful adoption of one child by one parent.

        """
        Ellipsoids().adopt(Ellipsoid())
        Pores().adopt(Pore())
        Particles().adopt(Particle())

    def test_successful_adoption_1(self):
        """Test the successful adoption of one child by one parent.

        """
        ellipsoids = Ellipsoids()
        ellipsoids.spawn()
        ellipsoid = ellipsoids()
        ellipsoids.disown(ellipsoid)
        ellipsoids.adopt(ellipsoid)
        particles = Particles()
        particles.spawn()
        particle = particles()
        particles.disown(particle)
        particles.adopt(particle)
        pores = Pores()
        pores.spawn()
        pore = pores()
        pores.disown(pore)
        pores.adopt(pore)

    def test_failed_adoption_0(self):
        """Test the failed adoption of one child by one parent.

        """
        self.assertRaises(
            AssertionError, lambda: Ellipsoids().adopt(Pore())
        )
        self.assertRaises(
            AssertionError, lambda: Ellipsoids().adopt(Particle())
        )
        self.assertRaises(
            AssertionError, lambda: Particles().adopt(Ellipsoid())
        )
        self.assertRaises(
            AssertionError, lambda: Particles().adopt(Pore())
        )
        self.assertRaises(
            AssertionError, lambda: Pores().adopt(Ellipsoid())
        )
        self.assertRaises(
            AssertionError, lambda: Pores().adopt(Particle())
        )

    def test_failed_adoption_1(self):
        """Test the failed adoption of one child by one parent.

        """
        ellipsoid = Ellipsoid()
        Ellipsoids().adopt(ellipsoid)
        self.assertRaises(
            AssertionError, lambda: Ellipsoids().adopt(ellipsoid)
        )
        particle = Particle()
        Particles().adopt(particle)
        self.assertRaises(
            AssertionError, lambda: Particles().adopt(particle)
        )
        pore = Pore()
        Pores().adopt(pore)
        self.assertRaises(
            AssertionError, lambda: Pores().adopt(pore)
        )

    def test_failed_adoption_2(self):
        """Test the failed adoption of one child by one parent.

        """
        ellipsoid = Ellipsoid()
        ellipsoids = Ellipsoids()
        ellipsoids.adopt(ellipsoid)
        self.assertRaises(
            AssertionError, lambda: ellipsoids.adopt(ellipsoid)
        )
        particle = Particle()
        particles = Particles()
        particles.adopt(particle)
        self.assertRaises(
            AssertionError, lambda: particles.adopt(particle)
        )
        pore = Pore()
        pores = Pores()
        pores.adopt(pore)
        self.assertRaises(
            AssertionError, lambda: pores.adopt(pore)
        )

    def test_failed_adoption_3(self):
        """Test the failed adoption of one child by one parent.

        """
        ellipsoids = Ellipsoids()
        ellipsoids.spawn()
        self.assertRaises(
            AssertionError, lambda: ellipsoids.adopt(ellipsoids())
        )
        particles = Particles()
        particles.spawn()
        self.assertRaises(
            AssertionError, lambda: particles.adopt(particles())
        )
        pores = Pores()
        pores.spawn()
        self.assertRaises(
            AssertionError, lambda: pores.adopt(pores())
        )

    def test_successful_disowning_0(self):
        """Test the successful disowning of one child by one parent.

        """
        ellipsoid = Ellipsoid()
        ellipsoids = Ellipsoids()
        ellipsoids.adopt(ellipsoid)
        ellipsoids.disown(ellipsoid)
        particle = Particle()
        particles = Particles()
        particles.adopt(particle)
        particles.disown(particle)
        pore = Pore()
        pores = Pores()
        pores.adopt(pore)
        pores.disown(pore)

    def test_successful_disowning_1(self):
        """Test the successful disowning of one child by one parent.

        """
        ellipsoids = Ellipsoids()
        ellipsoids.spawn()
        ellipsoids.disown(ellipsoids())
        particles = Particles()
        particles.spawn()
        particles.disown(particles())
        pores = Pores()
        pores.spawn()
        pores.disown(pores())

    def test_failed_disowning_0(self):
        """Test the failed disowning of one child by one parent.

        """
        self.assertRaises(
            AssertionError, lambda: Ellipsoids().disown(Ellipsoid())
        )
        self.assertRaises(
            AssertionError, lambda: Ellipsoids().disown(Pore())
        )
        self.assertRaises(
            AssertionError, lambda: Ellipsoids().disown(Particle())
        )
        self.assertRaises(
            AssertionError, lambda: Particles().disown(Ellipsoid())
        )
        self.assertRaises(
            AssertionError, lambda: Particles().disown(Pore())
        )
        self.assertRaises(
            AssertionError, lambda: Particles().disown(Particle())
        )
        self.assertRaises(
            AssertionError, lambda: Pores().disown(Ellipsoid())
        )
        self.assertRaises(
            AssertionError, lambda: Pores().disown(Pore())
        )
        self.assertRaises(
            AssertionError, lambda: Pores().disown(Particle())
        )

    def test_failed_disowning_1(self):
        """Test the failed disowning of one child by one parent.

        """
        ellipsoid = Ellipsoid()
        ellipsoids = Ellipsoids()
        ellipsoids.adopt(ellipsoid)
        ellipsoids.disown(ellipsoid)
        self.assertRaises(
            AssertionError, lambda: ellipsoids.disown(ellipsoid)
        )
        particle = Particle()
        particles = Particles()
        particles.adopt(particle)
        particles.disown(particle)
        self.assertRaises(
            AssertionError, lambda: particles.disown(particle)
        )
        pore = Pore()
        pores = Pores()
        pores.adopt(pore)
        pores.disown(pore)
        self.assertRaises(
            AssertionError, lambda: pores.disown(pore)
        )

    def test_failed_disowning_2(self):
        """Test the failed disowning of one child by one parent.

        """
        ellipsoids = Ellipsoids()
        ellipsoids.spawn()
        ellipsoid = ellipsoids()
        ellipsoids.disown(ellipsoid)
        self.assertRaises(
            AssertionError, lambda: ellipsoids.disown(ellipsoid)
        )
        particles = Particles()
        particles.spawn()
        particle = particles()
        particles.disown(particle)
        self.assertRaises(
            AssertionError, lambda: particles.disown(particle)
        )
        pores = Pores()
        pores.spawn()
        pore = pores()
        pores.disown(pore)
        self.assertRaises(
            AssertionError, lambda: pores.disown(pore)
        )

    def test_successful_placement_0(self):
        """Test the successful placement of one pore/particle.

        """
        cubit_init()
        cubit_cmd('create sphere radius 3')
        cubit_cmd('block 1 add volume 1')
        Particle(location=[0, 1, 0], radii=[0.1, 0.1, 0.1]).place()
        Pore(location=[0, 0, 1], radii=[0.1, 0.1, 0.1]).place()

    def test_successful_placement_1(self):
        """Test the successful placement of one pore/particle.

        """
        cubit_init()
        cubit_cmd('create sphere radius 3')
        cubit_cmd('block 1 add volume 1')
        particles = Particles()
        particles.adopt(Particle(location=[0, 1, 0], radii=[0.1, 0.1, 0.1]))
        particles.place()
        pores = Pores()
        pores.adopt(Pore(location=[0, 0, 1], radii=[0.1, 0.1, 0.1]))
        pores.place()

    def test_poisson_normalization(self):
        """Test the normalization of the Poisson distribution.

        """
        self.assertAlmostEqual(
            np.sum(
                Poisson(
                    intensity=np.random.rand(),
                    sizes=[np.random.rand()],
                )([np.arange(0, 50)])
            ), 1
        )

    def test_poisson_expectation(self):
        """Test the expectation value of the Poisson distribution.

        """
        occurrences = [np.arange(0, 50)]
        intensity = np.random.rand()
        sizes = [np.random.rand()]
        self.assertAlmostEqual(
            np.sum(
                occurrences[0] *
                Poisson(intensity=intensity, sizes=sizes,)(occurrences)
            ), intensity*sizes[0]
        )

    def test_poisson_moments(self):
        """Test the higher moments of the Poisson distribution.

        """
        for i in range(8):
            occurrences = [np.arange(0, 50)]
            intensity = np.random.rand()
            sizes = [np.random.rand()]
            moment_i = 0
            for j in range(i + 1):
                for k in range(j + 1):
                    moment_i += (intensity*sizes[0])**j/factorial(j) * \
                        np.sum(
                            (-1)**k *
                            (j - k)**i *
                            factorial(j)/factorial(k)/factorial(j - k)
                        )
            self.assertAlmostEqual(
                np.sum(
                    occurrences[0]**i *
                    Poisson(intensity=intensity, sizes=sizes,)(occurrences)
                ), moment_i
            )


if __name__ == '__main__':
    unittest.main()
