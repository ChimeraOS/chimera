<!DOCTYPE html>
<html>
<head>
	<title>Steam Buddy</title>
	<meta name="viewport" content="width=device-width">
	<link href="/public/style.css" rel="stylesheet">
	<link href="/public/filepond.min.css" rel="stylesheet">
	<script src="/public/filepond.min.js"></script>
</head>
<body>
	<script>
	    function toggleMenu(id) {
			var target = document.getElementById(id);
			var elements = document.getElementsByClassName('menuitems');
			for (const element of elements) {
				if (element !== target) {
					element.style.display = "none";
				}
			}
			if (target.style.display == "block") {
				target.style.display = "none";
			} else {
				target.style.display = "block";
			}
		}
	</script>
	<div class="header">
		<a href="/">Home</a>
		% if get('platform') :
			<em>/</em> <a href="/platforms/{{platform}}">{{platformName}}</a>

			% if get('app') and get('name') :
				<em>/</em> <a href="/platforms/{{platform}}/edit/{{name}}">{{app.name}}</a>
			% elif get('name') :
				<em>/</em> <a href="/platforms/{{platform}}/edit/{{name}}">{{name}}</a>
			% elif get('isNew') :
				<em>/</em> <a href="/platforms/{{platform}}/new">New</a>
			% end
		% end
		<div class="right">
			% if get('audio'):
				<div class="menuitems" id="audiomenu">
					<a href="/audio/volume_up">Volume Up</a>
					% if get('audio')['muted']:
						<a style="color : lightgreen" href="/audio/toggle_mute">{{get('audio')['volume']}}</a>
					% else:
						<a style="color : crimson; text-decoration : line-through" href="/audio/toggle_mute">{{get('audio')['volume']}}</a>
					% end
					<a href="/audio/volume_down">Volume Down</a>
					% for output in get('audio')['options']:
						% if get('audio')['active'] == output[0]:
							<a style="text-decoration : underline" href="/audio/{{output[0]}}">{{output[1]}}</a>
						% else:
							<a href="/audio/{{output[0]}}">{{output[1]}}</a>
						% end
					% end
				</div>
				<a href="javascript:void(0);" id="audiomenuicon" onclick="toggleMenu('audiomenu')">&#9835;</a>
			% end
            <div class="menuitems" id="mainmenu">
                <a href="/settings">Settings</a>
                <a href="/exit_game">Exit Game</a>
                <a href="/steam/restart">Restart Steam</a>
                <a href="/retroarch/load_state">Save Emulator State</a>
                <a href="/retroarch/save_state">Load Emulator State</a>
                <a href="/steam/compositor">Toggle Compositor</a>
                <a href="/steam/overlay">Toggle Steam Overlay</a>
                <a href="/mangohud">Toggle MangoHud</a>
                <a href="/virtual_keyboard">Virtual Keyboard</a>
                <a href="/logout">Log Out</a>
            </div>
            <a href="javascript:void(0);" id="mainmenuicon" onclick="toggleMenu('mainmenu')">&#9881;</a>
		</div>
	</div>
	<div class="content">
		{{!base}}
	</div>
</body>
</html>
