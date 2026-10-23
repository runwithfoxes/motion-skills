#!/bin/sh
# Fetch the handwriting font beside the page. Reenie Beanie, by James Grieshaber, SIL Open Font Licence, from Google Fonts.
set -e
cd "$(dirname "$0")"
curl -fsSL -o ReenieBeanie.ttf https://github.com/google/fonts/raw/main/ofl/reeniebeanie/ReenieBeanie.ttf
echo "ReenieBeanie.ttf"
