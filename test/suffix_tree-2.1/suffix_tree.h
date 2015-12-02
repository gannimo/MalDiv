/* Python suffix tree, (C) Thomas Mailund <mailund@birc.dk> and
 *                         Søren Besenbacher <besen@birc.dk> */

#ifndef SUFFIX_TREE_H_INCLUDED
#define SUFFIX_TREE_H_INCLUDED

/* doubly linked list */
struct list {
    struct node *head;
    struct node *tail;
};
typedef struct list list_t;


/* node in suffix tree */
struct node {
    struct node *parent;
    int start;           /* label(parent, this) = str[start..end] */
    int end;             
    int depth;
    int term_number;     /* if internal it is the terminal number of a
			  * descendent */
    struct node *suffix_link; 
    list_t children;

    /* doubly linked list part */
    struct node *next;
    struct node *prev;

    /* link to python -- needed to make sure we always get the same
       python object when we ask for a node */
    struct NodeObject *python_node;
};
typedef struct node node_t;



struct suffix_tree {
    char *str;
    int str_len;
    node_t *root;
    int new_node;
};
typedef struct suffix_tree suffix_tree_t;



/* builds a suffix tree for the string s -- s must NOT contain the
   special character `term' (term ensures that all suffixes are leaves) */
suffix_tree_t *       st_make(const char *s, const char term);
const node_t *        st_find(const suffix_tree_t *tree, const char *s);



#endif
