% rebase('base.tpl')
<form action="/shortcuts/{{ 'edit' if isEditing else 'new' }}" method="post" enctype="multipart/form-data">
	<input type="hidden" value="{{name}}" name="original_name">
	<input type="hidden" value="{{platform}}" name="platform">

	<div class="label">Name</div>
	<input type="text" name="name" value="{{name}}" {{ 'disabled' if isEditing else '' }}/>

	<div class="label">Hidden</div>
	<input type="checkbox" name="hidden" {{'checked' if hidden else ''}} />

	<div class="label">Banner</div>
	<input type="file" name="banner" />

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
