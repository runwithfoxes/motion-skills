#!/bin/sh
# Copy the two fonts the example uses in beside the page. Both are under the SIL Open Font Licence.
set -e
cd "$(dirname "$0")"
npm i --no-save --ignore-scripts @fontsource/space-grotesk@5.2.10 @fontsource/jetbrains-mono@5.2.8
cp node_modules/@fontsource/space-grotesk/files/space-grotesk-latin-500-normal.woff2 .
cp node_modules/@fontsource/jetbrains-mono/files/jetbrains-mono-latin-400-normal.woff2 .
cp node_modules/@fontsource/jetbrains-mono/files/jetbrains-mono-latin-500-normal.woff2 .
echo "fonts copied"
