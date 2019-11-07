<html>
<head>
	<title>SteamBuddy</title>
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

		.hidden {
			opacity : 0.25
		}

		.new-shortcut {
			width : 460px;
			height : 215px;
			color : white;
			background-color : #3268a8;
		}

		img {
			padding : 10px;
			width : 460px;
			height : 215px;
		}

		body {
			font-size : 24px;
			font-family : arial;
			margin : 0px;
			background-color : #f0f1f2;
		}

		form {
			max-width : 50%;
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
			margin-top : 40px;
			cursor : pointer;
			font-size : 24px;
			width : 100%;
			border-radius : 5px;
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

		.label {
			padding : 40px 0px 10px 0px;
			color : #4d4e4f;
			font-weight : 600;
		}

		.header {
			background-color : #10131c;
			width : 100%;
			height : 30px;
			color : white;
			padding : 20px 0;
			margin-bottom : 30px;
		}

		.nav {
			margin-left : 20px;
		}

	</style>
</head>
<body>
	<div class="header">
		<div class="nav">
			<a href="/">Home</a>
			% if get('platform') :
				<em>/</em> <a href="/platforms/{{platform}}">{{platformName}}</a>

				% if get('name') :
					<em>/</em> <a href="/platforms/{{platform}}/edit/{{name}}">{{name}}</a>
				% elif get('isNew') :
					<em>/</em> <a href="/platforms/{{platform}}/new">New</a>
				% end
			% end
		</div>
	</div>
	<div class="content">
		{{!base}}
	</div>
</body>
</html>
