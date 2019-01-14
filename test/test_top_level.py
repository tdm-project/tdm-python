import unittest
import tdm


class TestTDM(unittest.TestCase):

    def test_version(self):
        self.assertIsNotNone(tdm.__version__)


CASES = [
    TestTDM,
]


def suite():
    ret = unittest.TestSuite()
    test_loader = unittest.TestLoader()
    for c in CASES:
        ret.addTest(test_loader.loadTestsFromTestCase(c))
    return ret


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run((suite()))
