# Documentation for rs-template

Welcome to `rs-template`! This page, `docs/index.md`, will become the homepage of your documentation. You can use markdown to make this page look nice, such as by **bolding** and *italicising* important things.

> Don't forget block quotes!

```python
also = "don't forget code blocks"
```

Your online documentation should include at least:
 - a "quickstart" page, which includes installation instructions and a very brief example/tutorial of package usage. This may live on the homepage (this page), or you may create a separate file `docs/quickstart.md` and just use this page as a landing page.
 - The relevant type(s) of API reference. Depending on your package structure, you may want to document the python API, the command-line API, or both. This website contains examples of both.

 <!-- Here's the syntax for your table of contents -->
 <!-- You only need to include this on this page, and it will automatically apply to the entire site -->

```{eval-rst}
.. toctree::
   :maxdepth: 1
   :hidden:

   Python API <api>
   Command-line API <cli>

```
