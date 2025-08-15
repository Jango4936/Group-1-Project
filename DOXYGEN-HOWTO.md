
# Generate API Docs with Doxygen (Python/Django)

1. Install tools (from your project root):
   ```bash
   pip install doxypypy
   # optional but nice: pip install breathe
   ```

2. Use the provided config (this file assumes project layout as in your repo):
   ```bash
   doxygen Doxyfile-python
   ```

   The HTML will be in `docs/doxygen/html/index.html`.

3. Write comments that Doxygen will pick up:

   - Put **triple-quoted docstrings** right under each `class` or `def`.
   - Use Doxygen tags inside the docstring:
     - `@brief` one-liner summary
     - `@param <name> <type>`
     - `@return <type or description>`
     - `@exception <ExceptionType> description`
     - `@note`, `@warning`, `@see`

4. Common gotchas (why comments don't show):
   - `INPUT` didn't point to your `booking/` folder. (Fixed in `Doxyfile-python`.)
   - `FILE_PATTERNS` didn't include `*.py`. (Fixed.)
   - Docstrings weren't converted for Doxygen. Use **doxypypy** (`FILTER_PATTERNS` is set).
   - You forgot to run `doxygen` from the repo root.

5. Next steps:
   - Copy the snippets from `doxygen_comment_examples.md` into your code.
   - Regenerate: `doxygen Doxyfile-python`
   - Commit `docs/doxygen` to GitHub and enable GitHub Pages (root: `/docs`).
