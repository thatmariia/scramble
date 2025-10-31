from enum import Enum


class Level(int, Enum):
    """Enum representing the levels of expertise in the game."""
    BEGINNER = 1
    IMPROVER = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5

    def __str__(self):
        return self.name.capitalize()

    @classmethod
    def all_values(cls) -> list[int]:
        """
        Returns a sorted list of all level values.

        Returns
        -------
        list[int]
            List of all level values defined in the Level enum.
        """
        return sorted([level.value for level in cls])

    @classmethod
    def max_value(cls) -> int:
        """
        Returns the maximum level value.

        Returns
        -------
        int
            The maximum value of the Level enum.
        """
        return max(cls.all_values())

    @classmethod
    def min_value(cls) -> int:
        """
        Returns the minimum level value.

        Returns
        -------
        int
            The minimum value of the Level enum.
        """
        return min(cls.all_values())


