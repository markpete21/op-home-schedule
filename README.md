# Orangeville Prep — Home Game Schedule feed

`games.json` is the public data feed for the home schedule widget on the Orangeville Prep website.
It is refreshed daily from the "Home Games" sheet of the program's schedule workbook.
Only public fields are published: date, time, home team, opponent, theme, description and ticket/stream links.

- `sync_schedule.py` — builds `games.json` from a workbook export
- `descriptions.json` — fallback theme-night blurbs, used when the sheet's description is blank
