from . import read_db_pb2_grpc as importStub

class ReadDbService(object):

    def __init__(self, router):
        self.connector = router.get_connection(ReadDbService, importStub.ReadDbStub)

    def Load(self, request, timeout=None, properties=None):
        return self.connector.create_request('Load', request, timeout, properties)

    def Execute(self, request, timeout=None, properties=None):
        return self.connector.create_request('Execute', request, timeout, properties)

    def StartPulling(self, request, timeout=None, properties=None):
        return self.connector.create_request('StartPulling', request, timeout, properties)

    def StopPulling(self, request, timeout=None, properties=None):
        return self.connector.create_request('StopPulling', request, timeout, properties)