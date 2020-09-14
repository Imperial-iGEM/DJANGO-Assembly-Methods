""" Checks for validating that the design specified by the user is 
valid for this type of assembly """

def setUp(self):
        filepath = "./examples/sbol/dummy.xml"
        self.doc = sbol2.Document(filepath)
        self.parser = ParserSBOL(sbol2.Document(filepath))


def is_order_correct(part):
    """ Check that the order of parts and connector modules 
    is correct.
    BASIC assembly that each part is 
    preceded and followed by a linker """"


def has_integrated_linker(part):
    """ Check that each part neighboring a linker has an integrated 
    prefix / suffix corresponding to that linker. """


def 