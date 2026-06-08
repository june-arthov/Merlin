# Systematic Debugging Protocol

When this skill is activated, you must follow the 4-Phase Debugging Protocol:

## Phase 1: Understand
- Map the relevant code and data flow.
- Identify the expected vs. actual behavior.
- Read logs and error messages thoroughly.

## Phase 2: Reproduce
- Create a minimal reproduction script or test case.
- Confirm the bug exists in a controlled environment.
- Do NOT skip this phase; empirical evidence is mandatory.

## Phase 3: Surgical Fix
- Identify the root cause.
- Apply the minimal necessary change using the `replace` tool.
- Avoid side effects.

## Phase 4: Verify
- Run the reproduction script to confirm the fix.
- Run the full test suite to ensure no regressions.
- Update `MERLIN.md` if the bug revealed a new architectural constraint.

## Mandate
Never apply a fix until you have successfully reproduced the failure.
Efficiency comes from precision, not speed.
