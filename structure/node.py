class Node:
    def __init__(self, ):
        pass

    def __str__(self) -> str:
        str = "mbr[" + ",".join(self.mbr) + "]" + "\n"
        for item in self.nodes:
            str = str + item + "\n"
        return str
