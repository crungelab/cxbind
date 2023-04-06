# CxBind :chains:

pybind11 binding generator


## Clone
```bash
git clone https://github.com/crungelab/cxbind
cd cxbind
procure
```

## Virtual Environment
```bash
hatch shell
```

# Development

## Tool Chain

[pybind11](https://github.com/pybind/pybind11)

## Build

### Generate Bindings
```bash
cxbind
```

## Build for PyPI
```bash
cmake -S . -B _build -DCMAKE_INSTALL_PREFIX=cxbind
cmake --install _build
```