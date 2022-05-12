from dataclasses import dataclass
from specklepy.api import operations
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
from specklepy.objects import Base
from specklepy.transports.server import ServerTransport

from my_token import token


@dataclass
class SpeckleConnection:
    server: str = 'speckle.xyz'
    token: str = ''
    stream_id: str = ''
    client: ... = None
    account: ... = None
    transport: ... = None

    def __post_init__(self):
        self.client = SpeckleClient(host=self.server)
        self.account = get_account_from_token(self.token, self.server)
        self.client.authenticate_with_account(self.account)
        self.setup_server_transport()

    @property
    def streams(self):
        return self.client.stream.list()

    def branches_from_stream(self, stream_id):
        return self.client.branch.list(stream_id)

    def commits_from_stream(self, stream_id, limit=100):
        return self.client.commit.list(stream_id, limit=limit)

    def stream_by_name(self, name):
        return self.client.stream.search(name)[0]

    def get_stream(self, stream_id):
        return self.client.stream.get(id=stream_id)

    def setup_server_transport(self):
        self.transport = ServerTransport(client=self.client, stream_id=self.stream_id)

    def send_to_stream(self, speckle_object, message):
        hash = operations.send(base=speckle_object, transports=[self.transport])
        commit_id = self.client.commit.create(stream_id=self.stream_id, object_id=hash, message=message)
        return commit_id


@dataclass()
class BotCommit(Base):
    user_id: str
    request: object

    def __post_init__(self):
        self.request = {} if self.request is None else self.request


if __name__ == '__main__':
    bc = BotCommit(user_id='123', request={'answer': 'this is a test'})
    connection = SpeckleConnection(token=token, stream_id='a2e12c1fc9')
    connection.send_to_stream(bc, 'testing custom Speckle Object')
