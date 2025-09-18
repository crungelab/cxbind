# Valgrind

```bash
valgrind --leak-check=yes python test_arguments.py
```

```bash
valgrind --leak-check=yes --suppressions=../valgrind/python-3.10.supp python test_arguments.py
```

```bash
valgrind --leak-check=full --show-leak-kinds=all --suppressions=../valgrind/python-3.10.supp python test_arguments.py
```

```bash
valgrind --leak-check=full --show-leak-kinds=all --suppressions=../valgrind/python-3.10.supp --log-file=memcheck.log python test_arguments.py
```

```bash
valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes \
 --suppressions=../valgrind/python-3.10.supp --log-file=memcheck.log python test_arguments.py
```
