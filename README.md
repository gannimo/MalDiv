MalDiv
======

Abstract
--------

Signature-based similarity metrics are the primary mechanism to detect malware
on current systems. Each file is scanned and compared against a set of
signatures. This approach has several problems: (i) all possible detectable
malware must have a signature in the database and (ii) it might take a
substantial amount of time between initial spread of the malware and the time
anti-malware companies generate a signature to protect from the malware. 

On the other hand, the malware landscape is changing: there are only few
malware families alive at a certain point in time. Each family evolves along
a common software update and maintenance cycle. Individual malware instances
are repacked or obfuscated whenever they are detected by a large set of
anti-malware products, basically resulting in an arms race between malware
authors and anti-malware products.

Anti-malware products are not efficient if they follow this arms race and we
show how it is possible to maximize the advantage for malware distributors.
We present MalDiv, an automatic diversification mechanism that uses
compiler-based transformations to generate an almost infinite amount of
binaries with the same functionality but very low similarity, resulting in
different signatures. Malware diversity builds on software diversity and uses
open decisions in the compiler to reorder and change code and data. In
addition, static data is encrypted using a set of transformations. Such a tool
allows malware distributors to generate an almost unlimited amount of binaries
that cannot be detected using signature-based matching.


Contents
--------

The following subdirectories and files are in this repository:
- README.md: you guessed it
- INSTALL: use this file to build a diversifying LLVM and clang
- src: will keep the sources for the LLVM and clang compiler
- bin: will keep the compiled binaries
- test: contains a set of simple examples

