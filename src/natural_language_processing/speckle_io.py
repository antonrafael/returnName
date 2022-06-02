from dataclasses import dataclass
from specklepy.api import operations
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
from specklepy.objects import Base
from specklepy.transports.server import ServerTransport


@dataclass
class SpeckleConnection:
    server: str = 'speckle.xyz'
    token: str = ''
    stream_id: str = ''
    branch_name: str = 'main'
    commit_id: str = ''
    client: ... = None
    account: ... = None
    transport: ... = None
    max_retrieved_commits: int = 100

    def __post_init__(self):
        self.client = SpeckleClient(host=self.server)
        if self.token == '': return
        self.setup_token()
        if self.stream_id == '': return
        self.setup_server_transport()

    @property
    def active_stream(self):
        return self.get_stream(self.stream_id)

    @property
    def active_branch(self):
        branches = [branch for branch in self.branches if branch.name == self.branch_name]
        return branches[0] if len(branches) > 0 else None

    @property
    def active_commit(self):
        commits = [commit for commit in self.commits if commit.id == self.commit_id]
        return commits[0] if len(commits) > 0 else None

    @property
    def streams(self):
        return self.client.stream.list()

    @property
    def branches(self):
        return self.client.branch.list(self.stream_id)

    @property
    def commits_all_branches(self):
        return self.client.commit.list(self.stream_id, limit=self.max_retrieved_commits)

    @property
    def commits(self):
        stream_commits = self.commits_all_branches
        return [commit for commit in stream_commits if commit.branchName == self.branch_name]

    def new_stream_id(self, name):
        return self.client.stream.create(name=name)

    def new_stream(self, name):
        stream_id = self.new_stream_id(name)
        return self.get_stream(stream_id)

    def set_new_stream(self, name):
        self.stream_id = self.new_stream_id(name)
        self.setup_server_transport()

    def stream_by_name(self, name):
        return self.client.stream.search(name)[0]

    def get_stream(self, stream_id):
        return self.client.stream.get(id=stream_id)

    def setup_token(self, token=None):
        self.token = self.token if token is None else token
        self.account = get_account_from_token(self.token, self.server)
        self.client.authenticate_with_account(self.account)

    def setup_server_transport(self):
        self.transport = ServerTransport(client=self.client, stream_id=self.stream_id)   ### account Vs client?

    def send_to_stream(self, speckle_object, message):
        hash = operations.send(base=speckle_object, transports=[self.transport])
        commit_id = self.client.commit.create(stream_id=self.stream_id, object_id=hash, message=message)
        return commit_id

    def receive(self, mark_received=True):
        stream_data = operations.receive(self.active_commit.referencedObject, self.transport)
        if mark_received:
            self.client.commit.received(
                self.stream_id,
                self.commit_id,
                source_application='blender',
                message='received commit from Speckly add-on for Blender',
            )
        return stream_data


@dataclass
class BotCommit(Base):
    user_id: str = ''
    request: dict = None

    def __post_init__(self):
        self.request = {} if self.request is None else self.request


if __name__ == '__main__':
    from my_token import token
    bc = BotCommit(
        user_id='123',
        request={
            'field': 'structural', 'success': True, 'element': 'beam', 'element_name': 'B125', 'direction': 'down',
            'number': 0.2, 'unit': 'm', 'answer': 'Hey there! Perfect, I understood that a beam named B125 ' +
            'is requested to be moved down by 0.2 m. Do you want to commit that action to the Speckle Server?'
        }
    )
    connection = SpeckleConnection(token=token, stream_id='8e6d1d1c53')
    print('')
    # connection.send_to_stream(bc, 'testing custom Speckle Object')
