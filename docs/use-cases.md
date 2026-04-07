# Use Cases

## UC1: Manager views branch health overview

**Actor:** Restaurant area manager  
**Trigger:** Manager opens the AI Manager Co-Pilot tab

**Flow:**
1. The app computes aggregate metrics for every branch in the dataset.
2. The Branch Health Overview table is displayed with columns: Branch, City, Avg Rating, Total Reviews, Status, Trend.
3. Status is colour-coded: 🔴 Needs Attention (avg < 2.5), 🟡 Monitor (2.5–3.5), 🟢 Healthy (> 3.5).
4. Trend compares the last 30 days vs the previous 30-day window: ⬆️ improving, ⬇️ declining, ➡️ stable (±0.1 threshold).
5. The manager scans for red or declining branches to prioritise follow-up.

**Outcome:** Manager has a single-screen view of every branch's rating health without manual data aggregation.

---

## UC2: Manager generates AI insights for a specific branch

**Actor:** Restaurant area manager  
**Trigger:** Manager clicks a branch row in the health table or selects a branch from the sidebar dropdown, then clicks **Generate Insights**

**Flow:**
1. Clicking a row in the health table pre-selects that branch in the Co-Pilot sidebar.
2. The manager adjusts the time range slider (30–365 days) as needed.
3. The manager clicks **Generate Insights**.
4. The app filters reviews for that branch and time window, takes the 20 most recent, and sends them to Claude with the manager co-pilot system prompt.
5. Claude returns a structured response with three sections: `SUMMARY`, `ACTION ITEMS`, and `STAFF BRIEFING`.
6. The app renders these as styled cards: Summary and Action Items side by side, Staff Briefing below.
7. Each Action Item shows the problem, a supporting quote from a review, and a concrete directive.

**Outcome:** Manager receives actionable, evidence-backed recommendations within seconds, without reading individual reviews.

---

## UC3: Manager downloads staff briefing memo

**Actor:** Restaurant area manager  
**Trigger:** Manager has generated insights (UC2) and clicks **Download Staff Briefing (.txt)**

**Flow:**
1. After insights are generated, a download button appears below the insight cards.
2. The manager clicks the button.
3. The browser downloads a `.txt` file named `briefing_{branch}_{date}.txt`.
4. The file contains the Staff Briefing section as clean plain text, with markdown symbols stripped.
5. The manager can share or print the file for a team briefing.

**Outcome:** Manager has a ready-to-share staff memo generated directly from customer feedback data.
