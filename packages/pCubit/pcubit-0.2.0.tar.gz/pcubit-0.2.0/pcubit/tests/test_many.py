"""

"""

import unittest
import numpy as np
from scipy.special import factorial
from ..stats import Generator, Poisson, Statistics


class Many(unittest.TestCase):
    """

    """
    def main(self):
        """Main function for module-level testing functionality.

        """
        self.test_poisson_normalization()
        self.test_poisson_expectation()
        self.test_poisson_moments()
        self.test_generator_seeding()

    def test_poisson_normalization(self):
        """Test the normalization of the Poisson distribution.

        """
        n_i = np.arange(0, 50)
        occurrences = np.meshgrid(n_i, n_i, n_i)
        self.assertAlmostEqual(
            np.sum(
                Poisson(
                    intensity=np.random.rand(),
                    sizes=np.random.rand(len(occurrences)),
                )(occurrences)
            ), 1
        )

    def test_poisson_expectation(self):
        """Test the expectation value of the Poisson distribution.

        """
        n = np.arange(0, 50)
        occurrences = np.meshgrid(n, n, n)
        intensity = np.random.rand()
        sizes = np.random.rand(len(occurrences))
        for ll, n_l in enumerate(occurrences):
            self.assertAlmostEqual(
                np.sum(
                    n_l*Poisson(intensity=intensity, sizes=sizes)(occurrences)
                ), intensity*sizes[ll]
            )

    def test_poisson_moments(self):
        """Test the higher moments of the Poisson distribution.

        """
        for i in range(8):
            n = np.arange(0, 50)
            occurrences = np.meshgrid(n, n, n)
            intensity = np.random.rand()
            sizes = np.random.rand(len(occurrences))
            for ll, n_l in enumerate(occurrences):
                moment_i = 0
                for j in range(i + 1):
                    for k in range(j + 1):
                        moment_i += (intensity*sizes[ll])**j/factorial(j) * \
                            np.sum(
                                (-1)**k *
                                (j - k)**i *
                                factorial(j)/factorial(k)/factorial(j - k)
                            )
                self.assertAlmostEqual(
                    np.sum(
                        n_l**i*Poisson(intensity=intensity,
                                       sizes=sizes)(occurrences)
                    ), moment_i
                )

    def test_generator_seeding(self):
        """Test seeding the generator allows repeatability.

        """
        for _ in range(8):
            seed = np.random.randint(88)
            generator_0 = Generator(
                pore_statistics=Statistics(
                    location='uniform random',
                    radii=lambda: np.random.default_rng(seed=seed).random(3),
                    angles='uniform random'
                ),
                seed=seed
            )
            generator_1 = Generator(
                pore_statistics=Statistics(
                    location='uniform random',
                    radii=lambda: np.random.default_rng(seed=seed).random(3),
                    angles='uniform random'
                ),
                seed=seed
            )
            for _ in range(8):
                num_pores = np.random.randint(8, 23)
                self.assertTrue((
                    generator_0(num_pores=num_pores).get_data() ==
                    generator_1(num_pores=num_pores).get_data()
                ).all())


if __name__ == '__main__':
    unittest.main()
