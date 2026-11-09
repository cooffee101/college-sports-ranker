# CFB Top 25 Ranker

Drag-and-drop top 25 builder for all 138 FBS teams, with records and game-by-game results.

- `site/index.html` is the home screen (College Football on the left, College Basketball coming soon on the right)
- `site/cbb.html` is the men's basketball ranker (364 Division I teams, 32 conferences, records and schedules)
- `site/cfb.html` is the football ranker (plain HTML/CSS/JS, no build step), including the 12-team playoff view
- `site/records.json` holds records and game lists and is rewritten automatically
- `scripts/build_records.py` rebuilds `records.json` from the open-source cfbfastR schedule data
- `.github/workflows/update-records.yml` runs the scripts every day at 10:00 UTC, commits any change, and redeploys the site

## One-time setup
1. Create a new GitHub repository (for example `cfb-ranker`) and upload everything in this folder, including the hidden `.github` folder.
2. Repo **Settings > Pages > Build and deployment > Source: GitHub Actions**.
3. Repo **Settings > Actions > General > Workflow permissions: Read and write permissions**, then Save.
4. Open the **Actions** tab, choose **Update records and deploy**, click **Run workflow**.
5. When it finishes, your site is at `https://YOUR-USERNAME.github.io/cfb-ranker/`.

## Updating
Nothing to do. The workflow refreshes records daily. To update right now, run it by hand from the Actions tab. Records are only as current as the cfbfastR data, which can lag a few hours after games end.

## Notes
- Your ranking, logos and typed-in record edits are saved in your browser for that web address. A new address starts empty, so use **Backup** on the old site and **Restore** on the new one to carry them over.
- Use a different season with the `SEASON` environment variable (the script otherwise picks the season from today's date).

## Basketball
- `scripts/build_cbb.py` writes `site/cbb-data.json` (teams, conferences, team colors, records, game lists) daily, so records stay current during the season.
- Logos for basketball go in `site/cbb-logos/` (same naming rules as football). Teams without a logo show a jersey in their colors.
