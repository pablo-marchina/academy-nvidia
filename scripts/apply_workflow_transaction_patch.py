#!/usr/bin/env python3
"""Apply the one-time workflow transaction recovery fix."""
from pathlib import Path

runner_path = Path("src/orchestration/runner.py")
runner = runner_path.read_text(encoding="utf-8")

old = '''        self.repo.update_workflow_status(
            state.workflow_id,
            status=WorkflowStatus.RUNNING,
            current_node="",
            state_json=self._dump_state(state),
        )

        thread_id = state.analysis_run_id or state.workflow_id
'''
new = '''        self.repo.update_workflow_status(
            state.workflow_id,
            status=WorkflowStatus.RUNNING,
            current_node="",
            state_json=self._dump_state(state),
        )
        # Establish a durable workflow/analysis boundary before node execution.
        # If a later node flush fails, rolling back must not delete the workflow
        # record that is needed to persist the concrete failure for the API/UI.
        self.session.commit()

        thread_id = state.analysis_run_id or state.workflow_id
'''
if old not in runner:
    raise RuntimeError("workflow running boundary pattern not found")
runner = runner.replace(old, new, 1)

old = '''        except NodeExecutionError as exc:
            self._fail_state(state, exc.error_message or f"Node failed: {exc.node_name}", node_name=exc.node_name)
            return state
        except Exception as exc:
            node_name = state.current_node or "workflow_execution"
            self._fail_state(
'''
new = '''        except NodeExecutionError as exc:
            # A failed flush leaves SQLAlchemy in PendingRollbackError state.
            # Restore the session before writing the durable workflow failure.
            self.session.rollback()
            self._fail_state(state, exc.error_message or f"Node failed: {exc.node_name}", node_name=exc.node_name)
            return state
        except Exception as exc:
            self.session.rollback()
            node_name = state.current_node or "workflow_execution"
            self._fail_state(
'''
if old not in runner:
    raise RuntimeError("workflow exception pattern not found")
runner = runner.replace(old, new, 1)

old = '''        self._sync_analysis_run(state, status=WorkflowStatus.RUNNING)

        token = session_var.set(self.session)
'''
new = '''        self._sync_analysis_run(state, status=WorkflowStatus.RUNNING)
        self.session.commit()

        token = session_var.set(self.session)
'''
if old not in runner:
    raise RuntimeError("resume running boundary pattern not found")
runner = runner.replace(old, new, 1)

old = '''        except NodeExecutionError as exc:
            self._fail_state(state, exc.error_message or f"Node failed: {exc.node_name}", node_name=exc.node_name)
            return state
        except Exception as exc:
            self._fail_state(
                state,
                f"Workflow resume failed: {type(exc).__name__}: {exc}",
'''
new = '''        except NodeExecutionError as exc:
            self.session.rollback()
            self._fail_state(state, exc.error_message or f"Node failed: {exc.node_name}", node_name=exc.node_name)
            return state
        except Exception as exc:
            self.session.rollback()
            self._fail_state(
                state,
                f"Workflow resume failed: {type(exc).__name__}: {exc}",
'''
if old not in runner:
    raise RuntimeError("resume exception pattern not found")
runner = runner.replace(old, new, 1)
runner_path.write_text(runner, encoding="utf-8")
Path(__file__).unlink()
print("workflow transaction recovery fix applied")
