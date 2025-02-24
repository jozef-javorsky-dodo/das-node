from hyperon_das_node import DistributedAlgorithmNode, Message, LeadershipBrokerType, MessageBrokerType

class PrintMessage(Message):
    def __init__(self, content: str):
        super().__init__()
        self.content = content

    def act(self, node: "SimpleNode") -> None:
        # ideally we should call a node.method in here 
        node.print_content(self.content)

class SimpleNode(DistributedAlgorithmNode):
    def __init__(self, node_id: str, is_server: bool) -> None:
        super().__init__(
            node_id,
            LeadershipBrokerType.SINGLE_MASTER_SERVER,
            MessageBrokerType.GRPC,
        )

        self.is_server = is_server
        self.known_commands = {
            "print": PrintMessage,
        }

    def print_content(self, content: str):
        print(content)

    def message_factory(self, command: str, args: list[str]) -> Message:
        message = super().message_factory(command, args)
        if message is not None:
            return message

        if klass:=self.known_commands.get(command):
            return klass(*args)

        return None

class SimpleNodeServer(SimpleNode):
    def __init__(self, node_id: str) -> None:
        super().__init__(node_id, True)

    def node_joined_network(self, node_id: str) -> None:
        self.add_peer(node_id)

    def cast_leadership_vote(self) -> str:
        return self.node_id()

class SimpleNodeClient(SimpleNode):
    def __init__(self, node_id: str, server_id: str) -> None:
        super().__init__(node_id, False)
        self.server_id = server_id
        self.add_peer(server_id)

    def node_joined_network(self, node_id: str) -> None:
        # do nothing
        pass

    def cast_leadership_vote(self) -> str:
        return self.server_id


if __name__ == "__main__":
    server = SimpleNodeServer("localhost:35700")
    client = SimpleNodeClient("localhost:35701", "localhost:35700")
    server.join_network()
    client.join_network()

    client.send("print", ["something"], "localhost:35700")
