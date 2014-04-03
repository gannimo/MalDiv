BINpath=/home/gannimo/Cal/projects/MalwareDiversity/multi-syscan/bin/Release+Asserts/bin
LIBpath=/home/gannimo/Cal/projects/MalwareDiversity/multi-syscan/bin/Release+Asserts/lib

CC=$(BINpath)/clang
OPTS=-O3 -emit-llvm


all: hello

hello: hello.c
	$(CC) $(OPTS) hello.c -c -o hello.bc
	$(BINpath)/opt -load $(LIBpath)/LLVMObjDiv.so -GVDiv -rng-seed=1 hello.bc > hello2.bc
	$(BINpath)/llc hello2.bc -o hello.s
	gcc hello.s -o hello.native
