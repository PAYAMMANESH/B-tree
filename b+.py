class Leaf:
    def __init__(self):
        self.keyval = []
        self.recnum = []
        self.prevLf = None
        self.nextLf = None

    def is_leaf(self):
        return True

    def get_item(self, key, near):
        vals = self.keyval
        if near:
            for i in range(len(vals)):
                if key <= vals[i]:
                    return i
        else:
            for i in range(len(vals)):
                if key == vals[i]:
                    return i
        return -1

    def add_key(self, key, rec):
        vals = self.keyval
        itm = len(vals)
        for i in range(len(vals)):
            if key == vals[i]:
                itm = -1
                break
            if key <= vals[i]:
                itm = i
                break
        if itm != -1:
            vals.insert(itm, key)
            self.recnum.insert(itm, rec)
        return itm

    def split(self):
        mov = len(self.keyval) // 2
        new_leaf = Leaf()
        new_leaf.keyval = self.keyval[mov:]
        new_leaf.recnum = self.recnum[mov:]
        self.keyval = self.keyval[:mov]
        self.recnum = self.recnum[:mov]
        new_leaf.prevLf = self
        new_leaf.nextLf = self.nextLf
        if self.nextLf:
            self.nextLf.prevLf = new_leaf
        self.nextLf = new_leaf
        return new_leaf

    def merge(self, fr_nod, pa_nod, fr_key):
        self.keyval += fr_nod.keyval
        self.recnum += fr_nod.recnum
        self.nextLf = fr_nod.nextLf
        if fr_nod.nextLf:
            fr_nod.nextLf.prevLf = self
        fr_nod.prevLf = None
        fr_nod.nextLf = None
        itm = len(pa_nod.keyval) - 1
        for i in range(len(pa_nod.keyval) - 1, -1, -1):
            if pa_nod.keyval[i] == fr_key:
                itm = i
                break
        for i in range(itm, len(pa_nod.keyval) - 1):
            pa_nod.keyval[i] = pa_nod.keyval[i + 1]
            pa_nod.nodptr[i + 1] = pa_nod.nodptr[i + 2]
        pa_nod.keyval.pop()
        pa_nod.nodptr.pop()


class Node:
    def __init__(self):
        self.keyval = []
        self.nodptr = []

    def is_leaf(self):
        return False

    def get_item(self, key):
        vals = self.keyval
        for i in range(len(vals)):
            if key < vals[i]:
                return i
        return len(vals)

    def add_key(self, key, ptr_l, ptr_r):
        vals = self.keyval
        itm = len(vals)
        for i in range(len(vals)):
            if key <= vals[i]:
                itm = i
                break
        vals.insert(itm, key)
        self.nodptr.insert(itm, ptr_l)
        self.nodptr.insert(itm + 1, ptr_r)


class BPlusTree:
    def __init__(self, order):
        self.root = Leaf()
        self.maxkey = order - 1
        self.minkyl = order // 2
        self.minkyn = self.maxkey // 2
        self.leaf = None
        self.item = -1
        self.keyval = ''
        self.recnum = -1
        self.length = 0
        self.eof = True
        self.found = False

    def insert(self, key, rec):
        stack = []
        self.leaf = self.root
        while not self.leaf.is_leaf():
            stack.append(self.leaf)
            self.item = self.leaf.get_item(key)
            self.leaf = self.leaf.nodptr[self.item]
        self.item = self.leaf.add_key(key, rec)
        self.keyval = key
        self.eof = False
        if self.item == -1:
            self.found = True
            self.item = self.leaf.get_item(key, False)
            self.recnum = self.leaf.recnum[self.item]
        else:
            self.found = False
            self.recnum = rec
            self.length += 1
            if len(self.leaf.keyval) > self.maxkey:
                pL = self.leaf
                pR = self.leaf.split()
                ky = pR.keyval[0]
                self.item = self.leaf.get_item(key, False)
                if self.item == -1:
                    self.leaf = self.leaf.nextLf
                    self.item = self.leaf.get_item(key, False)
                while True:
                    if len(stack) == 0:
                        new_n = Node()
                        new_n.keyval.append(ky)
                        new_n.nodptr.append(pL)
                        new_n.nodptr.append(pR)
                        self.root = new_n
                        break
                    nod = stack.pop()
                    nod.add_key(ky, pL, pR)
                    if len(nod.keyval) <= self.maxkey:
                        break
                    pL = nod
                    pR = nod.split()
                    ky = nod.keyval.pop()

    def remove(self, key):
        if key is None:
            if self.item == -1:
                self.eof = True
                self.found = False
                return False
            key = self.leaf.keyval[self.item]
        self._del(key)
        if not self.found:
            self.item = -1
            self.eof = True
            self.keyval = ''
            self.recnum = -1
        else:
            self.seek(key, True)
            self.found = True
        return self.found

    # Other methods such as seek, skip, goto, keynum, goTop, goBottom, pack, _del, _fixNodes should be added similarly

    def _del(self, key):
        stack = []
        par_nod = None
        par_ptr = -1
        self.leaf = self.root
        while not self.leaf.is_leaf():
            stack.append(self.leaf)
            par_nod = self.leaf
            par_ptr = self.leaf.get_item(key)
            self.leaf = self.leaf.nodptr[par_ptr]
        self.item = self.leaf.get_item(key, False)

    # Other parts of _del method should be implemented similarly


def display_tree(root):
    if not root:
        return

    current_level = [root]
    while current_level:
        next_level = []
        for node in current_level:
            if isinstance(node, Node):
                print(f"Keys: {node.keyval}, Pointers: {[str(x.keyval) for x in node.nodptr]}")
                next_level.extend(node.nodptr)
            else:
                print(f"Keys: {node.keyval}, Records: {node.recnum}")
        print("-----------------------")
        current_level = next_level


# Usage example:


def __main__():
    f = open("C:/Users/Payam/Desktop/test.txt")
    input_data = f.readline().split(",")
    max_deg = int(input("Enter max degree of tree: "))
    b_tree = BPlusTree(max_deg)
    for i in range(len(input_data)):
        b_tree.insert(int(input_data[i]), f"Record {i + 1}")
    display_tree(b_tree.root)


if __name__ == "__main__":
    __main__()
