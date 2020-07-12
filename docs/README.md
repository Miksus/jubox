## Version History
* 0.4.0
    - run_notebook function for conveniently parametrize and run notebooks
    - Accessor system.
        - Deprecated:
            - JupyterNotebook.get_cells(...), please use JupyterNotebook.cells.get(...)
            - JupyterNotebook.code_cells(...),  please use JupyterNotebook.cells.code
            - JupyterNotebook.raw_cells, please use JupyterNotebook.cells.raw
            - JupyterNotebook.markdown_cells, please use JupyterNotebook.cells.markdown
            - JupyterNotebook.error_cells, please use JupyterNotebook.cells.errors

            - CodeCell.streams, please use CodeCell.outputs.streams
            - CodeCell.display_data, please use CodeCell.outputs.display_data
            - CodeCell.execution_results, please use CodeCell.outputs.execution_results
        - CodeCell.outputs and JupyterNotebook.cells now return feature rich accessors
    - Various fixes and small feature additions
* 0.3.0
    - Initial release version
