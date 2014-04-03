BINpath=../bin/Release+Asserts/bin
LIBpath=../bin/Release+Asserts/lib

CC=$(BINpath)/clang
OPTS=-O3

RNG=2

MalDivFlags=-frandom-seed=$(RNG) -Xclang -nop-insertion -Xclang -nop-insertion-percentage=50 -Xclang -shuffle-stack-frames -Xclang -max-stack-pad-size=1024 -Xclang -pre-RA-randomizer-range=-1 -Xclang -isched-rand-percentage=50 -Xclang -randomize-function-list

all: hello

hello: hello.c
	$(CC) $(OPTS) -emit-llvm hello.c -c -o hello.bc
	$(BINpath)/opt -load $(LIBpath)/LLVMObjDiv.so -GVDiv -rng-seed=$(RNG) hello.bc > hello2.bc
	$(BINpath)/clang $(OPTS) $(MalDivFlags) hello2.bc -S -o hello.s
	gcc hello.s -o hello.native
