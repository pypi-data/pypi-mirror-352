from tko.run.unit import Unit
from tko.enums.execution_result import ExecutionResult
from tko.util.runner import Runner
from tko.run.solver_builder import SolverBuilder

class UnitRunner:

    def __init__(self):
        pass

    # run a unit using a solver and return if the result is correct
    @staticmethod
    def run_unit(solver: SolverBuilder, unit: Unit, timeout: None | float = None) -> ExecutionResult:
        exec, _ = solver.get_executable()
        if solver.has_compile_error():
            unit.received = exec.get_error_msg().get_str()
            return ExecutionResult.COMPILATION_ERROR
        cmd, folder = exec.get_command()
        if folder == "":
            folder = None
        if timeout == 0:
            timeout = None
        return_code, stdout, stderr = Runner.subprocess_run(cmd, unit.inserted, timeout, folder)
        unit.received = stdout + stderr
        if return_code != 0:
            return ExecutionResult.EXECUTION_ERROR
        if unit.received == unit.expected:
            return ExecutionResult.SUCCESS
        return ExecutionResult.WRONG_OUTPUT