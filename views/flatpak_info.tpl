% rebase('base.tpl')

<h2>{{app['name']}}</h2>
<p><img src="https://flathub.org/{{app['iconDesktopUrl']}}" alt="{{ app['name'] }}" title="{{ app['name'] }}"></img></p>
{{!app['description']}}

% if isInstalled:
<p><a href="/flatpak/uninstall/{{flatpak_id}}">Uninstall</a></p>
<p><a href="/flatpak">Back</a></p>
% else:
<p><a href="/flatpak/install/{{flatpak_id}}">Install</a></p>
<p><a href="/flatpak/available">Back</a></p>
% end
</p>