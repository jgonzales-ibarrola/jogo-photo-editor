# 01 — Quickstart (Windows)

## 1. Install (one time)

You need Python 3.10 or newer. Check by typing `python --version` in PowerShell.

Open PowerShell in this folder, then run:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e .
```

This creates a private Python environment in `.venv` and installs the tool and its libraries there.

Check it works:

```powershell
.venv\Scripts\python -m jogo presets
```

You should see a list of presets.

> **Tip:** to type `python -m jogo` instead of `.venv\Scripts\python -m jogo`, activate the environment first:
> `.venv\Scripts\Activate.ps1`. If PowerShell says scripts are disabled, run
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.
> The rest of the docs write `python -m jogo` and assume the environment is active.

### If Windows blocks it

If you see **"An Application Control policy has blocked this file"**, that is Windows Smart App Control checking new files.

- If it happens on first import, run the same command again. It often passes on the second try.
- Always use `python -m jogo`, not `jogo.exe`. The `.exe` launcher is unsigned and gets blocked.

## 2. Copy photos from your iPhone to the PC

**First, on the iPhone:** Settings → Apps → Photos (older iOS: Settings → Photos) → *Transfer to Mac or PC* → choose **Keep Originals**.
If you skip this, the iPhone converts your photos to lower-quality JPG during transfer.

Then pick one:

- **USB cable** (fastest for big ProRAW files): plug in, tap *Trust* on the iPhone, open File Explorer → *Apple iPhone* → *Internal Storage* → *DCIM*. Copy the files you want into `photos\in`.
- **iCloud for Windows** (Microsoft Store): photos sync to a folder on your PC. Copy from there.
- **Windows Photos app → Import**: also works over USB.

Windows may not show HEIC thumbnails. To see them, install *HEIF Image Extensions* from the Microsoft Store. The editor itself doesn't need it.

## 3. Your first edit

```powershell
python -m jogo edit
```

This edits everything in `photos\in` with the `natural` preset and saves to `photos\out`.
For each photo it prints what auto-fix changed and why, for example:

```
[1/3] IMG_0412.HEIC  (preset: natural)
    auto: Photo is dark -> exposure +0.45 EV.
    auto: 2.1% of the photo is near white -> highlights -0.41 to recover sky/detail.
    saved photos\out\IMG_0412_natural.jpg  (8064x6048, 49 MP, 19.8s)
```

## 4. Don't know which look you want? Try them all

```powershell
python -m jogo try photos\in\IMG_0412.HEIC
```

Open `photos\out\IMG_0412_compare.jpg`. It shows your photo in every preset. Pick the one you like:

```powershell
python -m jogo edit photos\in\IMG_0412.HEIC --preset vivid
```

## 5. Want it a bit different? Nudge one thing

```powershell
python -m jogo edit photos\in\IMG_0412.HEIC --preset vivid --exposure 0.3 --vibrance -0.1
```

Your numbers are added on top of auto-fix and the preset. What each option does: [03 Edits explained](03-edits-explained.md).

## 6. Make a version for Instagram / Facebook

```powershell
python -m jogo edit --crop 4:5 --resize 2048
```

Next: [02 Tool reference](02-tool-reference.md).
