# MedRen - The Media Renamer

A GUI tool for renaming media files based on their metadata.

## Features

- Rename files based on their creation date
- Support for both single files and directories
- Configurable filename templates
- Multiple metadata backends (EXIF, Hachoir, MediaInfo, ffmpeg)
- Drag and drop support
- Profile management
- Preview before renaming
- Copy filenames to clipboard

## Installation

```bash
pip install medren
```

## Usage

Run the GUI:
```bash
medren
```

Or with command line arguments:
```bash
medren path/to/directory --prefix "IMG_" --template "{prefix}{datetime}{suffix}{ext}"
```

Install backends prerequisites on Windows
```commandline
choco install exiftool
choco install mediainfo
choco install ffmpeg
```

### Command Line Arguments

- `inputs`: Input paths (dirs, filenames or pattern)
- `--prefix, -p`: Initial prefix value
- `--suffix, -s`: Initial suffix value
- `--profile, -P`: Profile name
- `--template, -t`: Initial template value
- `--datetime-format, -f`: Initial datetime format value

## License

MIT License
