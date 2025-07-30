# CLI reference

Command-line API can be easily and automatically documented by including an RST block. The code looks like this:

```
{eval-rst}
.. autoprogram:: rs_template._command_line:create_parser()
   :prog: rs.template

```

note that you need to direct `autoprogram` to a specific file and function which **returns an `argparse.ArgumentParser` object** (or to an `argparse.ArgumentParser` object itself).

This will be rendered into your documentation:

```{eval-rst}
.. autoprogram:: rs_template._command_line:create_parser()
   :prog: rs.template

```
