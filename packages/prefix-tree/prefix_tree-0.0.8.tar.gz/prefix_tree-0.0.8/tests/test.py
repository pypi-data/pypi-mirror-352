# pylint: disable=C0114

import unittest

from src.prefix_tree.trie import Trie


IVAN_31_TT = {
        'name': 'иван',
        'age': 31,
        'gender': True,
        'type': True
    }
IRINA_23_FT = {
        'name': 'ирина',
        'age': 23,
        'gender': False,
        'type': True
    }
IO_3_TT = {
        'name': 'ио',
        'age': 3,
        'gender': True,
        'type': True
    }
IVANOVICH_51_TN = {
        'name': 'иванович',
        'age': 51,
        'gender': True,
        'type': None
    }
TEST_DATA_SMALL = [
    IVAN_31_TT,
    IRINA_23_FT,
    IO_3_TT,
    IVANOVICH_51_TN
]


class TestTrieMethods(unittest.TestCase):  # pylint: disable=C0115
    SETUP_DONE = False

    @classmethod
    def setUpClass(cls) -> None:
        cls.trie = Trie()
        if TestTrieMethods.SETUP_DONE:
            return
        for person in TEST_DATA_SMALL:
            cls.trie.insert(
                person['name'],
                {
                    'name': person['name'],
                    'age': person['age'],
                    'gender': person['gender'],
                    'type': person['type']
                }
            )
            TestTrieMethods.SETUP_DONE = True

    def test_no_output_increment(self):
        """
        Regression
        """
        res1 = self.trie._get_by_prefix('иван')[:]  # pylint: disable=W0212
        res2 = self.trie._get_by_prefix('иван')[:]  # pylint: disable=W0212
        self.assertEqual(res1, res2)

    def test_get_by_prefix_sort_desc_by(self):
        """
        Regression
        """
        res = self.trie.get_by_prefix_sort_desc_by('ив', 'age')
        self.assertEqual(res, [IVANOVICH_51_TN, IVAN_31_TT])

    def test_len(self):
        """
        Regression
        """
        res = self.trie._get_by_prefix('%%')  # pylint: disable=W0212
        self.assertEqual(len(res), len(TEST_DATA_SMALL))

    def test_get_by_prefix_and_query(self):
        """
        Regression
        """
        res = self.trie.get_by_prefix_and_query("и", {"type": True, "gender": False})
        self.assertEqual(res, [IRINA_23_FT])


if __name__ == '__main__':
    unittest.main()
