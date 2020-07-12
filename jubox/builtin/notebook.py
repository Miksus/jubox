from jubox import JupyterNotebook, CodeCell

from nbconvert.preprocessors import CellExecutionError
import sys
import traceback

def _get_cell_exc_info(tb):
    "Get the actual exception raised in the notebook (instead of the CellExecutionError)"
    tbs = [tb_next for tb_next in traceback.walk_tb(tb)]
    last_tb = tbs[-1]
    f_locals = last_tb[0].f_locals
    outputs = f_locals["outputs"]
    for output in outputs:
        if output["output_type"] == "error":
            ename = output["ename"]
            evalue = output["evalue"]
            traceback_ = output["traceback"]
            break
    else:
        ename = None
        evalue = None
        traceback_ = None

    cellno = f_locals["cell_index"]
    cell = f_locals["cell"]
    return dict(
        ename=ename,
        evalue=evalue,
        traceback='\n'.join(traceback_),
        cellno=cellno, # Number of cell
        cell=CodeCell(cell), # Failed cell
    )


def run_notebook(notebook,
                on_failure=None,
                on_success=None,
                on_finally=None,
                parameters=None,
                parameters_with_imports=False,
                silence=False,
                clear_outputs=True,
                parameter_tag="parameters",
                ignore_cells=None,
                kwds_run=None,
                **kwargs):
    """Convenient function to execute a notebook

    Arguments:
        notebook {[str, Path like, JupyterNotebook]} : Jupyter Notebook to run

        on_failure {function} : Function to call if execution fails. Optional  
            Arguments Passed:
                notebook {JupyterNotebook} : The executed notebook
                ename {str} : Raised exception name from the notebook
                evalue {str} : Raised exception value from the notebook
                traceback {str} : Raised exception traceback from the notebook
                cellno {int} : Index of the failed cell
                cell {CodeCell} : Failed cell
                exc_info {tuple} : Actual exception
                **kwargs
        
        on_success {function} : Function to call if execution success. Optional
            Arguments Passed:
                notebook {JupyterNotebook} : The executed notebook
                **kwargs

        on_finally {function} : Function to call after the execution. Optional
            Arguments Passed:
                notebook {JupyterNotebook} : The executed notebook
                status {str} : Outcome of the execution (either "fail" or "success")
                **kwargs

        parameters {dict} : Parameter dict for the notebook. Replaced to first cell 
                            containing tag specified in parameter_tag. Optional

        parameters_with_imports {bool} : Whether to add import statements to parameters 
                            (default: False)

        silence {bool} : Whether to silence the exception after execution or not
        clear_outputs {bool} : Whether to clear the outputs from the cells before execution.
        parameter_tag {str} : Cell tag for the parameters

        ignore_cells {Dict[str, Any]} : Dict for identifying cells to ignore for execution. See jubox.utils.cells_match
        kwds_run {Dict} : Keyword arguments 

        kwargs {dict} : Additional keyword arguments passed to on_failure, on_success & 
                            on_finally
    Returns:
    --------
        JupyterNotebook
    """
    notebook = JupyterNotebook(notebook)

    if parameters is not None:
        set_parameters(notebook, params=parameters, parameter_tag=parameter_tag, include_imports=parameters_with_imports)

    if clear_outputs:
        notebook.clear_outputs(inplace=True)

    kwds_run = {} if kwds_run is None else kwds_run

    status = None
    try:
        notebook(inplace=True, ignore=ignore_cells, **kwds_run)
    except CellExecutionError:
        status = "fail"

        exc_class, exc, tb = sys.exc_info()
        tbs = [tb_next for tb_next in traceback.walk_tb(tb)]
        cell_exc_info = _get_cell_exc_info(tb)

        if on_failure is not None:
            on_failure(
                notebook=notebook,
                exc_info=(exc_class, exc, tb),
                **cell_exc_info,
                **kwargs
            )
        if not silence:
            raise
    else:
        status = "success"
        if on_success is not None:
            on_success(
                notebook=notebook,
                **kwargs
            )
    finally:
        if on_finally is not None:
            on_finally(
                notebook=notebook,
                status=status,
                **kwargs
            )

    return notebook

def set_parameters(notebook, params=None, *, parameter_tag="parameters", include_imports=False):
    if params is None:
        params = {}

    parametrized_cell = CodeCell.from_variable_dict(params, include_imports=include_imports)

    param_cell = notebook.cells.get(tags=[parameter_tag])[0]
    param_cell.overwrite(parametrized_cell)
    param_cell.insert(0, "# This is autogenerated parameter cell\n")
