/* Python suffix tree, (C) Thomas Mailund <mailund@birc.dk> and
 *                         Søren Besenbacher <besen@birc.dk> */

#include "suffix_tree.h"
#include <Python.h>
#include <structmember.h>


typedef struct SuffixTreeObject {
    PyObject_HEAD
    suffix_tree_t *tree;
} SuffixTreeObject;

typedef struct NodeObject {
    PyObject_HEAD

    /* Add dictionary to handle user-annotation */
    PyObject *dict;

    SuffixTreeObject *tree;
    node_t *node;
} NodeObject;

static PyObject *SuffixTree_new         (PyTypeObject              *type,
                                         PyObject                  *args,
                                         PyObject                  *kwds);
static int       SuffixTree_init        (SuffixTreeObject          *self,
					 PyObject                  *args,
					 PyObject                  *kwds);
static PyObject *SuffixTree_root        (SuffixTreeObject          *self);
static PyObject *SuffixTree_string      (SuffixTreeObject          *self);


static PyObject* wrap_node              (SuffixTreeObject          *tree,
					 node_t                    *n);


static PyObject *Node_new               (PyTypeObject              *type,
                                         PyObject                  *args,
                                         PyObject                  *kwds);
static void      Node_dealloc           (NodeObject                *self);

static int       Node_compare           (NodeObject                *n1,
					 NodeObject                *n2);
static long      Node_hash              (NodeObject                *self);

static PyObject *Node_start             (NodeObject                *self);
static PyObject *Node_end               (NodeObject                *self);
static PyObject *Node_index             (NodeObject                *self);
static PyObject *Node_string_depth      (NodeObject                *self);

static PyObject *Node_edge_label        (NodeObject                *self);
static PyObject *Node_path_label        (NodeObject                *self);
static PyObject *Node_suffix            (NodeObject                *self);

static PyObject *Node_parent            (NodeObject                *self);
static PyObject *Node_next              (NodeObject                *self);
static PyObject *Node_prev              (NodeObject                *self);
static PyObject *Node_first_child       (NodeObject                *self);
static PyObject *Node_last_child        (NodeObject                *self);

static PyObject *Node_is_leaf           (NodeObject                *self);


/**********************************************************************/
/* exporting stuff to python */
/**********************************************************************/

static PyGetSetDef SuffixTree_getseters[] = {
    {"root", (getter)SuffixTree_root, NULL,
     "The root-node of the tree.", 
     NULL /* no closure */
    },
    {"string", (getter)SuffixTree_string, NULL,
     "The string the tree is built over + the terminal symbol.",
     NULL /* no closure */
    },

    {0} /* sentinel */
};

/* FIXME: deallocation of this guy! */
static PyTypeObject SuffixTreeType = {
    PyObject_HEAD_INIT(NULL)
    .tp_name      = "_suffix_tree.SuffixTree",
    .tp_basicsize = sizeof(SuffixTreeObject),
    .tp_flags     = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_doc       = "Suffix tree object",
    .tp_getset    = SuffixTree_getseters,
    .tp_init      = (initproc)SuffixTree_init,
    .tp_new       = SuffixTree_new,
};


static PyGetSetDef Node_getseters[] = {
    {"start", (getter)Node_start, NULL,
     "The start index of the label on the edge from parent to this node.",
     NULL /* no closure */
    },
    {"end", (getter)Node_end, NULL,
     "The end index of the label on the edge from parent to this node.",
     NULL /* no closure */
    },
    {"index", (getter)Node_index, NULL,
     "If the node is a leaf, this is the start of the suffix.  If the node "
     "is an inner node, it is the index of one of its leaves.",
     NULL /* no closure */
    },
    {"stringDepth", (getter)Node_string_depth, NULL,
     "The string depth (length of the path label) of this node. "
     "Notice that this is not the *tree* depth, that is, not the number of "
     "nodes between the root and this node,",
     NULL /* no closure */
    },

    {"edgeLabel", (getter)Node_edge_label, NULL,
     "The label on the edge to this node's parent (string[start:end+1]).",
     NULL /* no closure */
    },
    {"pathLabel", (getter)Node_path_label, NULL,
     "The label on the path to this node from the root.",
     NULL /* no closure */
    },
    {"suffix", (getter)Node_suffix, NULL,
     "The string string[index:], which for leaves is the correct suffix "
     "but for inner nodes is really just some suffix.",
     NULL /* no closure */
    },


    {"parent", (getter)Node_parent, NULL,
     "The parent of this node, or None if the node is the root.",
     NULL /* no closure */
    },
    {"next", (getter)Node_next, NULL,
     "The next sibling of this node, or None.",
     NULL /* no closure */
    },
    {"prev", (getter)Node_prev, NULL,
     "The previous sibling of this node, or None.",
     NULL /* no closure */
    },
    {"firstChild", (getter)Node_first_child, NULL,
     "The first child of this node, or None.",
     NULL /* no closure */
    },
    {"lastChild", (getter)Node_last_child, NULL,
     "The last child of this node, or None.",
     NULL /* no closure */
    },

    { "isLeaf", (getter)Node_is_leaf, NULL,
      "Predicate that is true if self is a leaf, false otherwise.", NULL
    },

    {0} /* sentinel */
};

static PyTypeObject NodeType = {
    PyObject_HEAD_INIT(NULL)
    .tp_name       = "_suffix_tree.SuffixTreeNode",
    .tp_basicsize  = sizeof(NodeObject),
    .tp_flags      = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_doc        = "Suffix tree node object",
    .tp_dealloc    = (destructor)Node_dealloc,
    .tp_compare    = (cmpfunc)Node_compare,
    .tp_hash       = (hashfunc)Node_hash,
    .tp_getset     = Node_getseters,
    .tp_dictoffset = offsetof(NodeObject,dict),
    .tp_new        = Node_new,
};



static PyMethodDef _suffix_tree_methods[] = {
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
init_suffix_tree(void) 
{
    if (PyType_Ready(&SuffixTreeType) < 0) return;
    if (PyType_Ready(&NodeType) < 0) return;

    Py_INCREF(&SuffixTreeType);
    Py_INCREF(&NodeType);

    PyObject* m = Py_InitModule3("_suffix_tree", _suffix_tree_methods,
				 "Wrapper module for suffix trees.");
    PyModule_AddObject(m, "SuffixTree", (PyObject *)&SuffixTreeType);
}








/**********************************************************************/
/* tree bindings */
/**********************************************************************/


static PyObject *
SuffixTree_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    SuffixTreeObject *self = (SuffixTreeObject *)type->tp_alloc(type, 0);
    self->tree = NULL;
    return (PyObject*)self;
}

static int
SuffixTree_init(SuffixTreeObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *string = NULL;
    PyObject *terminal = NULL;
    static char *kwlist[] = {"string", "terminal", NULL};

    if (! PyArg_ParseTupleAndKeywords(args, kwds, "|ss", kwlist, 
				      &string, &terminal))
        return -1; 		/* rethrow exception */

    char *s; char *t; int n;
    if (!(string = PyTuple_GetItem(args,0)))      return -1; /* rethrow */
    if (!(terminal = PyTuple_GetItem(args,1)))    return -1; /* rethrow */
    /* n is actually ignored here -- the size of string s is strlen(s) */
    if (PyString_AsStringAndSize(string,&s,&n))   return -1; /* rethrow */
    if (PyString_AsStringAndSize(terminal,&t,&n)) return -1; /* rethrow */
    if (n != 1) // not a single terminal symbol
	{
	    PyErr_SetString(PyExc_RuntimeError,
			    "Terminal symbol must be a single character!");
	    return -1;
	}

    self->tree = st_make(s,*t);
    if (!self->tree) {
	PyErr_SetString(PyErr_NoMemory(),"Could not allocated suffix tree!");
	return -1;
    }

    return 0;
}

static PyObject *
SuffixTree_string(SuffixTreeObject *self)
{
    return PyString_FromStringAndSize(self->tree->str, self->tree->str_len);
}


static PyObject* 
wrap_node(SuffixTreeObject *tree, node_t *n)
{
    if (n->python_node)
	{
	    Py_INCREF((PyObject*)n->python_node);
	    return (PyObject*)n->python_node;
	}

    NodeObject *node = (NodeObject*)_PyObject_New((PyTypeObject*)&NodeType);
    if (!node) return 0;

    node->dict = PyDict_New();
    node->tree = tree;
    node->node = n;

    //Py_INCREF((PyObject*)tree); //FIXME: handle cyclic GC and make
    //sure tree isn't deleted while we have a node

    // make sure the node is never deleted while the tree is in existence
    Py_INCREF(node);
    n->python_node = node;

    return (PyObject*)node;
}

static PyObject*
SuffixTree_root(SuffixTreeObject *self)
{
    return wrap_node(self,self->tree->root);
}




/**********************************************************************/
/* node bindings */
/**********************************************************************/

static PyObject *
Node_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    NodeObject *self = (NodeObject *)type->tp_alloc(type, 0);
    self->dict = NULL;
    self->tree = NULL;
    self->node = NULL;
    return (PyObject*)self;
}

static int
Node_clear(NodeObject *self)
{
    Py_XDECREF(self->dict); self->dict = NULL;
    Py_XDECREF(self->tree); self->tree = NULL;
    return 0;
}

static void
Node_dealloc(NodeObject *self)
{
    Node_clear(self);
    self->ob_type->tp_free((PyObject*)self);
}

static int
Node_compare(NodeObject *n1, NodeObject *n2)
{
    return (int)(n1->node - n2->node);
}

static long
Node_hash(NodeObject *self)
{
    return (long)(self->node);
}




static PyObject *
Node_start(NodeObject *self)
{
    return PyInt_FromLong(self->node->start);
}

static PyObject *
Node_end(NodeObject *self)
{
    return PyInt_FromLong(self->node->end);
}

static PyObject *
Node_index(NodeObject *self)
{
    return PyInt_FromLong(self->node->term_number);
}

static PyObject *
Node_string_depth(NodeObject *self)
{
    return PyInt_FromLong(self->node->depth);
}


static PyObject *
Node_edge_label(NodeObject *self)
{
    int start = self->node->start;
    int end = self->node->end+1;
    int length = end-start;

    /* the root is a special case... */
    if (start < 0) return PyString_FromStringAndSize("", 0);
    return PyString_FromStringAndSize(self->tree->tree->str + start, length);
}

static PyObject *
Node_path_label(NodeObject *self)
{
    int start = self->node->term_number;
    int length = self->node->depth;

    return PyString_FromStringAndSize(self->tree->tree->str + start, length);
}

static PyObject *
Node_suffix(NodeObject *self)
{
    int start = self->node->term_number;
    int length = self->tree->tree->str_len - start;
    /* the root is a special case... */
    if (start < 0) return SuffixTree_string(self->tree);
    return PyString_FromStringAndSize(self->tree->tree->str + start, length);
}




static PyObject *
Node_parent(NodeObject *self)
{
    node_t *parent = self->node->parent;
    if (!parent)
	{
	    Py_INCREF(Py_None);
	    return Py_None;
	}
    else
	{
	    return wrap_node(self->tree,parent);
	}
}

static PyObject *
Node_next(NodeObject *self)
{
    node_t *next = self->node->next;
    if (!next)
	{
	    Py_INCREF(Py_None);
	    return Py_None;
	}
    else
	{
	    return wrap_node(self->tree,next);
	}
}

static PyObject *
Node_prev(NodeObject *self)
{
    node_t *prev = self->node->prev;
    if (!prev)
	{
	    Py_INCREF(Py_None);
	    return Py_None;
	}
    else
	{
	    return wrap_node(self->tree,prev);
	}
}

static PyObject *
Node_first_child(NodeObject *self)
{
    node_t *c = self->node->children.head;
    if (!c)
	{
	    Py_INCREF(Py_None);
	    return Py_None;
	}
    else
	{
	    return wrap_node(self->tree,c);
	}
}

static PyObject *
Node_last_child(NodeObject *self)
{
    node_t *c = self->node->children.tail;
    if (!c)
	{
	    Py_INCREF(Py_None);
	    return Py_None;
	}
    else
	{
	    return wrap_node(self->tree,c);
	}
}

static PyObject*
Node_is_leaf(NodeObject *self)
{
    if (self->node && self->node->children.head)
	{ Py_INCREF(Py_False); return Py_False; }
    else
	{ Py_INCREF(Py_True); return Py_True; }
}
