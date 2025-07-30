# Python API reference

Python API can be easily documented with sphinx. For more information on all of the options, check out [sphinx's documentation](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html). The [reciprocalspaceship docs](https://github.com/rs-station/reciprocalspaceship/tree/main/docs) also do some clever things with sphinx.

In the simplest form, the following code creates the documentation below for the entire module (in this case, all functions living inside the file `python_library.py`). You can include more of these blocks to document other modules as desired; you could also document different modules on different pages.

```
{eval-rst}
.. automodule:: rs_template.python_library
   :members:
```

```{eval-rst}
.. automodule:: rs_template.python_library
   :members:

```
