# Wrappers

Example:

```yaml
'struct.SDL_Window':
  gen_wrapper:
    type: 'Window'
```

If a struct or class is wrapped during generation we need to check the parameters and return values of all functions/methods we are generating bindings for.

Entries are looked up by the fqname of the wrapped type.

If an entry exists for a parameter or return node we need to substitute it with the type specified under `gen_wrapper`.