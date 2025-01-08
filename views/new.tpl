% rebase('base.tpl', content_share_only=get('content_share_only'))

<script src="/public/alpinejs@3.12.0.min.js"></script>

<script>

const IMAGE_TYPES = ['banner', 'poster', 'background', 'logo', 'icon'];

function capitalize(word) {
	return word.charAt(0).toUpperCase() + word.slice(1);
}

async function fetchimgs(url) {
	const response = await fetch(url);
	const json = await response.json();
	return json.data;
}

function images() {
	return {
		isEditing: '{{isEditing}}' === 'True',
		gameName: "{{!name}}",
		gameID: null,
		gameOptions: [],
		showSuggestions: true,
		async clearGameOptions() {
			await new Promise(r => setTimeout(r, 500));
			this.showSuggestions = false;
			this.gameOptions = [];
		},
		async updateGameOptions() {
			if (!this.gameName) {
				this.gameOptions = [];
				return;
			}
			url = "/steamgrid/search/" + this.gameName.replace(/'/g, "");
			response = await fetch(url);
			games = await response.json();
			if (!games.success || !this.showSuggestions) {
				this.showSuggestions = true;
				this.gameOptions = [];
				return;
			}

			if (!this.isEditing) {
				this.gameOptions = games.data;
				return;
			}

			if (games.data && games.data.length > 0) {
				this.setGameName(games.data[0].name, games.data[0].id);
			}
		},
		images: {
			banner: [{}],
			poster: [{}],
			background: [{}],
			logo: [{}],
			icon: [{}],
		},

		selected: {
			banner: 0,
			poster: 0,
			background: 0,
			logo: 0,
			icon: 0,
		},

		imageURLs: {
			banner: null,
			poster: null,
			background: null,
			logo: null,
			icon: null,
		},

		setGameName(name, id) {
			this.showSuggestions = false;
			if (!this.isEditing) {
				this.gameName = name;
			}
			this.gameID = id;
			this.gameOptions = [];
			this.selected = {
				banner: 0,
				poster: 0,
				background: 0,
				logo: 0,
				icon: 0,
			};

			this.images = {
				banner: [{}],
				poster: [{}],
				background: [{}],
				logo: [{}],
				icon: [{}],
			};

			this.imageURLs = {
				banner: null,
				poster: null,
				background: null,
				logo: null,
				icon: null,
			};

			this.loadImages();
		},

		next(type) {
			this.selected[type] += 1;
			if (this.selected[type] >= this.images[type].length) {
				this.selected[type] = 0;
			}

			this.imageURLs[type] = this.getImg(type, 'url');
		},

		prev(type) {
			this.selected[type] -= 1;
			if (this.selected[type] < 0) {
				this.selected[type] = this.images[type].length - 1;
			}
			this.imageURLs[type] = this.getImg(type, 'url');
		},

		async loadImages() {
			for (type of IMAGE_TYPES) {
				this.images[type] = await fetchimgs(`/steamgrid/images/${this.gameID}?type=${type}`);
				this.imageURLs[type] = this.getImg(type, 'url');
			}
		},

		getImg(type, field) {
			if (!this.images[type]) {
				return null;
			}

			if (!this.images[type][this.selected[type]]) {
				return null;
			}

			return this.images[type][this.selected[type]][field] || null;
		}
	};
}
</script>


<div x-data="images()">
<form autocomplete="off" action="/shortcuts/{{ 'edit' if isEditing else 'new' }}" method="post" enctype="multipart/form-data">
	<input type="hidden" value="{{name}}" name="original_name">
	<input type="hidden" value="{{platform}}" name="platform">

	<div class="label">Name</div>
	<div class="steamgridapi">
		<input id="gamename" @blur="clearGameOptions()" x-effect="updateGameOptions()" x-model.debounce.500ms="gameName" type="text" name="name" value="{{name}}" required {{ 'disabled' if isEditing else '' }}/>
		<template x-for="game in gameOptions" x-show="showSuggestions">
			<div class="game-name-suggestion" @click="setGameName(game.name, game.id)" x-text="game.name"></div>
		</template>
	</div>

	<div class="label">Hidden</div>
	<input type="checkbox" name="hidden" {{'checked' if hidden else ''}} />

	<div class="label">Content</div>
	<input type="file" class="filepond" name="content" />

	<template x-for="type in IMAGE_TYPES">
		<div>
			<div class="label" x-text="capitalize(type)"></div>
			<div style="margin-top: 10px; margin-bottom: 30px; user-select: none;">
				<span style="font-size: 40px; cursor: pointer;" @click="prev(type)">⬅️ </span>
				<img style="all: initial; max-width: 60%; vertical-align:middle" :src="getImg(type, 'thumb')">
				<input x-model="imageURLs[type]" type="hidden" :id="`image-url-${type}`" :name="`image-url-${type}`" />
				<span style="font-size: 40px; cursor: pointer;" @click="next(type)">➡️ </span>
			</div>
		</div>
	</template>

	% if isEditing :
		<button>Update</button>
	% else :
		<button>Add</button>
	% end
</form>
</div>

<script>
FilePond.parse(document.body);
FilePond.setOptions({
	server : '/shortcuts/file-upload',
	chunkUploads : true,
	chunkSize : 1000000 // 1 MB
});
</script>

% if steamShortcutID:
<form action="/launch/{{steamShortcutID}}">
	<button>Launch</button>
</form>
% end

% if isEditing:
<form action="/shortcuts/delete" method="post">
	<input type="hidden" value="{{platform}}" name="platform">
	<input type="hidden" value="{{name}}" name="name">
	<button class="delete">Delete</button>
</form>
% end
