from geocom.enums import LeicaReturnCode

class TCException(Exception):
    def __init__(self, return_code: LeicaReturnCode):
        self.returnMessage = return_code.name
