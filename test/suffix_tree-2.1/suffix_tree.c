/* Python suffix tree, (C) Thomas Mailund <mailund@birc.dk> and
 *                         Søren Besenbacher <besen@birc.dk> */

#include "suffix_tree.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#define TRUE 1
#define FALSE 0




/* creates an internal node */
static node_t *
internal_node(node_t *parent, int start, int end, int depth,
	      int term_number,  node_t *suffix_link)
{
    node_t *tmp = (node_t*)malloc(sizeof(node_t));
    if (!tmp) return tmp;

    tmp->parent = parent;
    tmp->start = start;
    tmp->end = end;
    tmp->depth = depth;
    tmp->term_number = term_number;
    tmp->suffix_link = suffix_link;
    
    tmp->children.head = NULL;
    tmp->children.tail = NULL;

    tmp->prev = tmp->next = NULL;
    tmp->python_node = NULL;

    return tmp;
}

/* creates a leaf node */
static node_t *
leaf_node(node_t *parent, int start, int end, int depth, int term_number)
{
    node_t *tmp = (node_t*)malloc(sizeof(node_t));
    if (!tmp) return tmp;

    tmp->parent = parent;
    tmp->start = start;
    tmp->end = end;
    tmp->depth = depth;
    tmp->term_number = term_number;
    tmp->suffix_link = (node_t*)NULL;

    tmp->children.head = NULL;
    tmp->children.tail = NULL;

    tmp->prev = tmp->next = NULL;
    tmp->python_node = NULL;

    return tmp;
}


/* inserts element into doubly linked list */
static node_t *
insert(list_t *l, node_t *n)
{
    if(l->head == 0)
	{
	    l->head = l->tail = n;
	    n->prev = n->next = 0;
	}
    else
	{
	    n->prev = l->tail; n->next = 0;
	    l->tail->next = n;
	    l->tail = n;
	}
    return n;
}

/* replace old node with new in list */
static void
replace(list_t *l, node_t *old, node_t *new)
{
    /* first simply re-link nodes */
    new->prev = old->prev;
    new->next = old->next;
    if (old->next) old->next->prev = new;
    if (old->prev) old->prev->next = new;
    old->prev = old->next = 0;

    /* then re-wire head and tail if necessary */
    if (l->head == old)
	l->head = new;
    if (l->tail == old)
	l->tail = new;
}


/*
  inserts a new internal node at position pos on the edge
  between ln->elem and its parent.
*/
static node_t *
insertBefore(node_t *old, int pos)
{
    node_t *new = internal_node(old->parent, old->start, pos,
				(old->parent->depth)+(pos - (old->start))+1,
				old->term_number, NULL);
    replace(&(old->parent->children), old, new);
    insert(&(new->children), old);
    old->start = (pos + 1);
    old->parent = new;
    return new;
}

static node_t *
fastScan(suffix_tree_t *tree, node_t *n, int start, int end)
{
    int x = start;
    node_t *ln;

    if (start > end) return n;

    while (x < end+1)
	{
	    for (ln = n->children.head; ln; ln = ln->next)
		{
		    if(tree->str[ln->start] == tree->str[x])
			{
			    n = ln;
			    x = x + (n->end - n->start)+1;
			    break;
			}
		}
	}
    if (x > end+1)  // <=> x != end
	{
	    n = insertBefore(ln, n->end + end - x +1);
	    tree->new_node = TRUE;
	}
    return n;
}


static node_t *
slowScan(suffix_tree_t *tree, node_t *n, int start, int end)
{
    int tail_length = end - start + 1;
    node_t *ln;

    if (start > end) return n;

    for (ln = n->children.head; ln; ln = ln->next)
	{
	    if (tree->str[ln->start] == tree->str[start])
		{
		    int k = 0;
		    while (tree->str[ln->start + k] == tree->str[start + k])
			{
			    if (k == ln->end - ln->start)
				{
				    if (k + 1 == tail_length)
					{
					    return ln;
					} 
				    return slowScan(tree, ln, start+k+1, end);
				}
			    if (k + 1 == tail_length) 
				{
				    return insertBefore(ln, ln->start+k);
				}
			    k++;
			} 
		    return insertBefore(ln, ln->start+k-1);
		}
	}
    return n;
}


suffix_tree_t *
make_helper(char *s, int length)
{
    node_t *head_i;   /*  head_i == head(i)  */
    node_t *term_i;   /* term_i == terminal node i,
			 tail(i) == str[term_i.start...term_i.end] */
    int i;
    node_t *w;
    
    suffix_tree_t *tree = (suffix_tree_t*)malloc(sizeof(suffix_tree_t));
    if (!tree) return tree;

    tree->str = s;
    tree->str_len = length;
    tree->root = internal_node(NULL, -1, -1, 0, 0, NULL); 
    tree->root->suffix_link = tree->root;
  
    
    /* add str[0..length-1] */
    term_i = leaf_node(tree->root, 0, length-1, length, 0);
    insert(&(tree->root->children), term_i);
    head_i = tree->root; 
  
    for (i = 1; i < length; i++)
	{
	    tree->new_node = FALSE;
	    if (head_i == tree->root)
		head_i = slowScan(tree, tree->root, 
				  term_i->start+1, term_i->end);
	    else
		{
		    if(head_i->parent != tree->root)
			w = fastScan(tree,
				     head_i->parent->suffix_link, 
				     head_i->start, head_i->end); 
		    else
			w = fastScan(tree, tree->root, 
				     head_i->start + 1, head_i->end); 
		    head_i->suffix_link = w;
		    if (tree->new_node)
			head_i = w;
		    else 
			head_i = slowScan(tree, w, term_i->start, term_i->end);
		}
	    term_i = leaf_node(head_i, head_i->depth+i, 
			       length-1, length-i, i); 
	    insert(&(head_i->children), term_i);
	}

    return tree;
}

suffix_tree_t *
st_make(const char *s, const char term)
{
    const char *c;
    for (c = s; *c; ++c) 
	assert(*c != term); /* make sure `term' is not in the string */

    size_t string_length = strlen(s) + 2; // for `term' and \0
    char *t = malloc(string_length);
    strcpy(t,s);
    t[string_length-2] = term;

    return make_helper(t, string_length - 1);
}



static const node_t *
find_helper(const suffix_tree_t *tree, const node_t *n,
	    const char *s, int length)
{
    node_t *ln;

    if (length==0) return n;
    
    for (ln = n->children.head; ln; ln = ln->next)
	{
	    if (tree->str[ln->start] == s[0])
		{
		    int k = 0;
		    while (tree->str[ln->start + k] == s[k])
			{
			    if(k  == length-1)
				return ln;
			    if (k == ln->end - ln->start)
				return find_helper(tree, ln, 
						   &s[k+1], length-(k+1));
			    k++;
			}    
		}
	}
    return NULL; //pattern not recognized!
}

const node_t *
st_find(const suffix_tree_t *tree, const char *s)
{
    return find_helper(tree, tree->root, s, strlen(s));
}

