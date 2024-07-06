from typing import Dict

class Node():
    def __init__(self, value, children = {}):
        self.value = value
        self.children = children
    
    def __repr__(self) -> str:
        if not self.children:
            return f"Node({self.value})"
        
        string = f"Node({self.value}, {{"
        if len(self.children) < 1:
            return f"{string}}})"
        
        if len(self.children) == 1:
            k, v = list(self.children.items())[0]
            return f"{string}'{k}': {v}}})"
        
        if len(self.children) > 1:
            for k, v in self.children.items():
                string += f"'{k}': {v}, "
            return f"{string[:-2]}}})"
        return "-1"
    
    def to_json(self):
        if not self.children:
            return f'{{"value": "{self.value}"}}'
        
        string = f'{{"value": "{self.value}", "children": {{'
        if len(self.children) < 1:
            return f'{string}}}}}'
        
        if len(self.children) == 1:
            k, v = list(self.children.items())[0]
            return f'{string}"{k}": {v.to_json()}}}}}'
        
        if len(self.children) > 1:
            for k, v in self.children.items():
                string += f'"{k}": {v.to_json()}, '
            return f'{string[:-2]}}}}}'
        return '-1'

class Tree():
    def __init__(self, root : Node = None):
        self.root = root

    def __str__(self):
        return f"Tree({self.root})"
    
    def to_json(self):
        return self.root.to_json()
    
    def is_empty(self):
        return self.root is None
    
    def insert(self, data, path : list[str]):
        if self.root is None:
            if path != []:
                return None
            self.root = Node(data)
            return self.root
        current = self.root
        # Tree must exist up to the parent of the new node
        for p in path[:-1]:
            if p not in current.children:
                return None
            current = current.children[p]
        # Tree must not have the new node already
        if path[-1] in current.children:
            print(f'Error: {path[-1]} already exists in the tree at path {path[:-1]}')
            return None
        current.children[path[-1]] = Node(data, {})
        return current

    def search(self, path : list[str]):
        if self.root is None:
            return None
        if path == []:
            return self.root
        current = self.root
        for response in path:
            if response not in current.children:
                return None
            current = current.children[response]
        return current
        
if __name__ == '__main__':
    root = Node('A', {'0': Node('B', {'0': Node('C', {'0': Node('G', {'0': Node('P', {})}),
                                                      '1': Node('H', {}),
                                                      '2': Node('I', {})}),
                                      '1': Node('D', {'0': Node('J', {})}),
                                      '2': Node('E', {'0': Node('K', {}),
                                                      '1': Node('L', {})}),
                                      '3': Node('F', {'0': Node('M', {}),
                                                      '1': Node('N', {}),
                                                      '2': Node('O', {})})})})
    tree = Tree(root)
    print("Search A[0], B[2], E[1] to find L:", tree.search(['0', '2', '1']))
    print("Insert 'Q' inside L[0]:", tree.insert('Q', ['0', '2', '1', '0']))
    print(tree)

    tree2 = Tree()
    print(tree2)
    print("Insert 'A' into an empty tree:", tree2.insert('A', []))
    print(tree2)
    print("Insert 'B' into an empty tree:", tree2.insert('B', ['0']))
    print("To jSON:")
    print(tree.to_json())




    
