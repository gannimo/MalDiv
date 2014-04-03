#include <stdio.h>
#include <string.h>

const char foo[] = "foobar";
char bar[7];

int main(int argc, char* argv[]) {
	strcpy(bar, "barfoo");
	printf("Hello World %s %s\n", foo, bar);
  printf("Arguments: %d, executable: %s\n", argc, argv[0]);
	return 0;
}
