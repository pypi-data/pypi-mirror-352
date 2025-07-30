try:
    from IPython.core.magic import Magics, cell_magic, magics_class
except ImportError as e:
    import_error = e

    def load_ipython_extension(_):
        raise ImportError(f"IPython was not able to be imported: {import_error!r}")

else:
    # TODO: Update fused.load for raw source?
    from fused.core._udf_ops import load_udf_from_code

    @magics_class
    class FusedMagics(Magics):
        """Fused IPython Magics Collection"""

        # Function name is used as the magic name
        @cell_magic
        def udf(self, udf_name, udf_source):
            """Create a UDF out of the content of the cell block

            '%%udf udf_name' creates a UDF with the name 'udf_name'
            """
            udf = load_udf_from_code(udf_source, udf_name)
            self.shell.user_ns[udf_name] = udf

    def load_ipython_extension(ipython):
        ipython.register_magics(FusedMagics)
