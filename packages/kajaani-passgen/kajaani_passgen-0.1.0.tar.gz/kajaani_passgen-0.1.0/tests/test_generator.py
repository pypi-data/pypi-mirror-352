import unittest
from simplepassgen import generate_password


class TestPasswordGenerator(unittest.TestCase):
    def test_default_length(self):
        pwd = generate_password()
        self.assertEqual(len(pwd), 12)

    def test_custom_length(self):
        pwd = generate_password(length=20)
        self.assertEqual(len(pwd), 20)

    def test_no_digits_no_specials(self):
        pwd = generate_password(use_digits=False, use_specials=False)
        self.assertTrue(all(c.isalpha() for c in pwd))


if __name__ == '__main__':
    unittest.main()
