% rebase('base.tpl')
<form autocomplete="off" action="/shortcuts/{{ 'edit' if isEditing else 'new' }}" method="post" enctype="multipart/form-data">
	<input type="hidden" value="{{name}}" name="original_name">
	<input type="hidden" value="{{platform}}" name="platform">

	<div class="label">Name</div>
	<div class="steamgridapi">
	    <input id="gamename" type="text" name="name" value="{{name}}" required {{ 'disabled' if isEditing else '' }}/>
	    <div id="game-options"></div>
	</div>

	<div class="label">Hidden</div>
	<input type="checkbox" name="hidden" {{'checked' if hidden else ''}} />

	<div class="label">Content</div>
	<input type="file" class="filepond" name="content" />

	<div class="label">Banner</div>
	<div class="tabs">
		<div id="banner_upload_tab" class="tab left" onclick="show('banner_upload')">
			Upload
		</div><div id="banner_url_tab" class="tab" onclick="show('banner_url')">
			URL
		</div><div id="banner_steamgriddb_tab" class="tab right" onclick="show('banner_steamgriddb')">
			SteamGridDB
		</div>
	</div>

	<div id="banner_upload_content">
		<input type="file" class="filepond" name="banner" />
	</div>

	<div id="banner_url_content">
		<input id="banner-url" name="banner-url" />
	</div>

	<div id="banner_steamgriddb_content">
		<div id="game-images">
			% if not isEditing:
				<p class="placeholder">No banner images found. Enter a valid game name.</p>
			% end
		</div>
	</div>

	% if isEditing :
		<button>Update</button>
	% else :
		<button>Add</button>
	% end
</form>

<script>
FilePond.parse(document.body);
FilePond.setOptions({
	server : '/shortcuts/file-upload',
	chunkUploads : true,
	chunkSize : 1000000 // 1 MB
});
</script>


% if isEditing:
<form action="/shortcuts/delete" method="post">
	<input type="hidden" value="{{platform}}" name="platform">
	<input type="hidden" value="{{name}}" name="name">
	<button class="delete">Delete</button>
</form>
% end

<script>
    let games = [];
    function setImage(url, selectedID) {
        let field = document.getElementById("banner-url");
        field.value = url;
        const gameImages = document.getElementsByClassName("img-container");
		for (const img of gameImages) {
			if (img.id === selectedID) {
				img.classList.add("selected");
			} else {
				img.classList.remove("selected");
			}
		}
    }

	const banner_upload_content = document.getElementById("banner_upload_content");
	const banner_url_content = document.getElementById("banner_url_content");
	const banner_steamgriddb_content = document.getElementById("banner_steamgriddb_content");
	const banner_content_elements = [ banner_upload_content, banner_url_content, banner_steamgriddb_content ];

	const banner_upload_tab = document.getElementById("banner_upload_tab");
	const banner_url_tab = document.getElementById("banner_url_tab");
	const banner_steamgriddb_tab = document.getElementById("banner_steamgriddb_tab");

	const banner_tab_elements = [ banner_upload_tab, banner_url_tab, banner_steamgriddb_tab ];

	function show(id) {
		for (element of banner_content_elements) {
			element.style.display = "none";
		}

		for (element of banner_tab_elements) {
			element.classList.remove("selected");
		}

		var target_tab = document.getElementById(id+'_tab');
		var target_content = document.getElementById(id+'_content');
		target_content.style.display = "block";
		target_tab.classList.add("selected");
	}

	show('banner_upload');

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
        images.data.forEach(function (image, i) {
			container = document.createElement("div");
			container.setAttribute("class", "img-container");
            entry = document.createElement("IMG");
			container.setAttribute("id", `img-${i}`);
            entry.setAttribute("class", "game-image-suggestion");
            entry.setAttribute("src", image.thumb);
            entry.setAttribute("onclick", `setImage('${image.url}', 'img-${i}')`);
			container.appendChild(entry);
            imagesElement.appendChild(container);
        });
    }


	let timer;
	let lastSearch = '';
	const nameInput = document.getElementById('gamename');
	nameInput.addEventListener('keyup', () => {
	    clearTimeout(timer);
	    if (nameInput.value && nameInput.value !== lastSearch) {
	        timer = setTimeout(completeGameName, 700);
	    }
	});

	async function completeGameName() {
		lastSearch = nameInput.value;
        url = "/steamgrid/search/" + lastSearch;
        response = await fetch(url);
        games = await response.json();
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

    async function suggestImagesOnEdit() {
        let field = document.getElementById("gamename")
        if (field.value) {
            url = "/steamgrid/search/" + field.value;
            response = await fetch(url);
            games = await response.json();

            if (!games.success) {
            return;
            }

            games.data.forEach(function (game) {
                if (game.name == field.value) {
                    setGameName(game.name, game.id);
                }
            });
        }
    }
    // When clicking somewhere, close the suggestions
    document.addEventListener("click", function (e) {
        document.getElementById("game-options").innerHTML = '';
    });
    suggestImagesOnEdit();
</script>