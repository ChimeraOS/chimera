<!DOCTYPE html>
<html lang="en">
<head>
	<title>Chimera</title>
	<meta charset="utf-8"/>
	<meta name="viewport" content="width=device-width, initial-scale=1">
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
		<div class="left">
            <div class="menuitems" id="mainmenu">
                <a href="/library">Library</a>
                <a href="/actions">Actions</a>
                <a href="/virtual_keyboard">Virtual Keyboard</a>
                <a href="/system">System</a>
                <a href="/logout">Log Out</a>
            </div>
            <a href="javascript:void(0);" id="mainmenuicon" onclick="toggleMenu('mainmenu')">&#9776;</a>
		</div>
	</div>
	% if get('bare'):
		{{!base}}
	% else:
		<div class="content">
			{{!base}}
		</div>
	% end

	<link href="https://cdn.jsdelivr.net/npm/remixicon@2.5.0/fonts/remixicon.css" rel="stylesheet">
	<!-- https://remixicon.com/ -->
</body>
</html>
