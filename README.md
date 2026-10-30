# jogo-photo-editor

A free, open-source photo editor for iPhone photos. It runs on your own computer.
You give it HEIC, ProRAW (DNG) or JPG files. It fixes them automatically and saves edited copies.
Your originals are never changed and your photos never leave your machine.

Made for iPhone Pro 48MP photos and for beginners: you don't need to know editing to use it.
Each automatic fix is explained in plain words, so you learn while you use it.

## What it does

- **Auto-fix**: brightens dark photos, recovers bright skies, lifts dark shadows, removes color casts.
- **Presets**: ready-made looks (18 looks, incl. iPhone-style `amber`, `gold`, `rose-gold`, `bright`; e.g. `natural`, `beach`, `airy`, `tropical`, `cinematic`, `bw`) including color grading.
- **Try all looks at once**: one image that shows your photo in every preset, so you can pick.
- **Photo check-up**: shows the camera settings used and what is wrong or right with the photo.
- **Full 48MP output**, or resized for social media. Crops to `4:5`, `1:1`, `16:9` and more.
- **Removes GPS location** from saved copies by default, so posting online doesn't reveal where you live.

## 30-second start

```powershell
# one time: install (see docs/01-quickstart.md for details)
python -m venv .venv
.venv\Scripts\python -m pip install -e .

# every time: put photos in photos\in, then
.venv\Scripts\python -m jogo edit
```

Edited photos appear in `photos\out`.

## Documentation

| Read this | When |
|---|---|
| [01 Quickstart](docs/01-quickstart.md) | First time. Install, copy photos from iPhone, first edit. |
| [02 Tool reference](docs/02-tool-reference.md) | Every command, option, preference and preset. |
| [03 Edits explained](docs/03-edits-explained.md) | What exposure, contrast, highlights, etc. actually do. |
| [04 iPhone camera settings](docs/04-iphone-settings.md) | HEIF vs ProRAW, 48MP, exposure, which settings to turn on. |
| [05 Shooting guide (Philippines)](docs/05-shooting-guide-philippines.md) | Composition and taking better photos where you live. |
| [06 Composition and crop](docs/06-composition-and-crop.md) | Grid lines, composition techniques, how to decide a crop. |
| [07 Posting guide](docs/07-posting-guide.md) | Our edit-to-post workflow, carousel order, captions, timing. |
| [My style](docs/my-style.md) | Your editing taste and past decisions. Grows with every edit. |
| [Roadmap](ROADMAP.md) | What gets added next, and your learning path. |

## Using it with Claude Code

Open this folder in Claude Code and ask in plain words, for example:
"Edit the photos in photos/in with the beach preset and make 4:5 versions for Instagram."
The instructions Claude follows are in [CLAUDE.md](CLAUDE.md).

## Honest limits (v0.1)

- One full 48MP photo takes about 20 seconds and needs about 3 GB of free RAM. Use `--preview` for a fast 2048px check.
- ProRAW (DNG) files are decoded with LibRaw, not Apple's own engine. They can look flatter than in the iPhone Photos app before editing. Auto-fix corrects most of this.
- Auto white balance only corrects color casts it is confident about. It deliberately ignores blue sky and green leaves.
- No local edits yet (e.g. "brighten only the face"). See the [Roadmap](ROADMAP.md).

## License

MIT. Free to use, change and share.
