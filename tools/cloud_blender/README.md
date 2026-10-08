# Cloud Blender (phone-friendly experiment)

This is an independent prototype pipeline: GitHub's Ubuntu runner downloads official Blender 4.5 LTS, runs a Python modeling script, and uploads generated 3D files to the **Actions** run page. No laptop or running Blender MCP server is needed.

## First test

1. Open the repository in GitHub on your phone.
2. Open **Actions** → **Cloud Blender — Procedural Creature**.
3. Select the most recent green run (branch: `blender-cloud-test`).
4. At the bottom of that run, download the **cloud-blender-runner-prototype** artifact.
5. Unzip it in the Files app. It contains:
   - `runner_prototype.glb` — real 3D mesh with materials, useful for browser-game or Unreal import.
   - `runner_prototype.blend` — editable Blender scene.
   - `runner_prototype_preview.png` — static preview (only if rendering succeeds).
   - `runner_prototype_info.json` — export metadata.

## Editing the model from a phone

Change `tools/cloud_blender/create_test_creature.py` on this branch through GitHub's web editor, or have an AI coding agent change it. Every push affecting the test script/workflow launches a new cloud build. Do not upload or execute untrusted code.

This first model is a **stylized, four-eyed amphibious runner test only**. It is not meant to replace or overwrite the canonical Worldvein assets, species anatomy, or running games. You can take a generated `.glb` and import it separately once you approve it.

## Technical details

- Workflow file: `.github/workflows/blender-cloud.yml`
- Modeling script: `tools/cloud_blender/create_test_creature.py`
- Blender build: 4.5.14 LTS (official Linux x64 binary).
- Output is a GitHub Actions artifact, *not a commit to the main branch*.
- Files produced in a GitHub runner are temporary. Download them from **Artifacts** after each run; artifact retention is seven days here.
- A successful cloud build demonstrates headless modeling. It does **not** establish live Blender MCP control from a mobile ChatGPT conversation.

This test pipeline intentionally runs on a feature branch. To add the permanent **Run workflow** button under the default branch's Actions tab, review and merge the pull request before using manual workflow dispatch.
