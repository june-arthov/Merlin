# Self-Evolution Protocol

When this skill is activated, you are authorized to analyze and modify your own source code to improve performance, fix bugs, or add new capabilities.

## Methodology
1. **Self-Audit**: Use `grep_search` and `read_file` on the `merlin/` directory to understand your own architecture.
2. **Identification**: Find bottlenecks, redundant code, or missing features.
3. **Planning**: Use the `plan` tool to document the intended upgrade.
4. **Implementation**: Use `replace` or `write_file` to apply changes to your own modules.
5. **Validation**: Run the internal test suite to ensure the upgrade didn't break your core functionality.

## Mandate
- Always back up a module before modifying it.
- Ensure the `MerlinEngine` remains stable.
- If an upgrade fails, revert immediately.
