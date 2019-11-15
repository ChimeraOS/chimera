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

		.flathub-link, .flathub-new {
		    display : inline;
		    float : left;
		    margin : 10px;
		    width : 460px;
		    height : 215px;
		}

		.flathub-new img {
            margin:  0px;
            width : 100%;
            height : 100%;
        }

        .flathub {
            width: 100%;
			height : 100%;
			text-align: center;
			border-width : 4px;
			border-style : solid;
			border-image : linear-gradient(to bottom, #888888, #666666) 1 1;
        }

        .flathub img {
            border-style : hidden;
            border-width : 0px;
            height :  128px;
            width : 128px;
            margin-top: 10px;
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
			margin-top : 30px;
			margin-bottom : 30px;
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
			color : white;
			padding : 16px;
			margin-bottom : 10px;
		}
	</style>
</head>
<body>
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
	</div>
	<div class="content">
		{{!base}}
	</div>
</body>
</html>
