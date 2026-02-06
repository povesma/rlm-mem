# Review Screenshot

Review and analyze screenshots in context of current implementation.

## Process

1. **Find latest screenshot**:
   ```bash
   ls -t screenshots/*.png | head -n 1
   ```

2. **Read screenshot** with Read tool

3. **Compare with code** (optional):
   - Use RLM to find related UI files
   - Compare screenshot UI with code implementation
   - Check for consistency

4. **Provide feedback**:
   - UI/UX observations
   - Bugs or issues
   - Suggestions for improvement

## Notes

- Screenshots are typically in `screenshots/` directory
- Use for UI verification during development
