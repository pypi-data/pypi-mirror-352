import unittest

from nwebclient import util as u

class BaseTestCase(unittest.TestCase):
    
    def test_Args(self):
        args = u.Args.from_cmd('docker run -it --name myubuntu')
        self.assertEqual(args['name'], 'myubuntu')

    def test_flatten_dict(self):
        nested = {
            'a': {'sub': 1},
            'b': {'x': {'y': 2}},
            'c': 3
        }
        expected = {
            'a_sub': 1,
            'b_x_y': 2,
            'c': 3
        }
        result = u.flatten_dict(nested)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
