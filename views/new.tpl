% rebase('base.tpl')
<form autocomplete="off" action="/shortcuts/{{ 'edit' if isEditing else 'new' }}" method="post" enctype="multipart/form-data">
	<input type="hidden" value="{{name}}" name="original_name">
	<input type="hidden" value="{{platform}}" name="platform">

	<div class="label">Name</div>
	<div class="steamgridapi">
	    <input id="gamename" type="text" name="name" oninput="completeGameName(this)" value="{{name}}" {{ 'disabled' if isEditing else '' }}/>
	    <div id="game-options"></div>
	</div>

	<div class="label">Hidden</div>
	<input type="checkbox" name="hidden" {{'checked' if hidden else ''}} />

	<div class="label">Banner</div>
	<input type="file" name="banner" />
	<input id="banner-url" name="banner-url" />
	<div id="game-images"></div>

	<div class="label">Content</div>
	<input type="file" name="content" />

	% if isEditing :
		<button>Update</button>
	% else :
		<button>Add</button>
	% end
</form>

% if isEditing:
<form action="/shortcuts/delete" method="post">
	<input type="hidden" value="{{platform}}" name="platform">
	<input type="hidden" value="{{name}}" name="name">
	<button class="delete">Delete</button>
</form>
% end

<script>
    let games = ["Super Mario 64", "Super Mario Bros", "Super Mario World", "Super Gradius"];
    function setImage(url) {
        let field = document.getElementById("banner-url")
        field.value = url
        let gameImages = document.getElementById("game-images");
        gameImages.innerHTML = '';
    }
    async function setGameName(gameName, gameId) {
        let field = await document.getElementById("gamename");
        let gameOptions = await document.getElementById("game-options");
        let gameImages = await document.getElementById("game-images");
        field.value = gameName;
        gameOptions.innerHTML = '';
        gameImages.innerHTML = '';

        url = "/steamgrid/images/" + gameId;
        response = await fetch(url);
        images = await response.json();
        imagesElement = await document.getElementById("game-images");
        images.data.forEach(function (image) {
            entry = document.createElement("IMG");
            entry.setAttribute("class", "game-image-suggestion");
            entry.setAttribute("src", image.thumb);
            entry.setAttribute("onclick", "setImage(\"" + image.url + "\")");
            imagesElement.appendChild(entry);
        });
    }
    async function completeGameName(input) {
        url = "/steamgrid/search/" + input.value;
        response = await fetch(url);
        games = await response.json();
        console.log(games);
        if (!games.success) {
            return;
        }
        gameOptions = await document.getElementById("game-options");
        gameOptions.innerHTML = '';
        games.data.forEach(function (game) {
            entry = document.createElement("DIV");
            entry.setAttribute("class", "game-name-suggestion");
            entry.setAttribute("onclick", "setGameName(\"" + game.name + "\", " + game.id +")");
            entry.innerHTML = game.name;
            gameOptions.appendChild(entry);
        });
    }
</script>