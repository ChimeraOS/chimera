% rebase('base.tpl')
% from urllib.parse import quote

<h2>{{app.name}}</h2>

% if app.operation:
	<script type="text/JavaScript">
		async function reloadWhenDone() {
			url = "/{{ platform }}/progress/" + "{{ quote(app.content_id) }}";
			let result;
			try {
				response = await fetch(url);
				result = await response.json();
			} catch(e) {
				result = {};
			}
			if (!result.operation) {
				location.reload(true);
			} else {
				if (result.progress != -1) {
					document.getElementById('progress').innerHTML = result.progress + "%";
				}
				setTimeout(reloadWhenDone, 1000);
			}
		}
		reloadWhenDone();
	</script>
	<h3>
		{{app.operation}}... <div id="progress"></div>
	</h3>
% elif app.installed_version:
	<h3>Version: {{app.installed_version}}</h3>
% end

% if app.get('status'):
	<div class="status-badge" onclick="window.open('/status-info')">
		{{ app.get('status_icon') }} {{ app.get('status').capitalize() }}
	</div>
% end

<div class="left-content">
	% if app.get('notes'):
		<ul class="notes">
			% for note in app.notes:
				<li>{{ note }}</li>
			% end
		</ul>
	% end
</div>

<div class="img-container">
	<img src="{{app.image_url}}" alt="{{ app.name }}" title="{{ app.name }}">
</div>

<p>{{app.summary}}</p>

% if not app.operation:
	% if app.installed:
		% if app.available_version != None and app.installed_version != app.available_version:
			<form action="/{{platform}}/update/{{ quote(app.content_id) }}">
				<button class="add">Update to version {{app.available_version}}</button>
			</form>
		% end
		% if steamShortcutID:
		<form action="/launch/{{steamShortcutID}}">
			<button>Launch</button>
		</form>
		% end
		% if not remote:
		<form action="/{{platform}}/uninstall/{{ quote(app.content_id) }}">
			<button class="delete">Uninstall</button>
		</form>
		% end
	% else:
		<form action="/{{ platform }}/install/{{ quote(app.content_id) }}">
			<button class="add">Install</button>
		</form>
	% end
% end
