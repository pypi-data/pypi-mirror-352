#!/bin/sh
echo "installation de climax..."
echo ""
installation_path="$HOME/.climax"
destination_archive="$installation_path/climax.tar.gz"
mkdir -p $installation_path
curl -o $destination_archive  https://acme.tld/climax-linux-x86.tar.gz
tar -xzf $destination_archive --directory=$installation_path
rm $destination_archive
chmod 750 "$installation_path/climax"
grep -qF ".climax/env" ~/.zprofile || echo 'source "$HOME/.climax/env"' >> ~/.zprofile
grep -qF ".climax/env" ~/.profile || echo '. "$HOME/.climax/env"' >> ~/.profile
echo ""
echo "Installation ok."
echo ""
echo "Pour tester votre installation:"
echo "    - relancez votre shell"
echo "    - lancez climax --help"
echo ""
