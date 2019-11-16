% rebase('base.tpl')

<h2>{{app}}</h2>
<h3>Version: {{app.version}}</h3>
% if app.busy:
<script type="text/JavaScript">
    window.setTimeout("location.reload(true);", 5000)
</script>
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
<p ><img class="flathub-edit" src="{{app.image_url}}" alt="{{ app.name }}" title="{{ app }}"></img></p>
{{!app.get_description()}}

% if app.busy == False:
% if app.installed:
% if app.version != app.available_version:
<form action="/flathub/update/{{app.flatpak_id}}">
	<button class="add">Update to version {{app.available_version}}</button>
</form>
% end
<form action="/flathub/uninstall/{{app.flatpak_id}}">
	<button class="delete">Uninstall</button>
</form>
% else:
<form action="/flathub/install/{{app.flatpak_id}}">
	<button class="add">Install</button>
</form>
% end
% end
</p>