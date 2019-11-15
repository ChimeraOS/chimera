% rebase('base.tpl')

<h2>{{app}}</h2>
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
<form action="/shortcuts/delete" method="post">
	<input type="hidden" value="{{platform}}" name="platform">
	<input type="hidden" value="{{app.flatpak_id}}" name="name">
	<button class="delete">Uninstall</button>
</form>
% else:
<form action="/shortcuts/new" method="post">
	<input type="hidden" value="{{platform}}" name="platform">
	<input type="hidden" value="{{app.flatpak_id}}" name="name">
	<input type="hidden" value="off" name="hidden">
	<button class="add">Install</button>
</form>
% end
% end
</p>