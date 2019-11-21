import os

whitelist = [ os.path.splitext(f)[0] for f in os.listdir('images/flathub') ]
