% rebase('base.tpl')

<h2>{{app['name']}}</h2>
<p><img src="https://flathub.org/{{app['iconDesktopUrl']}}" alt="{{ app['name'] }}" title="{{ app['name'] }}"></img></p>
{{app['description']}}
<p>
% if isInstalled:
<a href="/flatpak/uninstall/{{flatpak_id}}">Uninstall</a>
% else:
<a href="/flatpak/install/{{flatpak_id}}">Install</a>
% end
</p>