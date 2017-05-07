import unittest

from gluon.globals import Request

execfile("applications/ACLCreator/controllers/default.py", globals())


class TestCreatedObjects(unittest.TestCase):
    def setUp(self):
        request = Request()  # Use a clean Request object

    def testCreatedObjects(self):


