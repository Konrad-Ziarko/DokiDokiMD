import unittest

loader = unittest.TestLoader()
start_dir = '.'
suite = loader.discover(start_dir, 'test_*.py')

runner = unittest.TextTestRunner()
runner.run(suite)





