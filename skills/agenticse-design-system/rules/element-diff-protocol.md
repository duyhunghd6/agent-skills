# Element-Level Diff Protocol

**MANDATORY FOR ALL VISUAL CHANGES:** Every time a 2D HTML/CSS element or token is modified in Workflow 3, you MUST create an element diff to show a side-by-side comparison.

## The 7-Step Process

1. **Extract `before.html`**
   - BEFORE making the change, locate the element in the screen's `index.html`.
   - Copy the HTML snippet into `screens/<screen-name>/history/vXXX_<slug>/before.html`.

2. **Make the Change**
   - Perform the required HTML/CSS edit directly in `screens/<screen-name>/index.html`.

3. **Extract `after.html`**
   - Copy the modified HTML snippet into `screens/<screen-name>/history/vXXX_<slug>/after.html`.

4. **Create `diff.html`**
   - Create an HTML file that renders BOTH snippets side-by-side or top-and-bottom.
   - Visually highlight the specific CSS or content properties that changed.

5. **Log `meta.json`**
   - In the same `history/vXXX_<slug>` folder, create `meta.json`:

   ```json
   {
     "id": "CHG-XXX",
     "screen": "screen-name",
     "element": "element-selector",
     "property": "changed-property",
     "before_value": "old-value",
     "after_value": "new-value",
     "token_ref": "token.name",
     "reason": "Why the change was made",
     "status": "PENDING"
   }
   ```

6. **Register the Change**
   - Append to `screens/<screen-name>/versions.json`.
   - Append to global `changes/changelog.json`.

7. **Link in Iteration Notes**
   - Provide direct markdown links to the `diff.html` file in the notes explicitly for human review/approval.
