% rebase('base.tpl')
<script>
async function getDescription() {
    url = '/flathub/description/{{app.flatpak_id}}';
    response = await fetch(url);
    values = await response.json();
    if (values) {
        document.getElementById('description').innerHTML = values.description;
    }
}
getDescription();
</script>
<h2>{{app}}</h2>
% if app.busy:
<script type="text/JavaScript">
async function reloadWhenDone() {
	url = "/flathub/progress/" + "{{app.flatpak_id}}";
	response = await fetch(url);
	values = await response.json();
	if (!values.busy) {
	    location.reload(true);
	} else {
	    if (values.progress != -1) {
	        document.getElementById('progress').innerHTML = values.progress + "%";
	    }
	    setTimeout(reloadWhenDone, 100);
	}
}
reloadWhenDone();
</script>
<h3>
% if app.installed:
Uninstalling... <div id="progress"></div>
% else:
Installing.. <div id="progress"></div>
% end
</h3>
% else:
% if app.version:
<h3>Version: {{app.version}}</h3>
% end
% end
<p ><img class="flathub-edit" src="{{app.image_url}}" alt="{{ app.name }}" title="{{ app }}"></p>
<p>{{app.summary}}<p>
<p id="description"></p>

% if app.busy == False:
% if app.installed:
% if app.version != app.available_version:
<form action="/flathub/update/{{app.flatpak_id}}">
	<button class="add">Update to version {{app.available_version}}</button>
</form>
% end
% if not app.version:
<form action="/flathub/update/{{app.flatpak_id}}">
	<button class="add">Check for updates</button>
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
