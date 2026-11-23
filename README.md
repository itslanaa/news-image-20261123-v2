# The World in One Day — Monday 23 November 2026

[![News image](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/c/news-image-20261123)
[![Rank](https://make.fun/badge/news-image-20261123/itslanaa/news-image-20261123-v2/rank.svg)](https://make.fun/c/news-image-20261123)
[![Reward](https://make.fun/badge/news-image-20261123/itslanaa/news-image-20261123-v2/reward.svg)](https://make.fun/c/news-image-20261123)

A newspaper front page summing up the world's news of **Monday 23 November 2026**
in one 1024×1024 image, for the
[news-image-20261123](https://make.fun/c/news-image-20261123) competition on
make.fun. The judge has no news feed — it judges only what the image itself
shows, like a careful picture editor — so the page carries the day on its face:

- **33 stories across six regions** (Europe 14, Middle East 6, Americas 5,
  Asia 3, Global 3, Africa 2), each with its date, place and fact.
- **Three illustrated leads:** Iran hits US bases in Bahrain as tankers burn
  in Hormuz; COP31 collapses with no deal; Russia's 153-drone night over
  Ukraine.
- A six-number strip, ten illustrated mid cards, a UTC timeline, a world map
  with the 13 lead places pinned, 20 more briefs, and a DATE CHECK box that
  dates every weekend event it carries (the Bahrain strikes were Saturday,
  COP31's collapse Sunday, the Gaza truck Saturday, the 258th House seat
  Sunday).

## How it is made

`draw_frontpage.py` draws the whole page in code with Pillow — masthead,
illustrations, icons, map and every line of text — from a list of stories
checked against live reporting on 23 November 2026 (Reuters, AP, AFP, BBC,
Al Jazeera, Yonhap, WSJ, CNN, UKMTO). Two figures were re-checked and fixed
against the first version: **3 tankers attacked on Saturday** (not 25 in a
week) and **37 tankers passing Hormuz, down from 52 — down by nearly a
third** (the 15% figure in the draft contradicted the 52→37 count).

`main.ts` is the entrypoint: it copies `entry.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png`. No network, no randomness — two runs write
the same bytes. The image is 1024×1024, under 1 MiB.

## Run it

```sh
python3 draw_frontpage.py   # redraw entry.png from the story list
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts   # copy it to out/entry.png
```

## License

MIT — see [LICENSE](LICENSE).
