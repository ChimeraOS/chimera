<style>
body {
	font-size : 24px;
}

input {
	width : 100%
}

input[type=submit] {
	padding-top : 20px;
	padding-bottom : 20px;
	margin-top : 40px;
}

select {
  width: 100%;
  padding: 16px 20px;
  border: none;
  border-radius: 4px;
  background-color: #f1f1f1;
}

.header {
	padding : 20px 0px 10px 0px;
}
</style>

<form action="/shortcuts/edit" method="post" enctype="multipart/form-data">
	<input type="hidden" value="{{platform}}" name="platform">
	<input type="hidden" value="{{name}}" name="original_name">

	<div class="header">Name:</div>
	<input type="text" name="name" value="{{name}}" />

	<div class="header">Hidden:</div>
	<input type="checkbox" name="hidden" {{'checked' if hidden else ''}} />

	<div class="header">Banner:</div>
	<input type="file" name="banner" />

	<div class="header">Content:</div>
	<input type="file" name="content" />

	<input type="submit" value="Update" />
</form>

<form action="/shortcuts/delete" method="post">
	<input type="hidden" value="{{platform}}" name="platform">
	<input type="hidden" value="{{name}}" name="name">
	<input type="submit" value="Delete" />
</form>
