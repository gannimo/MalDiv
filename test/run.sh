#!/bin/bash
for i in `seq 100`; do 
	RNG=$i make 
	cp hello.s gen/$i.s 
done
