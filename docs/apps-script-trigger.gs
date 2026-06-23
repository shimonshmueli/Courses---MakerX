/**
 * Maker-X schedule auto-deploy trigger.
 *
 * Lives inside the Google Sheet's Apps Script project (Extensions > Apps Script).
 * Fires a GitHub "repository_dispatch" event every time the sheet changes,
 * which kicks off .github/workflows/render-schedule.yml — that workflow
 * renders the Quarto site from the latest sheet data and pushes the result,
 * which Vercel then deploys automatically.
 *
 * SETUP (one-time, done by a human in the Apps Script editor — not by Claude):
 *
 * 1. Open the schedule Google Sheet > Extensions > Apps Script.
 * 2. Paste this whole file into Code.gs (replacing the default content).
 * 3. Project Settings (gear icon) > Script Properties > Add property:
 *      key:   GITHUB_TOKEN
 *      value: <a GitHub fine-grained PAT scoped to this repo, with
 *              "Contents: write" and "Actions: write" permissions>
 *    This keeps the token out of the script body, so it's never visible
 *    to anyone you share the sheet with.
 * 4. Triggers (clock icon, left sidebar) > Add Trigger:
 *      Function:          onScheduleEdit
 *      Event source:      From spreadsheet
 *      Event type:        On edit
 *    Save — Google will ask you to authorize the script once.
 * 5. Test: edit any cell in the sheet, then check the repo's Actions tab
 *    on GitHub to confirm a "Render Schedule from Google Sheet" run started.
 */

const GITHUB_OWNER = "shimonshmueli";
const GITHUB_REPO  = "Courses---MakerX";

function onScheduleEdit(e) {
  const token = PropertiesService.getScriptProperties().getProperty("GITHUB_TOKEN");
  if (!token) {
    Logger.log("GITHUB_TOKEN script property is not set — see setup steps in the file header.");
    return;
  }

  const url = "https://api.github.com/repos/" + GITHUB_OWNER + "/" + GITHUB_REPO + "/dispatches";
  const options = {
    method: "post",
    contentType: "application/json",
    headers: {
      "Authorization": "Bearer " + token,
      "Accept": "application/vnd.github+json"
    },
    payload: JSON.stringify({ event_type: "sheet-updated" }),
    muteHttpExceptions: true
  };

  const response = UrlFetchApp.fetch(url, options);
  Logger.log("GitHub dispatch response: " + response.getResponseCode() + " " + response.getContentText());
}
