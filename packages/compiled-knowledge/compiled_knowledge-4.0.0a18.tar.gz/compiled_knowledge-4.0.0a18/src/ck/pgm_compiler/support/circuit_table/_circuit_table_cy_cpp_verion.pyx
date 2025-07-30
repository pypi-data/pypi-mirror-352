# distutils: language = c++

from typing import Sequence, Tuple, Iterable, Optional, TypeAlias, Set

from ck.circuit import ADD, MUL

cdef int c_ADD = ADD
cdef int c_MUL = MUL

from ck.circuit._circuit_cy cimport Circuit, CircuitNode

from libcpp.vector cimport vector
from libcpp.unordered_set cimport unordered_set
from libcpp.unordered_map cimport unordered_map
from libcpp.pair cimport pair

from cpython.ref cimport PyObject, Py_INCREF, Py_DECREF
from cython.operator cimport dereference as deref, postincrement as incr


# Inject a hash function for vector[int] into the standard namespace
cdef extern from "_vector_hash.h" namespace "ck":
    cdef size_t hash_std_vector_int(vector[int])

ctypedef vector[int] Key
ctypedef vector[int].iterator KeyIterator

ctypedef vector[int] IntVec
ctypedef vector[int].iterator IntVecIterator

ctypedef unordered_set[int] IntSet
ctypedef unordered_set[int].iterator IntSetIterator

# KeyMap defined below
ctypedef unordered_map[Key, PyObject *].iterator KeyMapIterator
ctypedef pair[Key, PyObject *] KeyMapItem

# NodeVec defined below
ctypedef vector[PyObject *].iterator NodeVecIterator

TableInstance: TypeAlias = Sequence[int]

cdef class KeyMap:
    """
    A map from a Key (hashable STL vector) to a Python CircuitNode object.
    """

    cdef unordered_map[Key, PyObject *] _items

    cdef void put(self, Key key, CircuitNode node):
        Py_INCREF(node)
        self._items[key] = <PyObject *> node

    cdef Optional[CircuitNode] get(self, Key key):
        cdef CircuitNode node
        cdef KeyMapIterator it = self._items.find(key)
        if it == self._items.end():
            return None
        else:
            node = <CircuitNode> deref(it).second
            return node

    cdef void sum(self, Key key, CircuitNode node):
        # Add the given node to the node at `key`.
        cdef CircuitNode existing_node
        cdef KeyMapIterator it = self._items.find(key)
        if it == self._items.end():
            self.put(key, node)
        else:
            existing_node = <CircuitNode> deref(it).second
            self.put(key, _optimised_add(existing_node, node))

    cdef size_t size(self):
        return self._items.size()

    cdef KeyMapIterator begin(self):
        return self._items.begin()

    cdef KeyMapIterator end(self):
        return self._items.end()

    def instances(self) -> Iterable[TableInstance]:
        """
        Get the keys as Python objects of type TableInstance.
        """
        cdef KeyMapItem item
        for item in self._items:
            yield _key_to_instance(item.first)

    def values(self) -> Iterable[CircuitNode]:
        """
        Get the values as Python CircuitNode objects.
        """
        cdef KeyMapItem item
        for item in self._items:
            yield <CircuitNode> item.second

    def instance_values(self) -> Iterable[Tuple[TableInstance, CircuitNode]]:
        """
        Get the values as Python CircuitNode objects.
        """
        cdef KeyMapItem item
        for item in self._items:
            yield _key_to_instance(item.first), <CircuitNode> item.second

    cdef void clear(self):
        for pair in self._items:
            Py_DECREF(<object> pair.second)
        self._items.clear()

    def __dealloc__(self):
        self.clear()

cdef class NodeVec:
    cdef vector[PyObject *] _items

    cdef void push_back(self, CircuitNode node):
        Py_INCREF(node)
        self._items.push_back(<PyObject *> node)

    cdef CircuitNode at(self, int i):
        cdef CircuitNode node = <CircuitNode> self._items.at(i)
        return node

    cdef NodeVecIterator begin(self):
        return self._items.begin()

    cdef NodeVecIterator end(self):
        return self._items.end()

    cdef void clear(self):
        for ptr in self._items:
            Py_DECREF(<object> ptr)
        self._items.clear()

    def __dealloc__(self):
        self.clear()

cdef class CircuitTable:
    """
    A circuit table manages a set of CircuitNodes, where each node corresponds
    to an instance for a set of (zero or more) random variables.

    Operations on circuit tables typically add circuit nodes to the circuit. It will
    heuristically avoid adding unnecessary nodes (e.g. addition of zero, multiplication
    by zero or one.) However, it may be that interim circuit nodes are created that
    end up not being used. Consider calling `Circuit.remove_unreachable_op_nodes` after
    completing all circuit table operations.

    It is generally expected that no CircuitTable row will be created with a constant
    zero node. These are assumed to be optimised out already. This expectation
    is not enforced by the CircuitTable class.
    """
    cdef public Circuit circuit
    cdef public tuple[int, ...] rv_idxs
    cdef IntVec vec_rv_idxs
    cdef KeyMap rows

    def __init__(
            self,
            circuit: Circuit,
            rv_idxs: Sequence[int],
            rows: Iterable[Tuple[TableInstance, CircuitNode]] = (),
    ):
        """
        Args:
            circuit: the circuit whose nodes are being managed by this table.
            rv_idxs: indexes of random variables.
            rows: optional rows to add to the table.

        Assumes:
            * rv_idxs contains no duplicates.
            * all row instances conform to the indexed random variables.
            * all row circuit nodes belong to the given circuit.
        """
        self.circuit = circuit
        self.rv_idxs = tuple(rv_idxs)

        self.vec_rv_idxs = IntVec()
        for rv_id in self.rv_idxs:
            self.vec_rv_idxs.push_back(rv_id)

        self.rows = KeyMap()
        instance: TableInstance
        node: CircuitNode
        for instance, node in rows:
            self.rows.put(_instance_to_key(instance), node)

    cdef void add_row(self, tuple[int, ...] instance, CircuitNode node):
        self.rows.put(_instance_to_key(instance), node)

    cdef void put(self, Key key, CircuitNode value):
        self.rows.put(key, value)

    def __len__(self) -> int:
        return self.rows.size()

    def get(self, instance: TableInstance, default=None):
        value: Optional[CircuitNode] = self.rows.get(_instance_to_key(instance))
        if value is None:
            return default
        else:
            return value

    def __getitem__(self, instance: TableInstance) -> CircuitNode:
        value: Optional[CircuitNode] = self.rows.get(_instance_to_key(instance))
        if value is None:
            raise KeyError('instance not found: ' + str(instance))
        return value

    def __setitem__(self, instance: TableInstance, value: CircuitNode):
        self.put(_instance_to_key(instance), value)

    def keys(self) -> Iterable[TableInstance]:
        return self.rows.instances()

    def values(self) -> Iterable[CircuitNode]:
        return self.rows.values()

    def items(self) -> Iterable[Tuple[TableInstance, CircuitNode]]:
        return self.rows.instance_values()

    cpdef CircuitNode top(self):
        # Get the circuit top value.
        #
        # Raises:
        #     RuntimeError if there is more than one row in the table.
        #
        # Returns:
        #     A single circuit node.
        cdef CircuitNode node
        cdef KeyMapIterator it
        cdef size_t number_of_rows = self.rows.size()
        if number_of_rows == 0:
            return self.circuit.zero
        elif number_of_rows == 1:
            it = self.rows.begin()
            node = <CircuitNode> deref(it).second
            return node
        else:
            raise RuntimeError('cannot get top node from a table with more that 1 row')


# ==================================================================================
#  Circuit Table Operations
# ==================================================================================


def sum_out(table: CircuitTable, rv_idxs: Iterable[int]) -> CircuitTable:
    """
    Return a circuit table that results from summing out
    the given random variables of this circuit table.

    Normally this will return a new table. However, if rv_idxs is empty,
    then the given table is returned unmodified.

    Raises:
        ValueError if rv_idxs is not a subset of table.rv_idxs.
        ValueError if rv_idxs contains duplicates.
    """
    return _sum_out(table, tuple(rv_idxs))

def project(table: CircuitTable, rv_idxs: Iterable[int]) -> CircuitTable:
    """
    Project the given table onto the given random variables.
    Equivalent to `sum_out(table, to_sum_out)`, where `to_sum_out = table.rv_idxs - rv_idxs`.
    """
    to_sum_out: Set[int] = set(table.rv_idxs)
    to_sum_out.difference_update(rv_idxs)
    return _sum_out(table, tuple(to_sum_out))

def sum_out_all(table: CircuitTable) -> CircuitTable:
    """
    Return a circuit table that results from summing out
    all random variables of this circuit table.
    """
    return _sum_out_all(table)

def product(x: CircuitTable, y: CircuitTable) -> CircuitTable:
    """
    Return a circuit table that results from the product of the two given tables.

    If x or y have a single row with value 1, then the other table is returned. Otherwise,
    a new circuit table will be constructed and returned.
    """
    return _product(x, y)

cdef CircuitTable _product(CircuitTable x, CircuitTable y):
    cdef int i
    cdef Circuit circuit = x.circuit
    if y.circuit is not circuit:
        raise ValueError('circuit tables must refer to the same circuit')

    # Make the smaller table 'y', and the other 'x'.
    # This is to minimise the index size on 'y'.
    if x.rows.size() < y.rows.size():
        x, y = y, x

    # Special case: y == 0 or 1, and has no random variables.
    if y.vec_rv_idxs.size() == 0:
        if y.rows.size() == 1 and y.top().is_one:
            return x
        elif y.rows.size() == 0:
            return CircuitTable(circuit, x.rv_idxs)

    # Set operations on rv indexes. After these operations:
    # * co_rv_idxs is the set of rv indexes common (co) to x and y,
    # * yo_rv_idxs is the set of rv indexes in y only (yo), and not in x.
    cdef IntSet yo_rv_idxs_set = IntSet()
    cdef IntSet co_rv_idxs_set = IntSet()
    yo_rv_idxs_set.insert(y.vec_rv_idxs.begin(), y.vec_rv_idxs.end())
    for i in x.vec_rv_idxs:
        if yo_rv_idxs_set.find(i) != yo_rv_idxs_set.end():
            co_rv_idxs_set.insert(i)
    for i in co_rv_idxs_set:
        yo_rv_idxs_set.erase(i)

    if co_rv_idxs_set.size() == 0:
        # Special case: no common random variables.
        return _product_no_common_rvs(x, y)

    # Convert random variable index sets to sequences
    cdef IntVec yo_rv_idxs = IntVec(yo_rv_idxs_set.begin(), yo_rv_idxs_set.end())  # y only random variables
    cdef IntVec co_rv_idxs = IntVec(co_rv_idxs_set.begin(), co_rv_idxs_set.end())  # common random variables

    # Cache mappings from result Instance to index into source Instance (x or y).
    # This will be used in indexing and product loops to pull our needed values
    # from the source instances.
    cdef IntVec co_from_x_map = IntVec()
    cdef IntVec co_from_y_map = IntVec()
    cdef IntVec yo_from_y_map = IntVec()
    for rv_index in co_rv_idxs:
        co_from_x_map.push_back(_find(x.vec_rv_idxs, rv_index))
        co_from_y_map.push_back(_find(y.vec_rv_idxs, rv_index))
    for rv_index in yo_rv_idxs:
        yo_from_y_map.push_back(_find(y.vec_rv_idxs, rv_index))

    # Index the y rows by common-only key (y is the smaller of the two tables).
    cdef unordered_map[Key, vector[KeyMapItem]] y_index = unordered_map[Key, vector[KeyMapItem]]()
    cdef unordered_map[Key, vector[KeyMapItem]].iterator y_index_find
    cdef IntVec co = IntVec()
    cdef IntVec yo = IntVec()
    cdef Key y_key
    cdef PyObject * y_node_ptr
    cdef KeyMapItem item
    cdef KeyMapIterator y_it = y.rows.begin()
    cdef KeyMapIterator y_end = y.rows.end()
    while y_it != y_end:
        y_key = deref(y_it).first
        y_node_ptr = deref(y_it).second
        incr(y_it)

        # Split y_key into the common part (co) and the remaining part (yo)
        co.clear()
        yo.clear()
        for i in co_from_y_map:
            co.push_back(y_key[i])
        for i in yo_from_y_map:
            yo.push_back(y_key[i])

        #  Append (yo, y_node) to y_index[co]
        y_index_find = y_index.find(co)
        item = KeyMapItem(yo, y_node_ptr)
        if y_index_find == y_index.end():
            y_index[co] = vector[KeyMapItem]()
            y_index_find = y_index.find(co)
        deref(y_index_find).second.push_back(item)

    cdef CircuitTable table = CircuitTable(circuit, x.rv_idxs + tuple(yo_rv_idxs))
    cdef KeyMap rows = table.rows

    # Iterate over x rows, inserting (instance, value).
    # Rows with constant node values of one are optimised out.
    cdef KeyMapIterator x_it = x.rows.begin()
    cdef KeyMapIterator x_end = x.rows.end()
    cdef Key x_key
    cdef CircuitNode x_node, y_node
    while x_it != x_end:
        x_key = deref(x_it).first
        x_node = <CircuitNode> deref(x_it).second
        incr(x_it)

        # Split x_key to get the common part (co)
        co.clear()
        for i in co_from_x_map:
            co.push_back(x_key[i])

        # Get the y rows matching co
        y_index_find = y_index.find(co)
        if y_index_find == y_index.end():
            # no matching y rows, continue to next x row
            continue

        if x_node.is_one:
            # Multiplying by one.
            # Iterate over matching y rows.
            for item in deref(y_index_find).second:
                yo = item.first
                y_node = <CircuitNode> item.second
                key = Key(x_key.begin(), x_key.end())
                key.insert(key.end(), yo.begin(), yo.end())  # append yo to x_key
                rows.put(key, y_node)
        else:
            # Iterate over matching y rows.
            for item in deref(y_index_find).second:
                yo = item.first
                y_node = <CircuitNode> item.second
                key = Key(x_key.begin(), x_key.end())
                key.insert(key.end(), yo.begin(), yo.end())  # append yo to x_key
                rows.put(key, _optimised_mul(x_node, y_node))

    return table


cdef CircuitTable _sum_out(CircuitTable table, tuple[int, ...] rv_idxs):
    cdef int rv_index, i

    cdef IntSet rv_idxs_set
    for py_rv_index in rv_idxs:
        rv_idxs_set.insert(py_rv_index)

    if rv_idxs_set.size() == 0:
        # nothing to do
        return table

    # Get all table rvs that are not being summed out, remaining_rv_idxs.
    # Sets index_map[i] to the location in table.rv_idxs for remaining_rv_idxs[i]
    cdef IntVec remaining_rv_idxs
    cdef IntVec index_map
    cdef IntSetIterator find_it
    cdef IntVecIterator rvs_it = table.vec_rv_idxs.begin()
    cdef IntVecIterator rvs_end = table.vec_rv_idxs.end()
    i = 0
    while rvs_it != rvs_end:
        rv_index = deref(rvs_it)
        find_it = rv_idxs_set.find(rv_index)
        if find_it == rv_idxs_set.end():
            remaining_rv_idxs.push_back(rv_index)
            index_map.push_back(i)
        incr(rvs_it)
        i += 1

    cdef size_t num_remaining = remaining_rv_idxs.size()
    if num_remaining == 0:
        # Special case: summing out all random variables
        return _sum_out_all(table)

    # Group all result nodes by remaining rvs, summing them up as they are encountered
    cdef Circuit circuit = table.circuit
    cdef CircuitTable result_table = CircuitTable(circuit, remaining_rv_idxs)
    cdef KeyMap groups = result_table.rows
    cdef KeyMapIterator it = table.rows.begin()
    cdef KeyMapIterator end = table.rows.end()
    cdef Key table_key
    cdef Key group_key
    cdef CircuitNode node
    # Make the result table from the group sums
    while it != end:
        table_key = deref(it).first
        node = <CircuitNode> deref(it).second
        group_key.clear()
        for i in index_map:
            group_key.push_back(table_key.at(i))
        groups.sum(group_key, node)
        incr(it)

    return result_table

cdef CircuitTable _sum_out_all(CircuitTable table):
    # Return a circuit table that results from summing out
    # all random variables of this circuit table.

    cdef Circuit circuit = table.circuit
    cdef size_t num_rows = table.rows.size()

    cdef KeyMapIterator it, end
    cdef CircuitNode node, next_node

    if num_rows == 0:
        return CircuitTable(circuit, ())
    else:
        it = table.rows.begin()
        end = table.rows.end()
        node = <CircuitNode> deref(it).second
        incr(it)
        while it != end:
            next_node = <CircuitNode> deref(it).second
            node = _optimised_add(node, next_node)
            incr(it)

    if node.is_zero:
        return CircuitTable(circuit, ())
    else:
        return CircuitTable(circuit, (), [((), node)])

cdef int _find(IntVec xs, int x):
    # Return index of x in xs or -1 if not found
    cdef int i
    for i in range(xs.size()):
        if xs[i] == x:
            return i
    return -1

cdef CircuitTable _product_no_common_rvs(CircuitTable x, CircuitTable y):
    # Return the product of x and y, where x and y have no common random variables.
    #
    # This is an optimisation of more general product algorithm as no index needs
    # to be construction based on the common random variables.
    #
    # Rows with constant node values of one are optimised out.
    #
    # Assumes:
    #     * There are no common random variables between x and y.
    #     * x and y are for the same circuit.
    cdef Circuit circuit = x.circuit

    cdef CircuitTable table = CircuitTable(circuit, x.rv_idxs + y.rv_idxs)

    cdef KeyMapIterator it_x = x.rows.begin()
    cdef KeyMapIterator it_y

    cdef KeyMapIterator end_x = x.rows.end()
    cdef KeyMapIterator end_y = y.rows.end()

    cdef CircuitNode node_x
    cdef CircuitNode node_y
    cdef CircuitNode node

    cdef Key key_x
    cdef Key key_y
    cdef Key key

    while it_x != end_x:
        it_y = y.rows.begin()
        key_x = deref(it_x).first
        node_x = <CircuitNode> deref(it_x).second
        if node_x.is_zero:
            pass
        elif node_x.is_one:
            while it_y != end_y:
                key_y = deref(it_y).first
                node_y = <CircuitNode> deref(it_y).second
                if node_y.is_zero:
                    pass
                else:
                    key = _join_keys(key_x, key_y)
                    table.rows.put(key, node_y)
                incr(it_y)
        else:
            while it_y != end_y:
                key_y = deref(it_y).first
                node_y = <CircuitNode> deref(it_y).second
                if node_y.is_zero:
                    pass
                else:
                    key = _join_keys(key_x, key_y)
                    node = _optimised_mul(node_x, node_y)
                    table.rows.put(key, node)
                incr(it_y)
        incr(it_x)
    return table

cdef Key _instance_to_key(object instance: Iterable[int]):
    cdef Key key
    for state_idx in instance:
        key.push_back(state_idx)
    return key

cdef tuple[int, ...] _key_to_instance(Key key):
    cdef list[int] instance = []
    cdef KeyIterator it = key.begin()
    while it != key.end():
        instance.append(deref(it))
        incr(it)
    return tuple(instance)

cdef Key _join_keys(Key x, Key y):
    cdef Key result = Key(x)
    cdef KeyIterator it = y.begin()
    while it != y.end():
        result.push_back(deref(it))
        incr(it)
    return result

cdef CircuitNode _optimised_add(CircuitNode x, CircuitNode y):
    if x.is_zero:
        return y
    if y.is_zero:
        return x
    return x.circuit.op(c_ADD, (x, y))

cdef CircuitNode _optimised_mul(CircuitNode x, CircuitNode y):
    if x.is_zero:
        return x
    if y.is_zero:
        return y
    if x.is_one:
        return y
    if y.is_one:
        return x
    return x.circuit.op(c_MUL, (x, y))
