# Flight Path History

`index.html` — a self-contained animation of every flight in the travel sheet.
One file, no network, no build step to *view* it. Just open it.

## Rebuilding after the sheet changes

```
python3 build.py "/Users/jzair/Downloads/Jeff Air Travel Track - Main Sheet.csv"
```

Options:
- `--external` — link `logos/*.png` instead of inlining them (index.html drops to ~40 KB,
  but the `logos/` folder must travel with it).

## New airline in the sheet?

```
python3 fetch_logos.py        # downloads any missing logo into logos/
python3 build.py              # re-embeds them
```

A flight whose airline has no logo file falls back to a coloured two-letter chip,
so nothing ever renders broken.

## Files

| file | what it is |
|---|---|
| `index.html` | the generated animation (the only file you need to view/share) |
| `template.html` | page markup, CSS and JS; `/*__AP__*/ /*__AL__*/ /*__LG__*/` are the data slots |
| `build.py` | CSV → index.html |
| `airports.py` | lon/lat for every airport code, plus code aliases (`XIA`→`XIY`) |
| `fetch_logos.py` | logo downloader/shrinker (cached in `logos/`) |

## Data notes

- Rows missing a date, origin, destination or flight number are skipped (3 planned 2026 rows).
- Blank `Miles` are filled with the great-circle distance and marked `est.` on the card (6 rows).
- Airline names come from the flight-number prefix, not the `Airlines` column, which has a few
  typos (`NH805` was logged as Emirates, `ZH8011` as Jixiang). Edit `NAME` in `build.py` to change one.
- `XW` (NokScoot) has no reliable logo and uses the lettermark chip.

## Controls

space = play/pause · ← → = previous/next flight · drag the timeline to scrub · `1×` cycles speed.
