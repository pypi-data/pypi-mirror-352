# SexyPy : the Geekiest Python Ever!
SexyPy stands for **S-ex**_pression-ish(_**y**_)_ **Py**_thon_.   
Highly inspired by Clojure and Hy.   
Once I loved to use Hy when I need to use python. But as I started to learn Clojure, similarity between two languages confused me. I want a language more straightforward to being python but in S-expression so that I can exploit structural editing and metaprogramming by macro. Thus I decided to start this project.

# Documentation
You can find the documentation at [https://jethack23.github.io/sexypy/](https://jethack23.github.io/sexypy/).

# Installation
## Manual Installation (for development)
```bash
poetry install --no-root # for dependency
pip install -e . # for development
```
## Using pip
```bash
pip install sexypy
```

# How to Run sxpy code
## Run from source
```bash
spy {filename}.sy
```

## Run REPL
```bash
spy
#or
spy -t #if you want to print python translation.
```

## Run translation
```bash
s2py {filename}.sy
```
It just displays translation. (don't run it)

## Run Tests
```bash
# in project root directory
python -m unittest
#or
spy -m unittest
```


# Todo
## Environment
- [ ] Test on more python versions
- [ ] Some IDE plugins like hy-mode and jedhy for better editing experience.
## Macro System
- [ ] `as->` macro for syntactic sugar
- [ ] `gensym` for avoiding name collision
## Python AST
- [ ] `type_comment` never considered. Later, it should be covered