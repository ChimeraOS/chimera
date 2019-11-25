install:
	install -d -m755 $(DESTDIR)/etc/systemd/system
	install -d -m755 $(DESTDIR)/usr/bin
	install -d -m755 $(DESTDIR)/usr/share/steam-buddy/config
	install -d -m755 $(DESTDIR)/usr/share/steam-buddy/flathub
	install -d -m755 $(DESTDIR)/usr/share/steam-buddy/images
	install -d -m755 $(DESTDIR)/usr/share/steam-buddy/images/flathub
	install -d -m755 $(DESTDIR)/usr/share/steam-buddy/views
	install -D -m 755 bin/*                $(DESTDIR)/usr/bin/
	install -D -m 644 config/*.cfg         $(DESTDIR)/usr/share/steam-buddy/config/
	install -D -m 644 flathub/*.py         $(DESTDIR)/usr/share/steam-buddy/flathub/
	install -D -m 644 images/*.png         $(DESTDIR)/usr/share/steam-buddy/images/
	install -D -m 644 images/flathub/*.png $(DESTDIR)/usr/share/steam-buddy/images/flathub/
	install -D -m 755 launcher             $(DESTDIR)/usr/share/steam-buddy
	install -D -m 755 steam-buddy          $(DESTDIR)/usr/share/steam-buddy
	install -D -m 644 *.service            $(DESTDIR)/etc/systemd/system/
	install -D -m 644 *.socket             $(DESTDIR)/etc/systemd/system/
	install -D -m 644 views/*.tpl          $(DESTDIR)/usr/share/steam-buddy/views/

.PHONY: install
