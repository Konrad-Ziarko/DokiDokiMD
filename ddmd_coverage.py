import unittest
import coverage


cov = coverage.Coverage(
    source=['dokidokimd'],
    omit=['*/venv/*',
          '*/test/*',
          ])

cov.start()
loader = unittest.TestLoader()

suite = loader.discover(start_dir='.', pattern='test_*.py')
complete_suite = unittest.TestSuite(suite)
unittest.TextTestRunner().run(complete_suite)

cov.stop()
# cov.html_report(directory='coverage')
cov.xml_report()
report = cov.report(skip_empty=True)
cov.erase()

