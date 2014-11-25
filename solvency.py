import hashlib, os, json

class TreeError(Exception): pass
class ParentError(Exception): pass

class Node:
    def __init__(self, value, hash):
        self.value = value
        self.hash = hash
        self.parent = None

    def parents(self):
        '''return a list of parents going up to the root node'''
        node = self
        parents = []
        while node.parent:
            if node.parent in parents:
                raise ParentError('Parents Loop')
            parents.append(node.parent)
            node = node.parent

        return parents

    def root(self):
        if self.parent:
            return self.parent.root()
        else:
            return self

    def verify(self):
        if not self.parent: return True

        if self != self.parent.left and self != self.parent.right:
            #not a child of parent
            return False

        return self.parent.verify()


class Leaf(Node):
    def __init__(self, id, value, nonce=None):
        if not nonce: nonce = os.urandom(32)
        hash = hashlib.sha256(str(id)+str(value)+nonce).digest()
        Node.__init__(self, value, hash)
        self.id = id
        self.nonce = nonce

    def verify(self):
        hash = hashlib.sha256(str(self.id)+str(self.value)+self.nonce).digest()
        if hash != self.hash: return False
        return Node.verify(self)

    def proof(self):
        proof = {'leaf': {'id': self.id,
                          'value': self.value,
                          'nonce': self.nonce.encode('hex'),
                          'hash': self.hash.encode('hex')},
                 'parents': []}
        for parent in self.parents():
            left_dict   = {'value': parent.left.value,
                           'hash': parent.left.hash.encode('hex')}
            right_dict  = {'value': parent.right.value,
                           'hash': parent.right.hash.encode('hex')}
            parent_dict = {'value': parent.value,
                           'hash': parent.hash.encode('hex'),
                           'left': left_dict,
                           'right': right_dict}
            proof['parents'].append(parent_dict)

        return proof

    def json_proof(self):
        return json.dumps(self.proof())

    def save_proof(self, path='proofs'):
        jproof = self.json_proof()
        filename = os.path.join(path, self.id+'.txt')
        with open(filename, 'w') as file:
            file.write(jproof)


class Branch(Node):
    def __init__(self, left, right):
        value = left.value + right.value
        hash = hashlib.sha256(str(value)+left.hash+right.hash).digest()
        Node.__init__(self, value, hash)
        self.left = left
        self.right = right
        left.parent = right.parent = self

    def verify(self):
        if self.value != self.left.value + self.right.value: return False
        hash = hashlib.sha256(str(self.value)+self.left.hash+self.right.hash).digest()
        if self.hash != hash: return False
        return Node.verify(self)


def build_tree(leafs):
    '''Take a list of leafs, create a tree, and return the root node'''
    if not leafs: raise TreeError('No Leafs Given')
    nodes = leafs[:]
    while len(nodes) > 1:
        left, right = nodes.pop(0), nodes.pop(0)
        branch = Branch(left, right)
        nodes.append(branch)
    return nodes[0]

def proof2tree(proof):
    '''
    Takes a proof dictionary, creates a proof tree
    and returns the leaf and root
    '''
    leafdict = proof['leaf']
    leaf = Leaf(leafdict['id'], leafdict['value'], leafdict['nonce'].decode('hex'))
    child = leaf
    #import pdb; pdb.set_trace()
    for parentdict in proof['parents']:
        leftdict = parentdict['left']
        rightdict = parentdict['right']
        if child.hash == leftdict['hash'].decode('hex'):
            left = child
            right = Node(rightdict['value'], rightdict['hash'].decode('hex'))
        elif child.hash == rightdict['hash'].decode('hex'):
            left = Node(leftdict['value'], leftdict['hash'].decode('hex'))
            right = child
        else:
            raise ParentError('Child hash does not match either side of parent')

        parent = Branch(left, right)
        child = parent

    return leaf, parent

def json2tree(json_proof):
    proof = json.loads(json_proof)
    return proof2tree(proof)

def filename2tree(path):
    with open(path, 'r') as file:
        return json2tree(file.read())

def verify_proof(proof, id, value, roothash, rootvalue):
    leaf, root = proof2tree(proof)
    if leaf.id != id:
        print 'leaf.id != id'
        return False
    if leaf.value != value:
        print 'leaf.value != value'
        return False
    if root.hash != roothash:
        print 'root.hash != roothash'
        return False
    if root.value != rootvalue:
        print 'root.value != rootvalue'
        return False
    return leaf.verify()

def verify_json(json_proof, id, value, roothash, rootvalue):
    proof = json.loads(json_proof)
    return verify_proof(proof, id, value, roothash, rootvalue)

def verify_file(path, id, value, roothash, rootvalue):
    with open(path, 'r') as file:
        return verify_json(file.read(), id, value, roothash, rootvalue)
