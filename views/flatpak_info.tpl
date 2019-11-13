% rebase('base.tpl')

<h2>{{app}}</h2>
% if app.busy:
<h3>
% if app.installed:
Uninstalling...
% else:
Installing..
% end
% if app.progress != -1:
{{app.progress}}&#37;
% end
</h3>
% end
<p><img src="{{app.image_url}}" alt="{{ app.name }}" title="{{ app }}"></img></p>
{{!app.get_description()}}


% if app.installed:
% if app.busy == False:
<p><a href="/flatpak/uninstall/{{app.flatpak_id}}">Uninstall</a></p>
% end
<p><a href="/flatpak">Back</a></p>
% else:
% if app.busy == False:
<p><a href="/flatpak/install/{{app.flatpak_id}}">Install</a></p>
% end
<p><a href="/flatpak/available">Back</a></p>
% end
</p>