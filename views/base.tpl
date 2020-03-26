<html>
<head>
	<title>Steam Buddy</title>
	<meta name="viewport" content="width=device-width">
	<style>

		a:link {
		  text-decoration: none;
		  color : white;
		}

		a:visited {
		  text-decoration: none;
		  color : white;
		}

		a:hover {
			text-decoration: none;
			color : #bbbbbb;
		}

		a:active {
			text-decoration: none;
		}

		p.placeholder {
			color : #666666;
			font-size : 22px;
		}

		#progress {
		    display : inline;
		}

        .flathub {
            width : 100%;
            height : 100%;
            text-align : center;
            border-width : 4px;
            border-style : solid;
            border-image : linear-gradient(to bottom, #888888, #666666) 1 1;
        }

		.flathub h3 {
		    color : #000000;
            position : relative;
		}

		img.flathub-edit {
		    width : initial;
		    height : initial;
		    border-style : hidden;
		    border-width : 0px;
		    background-color : transparent;
		}

		.hidden {
			opacity : 0.4
		}

		.new-shortcut {
			width : 460px;
			height : 215px;
			color : white;
			background-color : #3268a8;
		}

		img {
			margin : 10px;
			width : 90%;
			height : auto;
			max-width : 460px;
			max-height : 215px;
			border-width : 4px;
			border-style : solid;
			border-image : linear-gradient(to bottom, #888888, #666666) 1 1;
			background-color : black;
		}

		img.selected {
			border-image : none;
			border-color : #0075ff;
			border-width : 12px;
		}

		.missing > img {
			width : 100%;
			opacity : 0;
			background-color : gray;
		}

		.missing {
			position : relative;
			display : inline-block;
			margin : 10px;
			overflow : hidden;
			padding : 0px;
			width : 90%;
			height : auto;
			max-width : 460px;
			max-height : 215px;
			background-color : #333333;
			border-width : 4px;
			border-style : solid;
			border-image : linear-gradient(to bottom, #888888, #666666) 1 1;
		}

		.missing-text {
			position : absolute;
			top : 50%;
			left : 50%;
			transform: translate(-50%, -50%);
		}

		body {
			font-size : 24px;
			font-family : arial;
			margin : 0px;
			background-color : #f0f1f2;
		}

		form {
			max-width : 700px;
			margin : auto;
		}

		.content {
			width : 90%;
			margin : auto;
		}

		button {
			background-color : #3268a8;
			border : none;
			color : white;
			padding-top : 20px;
			padding-bottom : 20px;
			margin-top : 50px;
			margin-bottom : 30px;
			cursor : pointer;
			font-size : 24px;
			width : 100%;
			border-radius : 5px;
		}

		.right {
		    text-align : right;
		}

		.delete {
			background-color : #ff3333;
		}

		input {
			font-size : 24px;
		}

		input[type=text] {
			width : 100%;
			font-size : 28px;
		}

		input[type=file] {
			width : 100%;
		}

		input[type=checkbox] {
			transform: scale(2.0);
		}

		table[class=settings] {
		    width: 100%;
		    font-size: 24px;
		}
		table[class=settings] th {
		    text-align: left;
		}

		.filepond {
			padding-bottom: 40px;
		}

		.label {
			padding : 40px 0px 10px 0px;
			color : #4d4e4f;
			font-weight : 600;
		}

		.header {
			background-color : #10131c;
			width : 100%;
			color : white;
			padding : 16px;
			margin-bottom : 10px;
			box-sizing : border-box;
		}

		.menuitems {
			margin-top : 64px;
			height : 100%;
			display : none;
		}

		.menuitems a {
			margin-top : 24px;
			font-size : 36px;
			display : block;
		}

		#mainmenuicon {
		    display : block;
		    position : absolute;
		    right : 15px;
		    top : 5px;
		    font-size: 40px;
		}

		#audiomenuicon {
			display : block;
			position : absolute;
			right : 70px;
			top : 5px;
			font-size: 40px;
		}

		.game-name-suggestion {
          position: relative;
          display: inline-block;
          width: 100%;
          background: #3268a8;
		  color: white;
          border: none;
          z-index: 99;
          /*position the autocomplete items to be the same width as the container:*/
          top: 100%;
          left: 0;
          right: 0;
          cursor: pointer;
        }
        .game-image-suggestion {
          cursor: pointer;
        }
        .game-name-suggestion:hover {
            background: #10131c;
        }
        .steamgridapi {
			position: relative;
            display: inline-block;
        }

		.tabs {
			margin-bottom: 20px;
		}

		.tab {
			width: 33.3%;
			background: #548aca;
			display: inline-block;
			text-align: center;
			color: white;
			cursor: pointer;
			font-size: 18px;
			padding-top: 12px;
			padding-bottom: 12px;
		}

		#game-images {
			text-align: center;
		}

		.tab.selected {
			background: #3268a8;
		}

		.tab.left {
			border-radius: 5px 0px 0px 5px;
		}

		.tab.right {
			border-radius: 0px 5px 5px 0px;
		}

		#banner-url {
			width: 100%;
		}
	</style>

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

			% if get('name') :
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
                <a href="/steam/restart">Restart Steam</a>
                <a href="/steam/compositor">Toggle Compositor</a>
                <a href="/mangohud">Toggle Mangohud</a>
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
