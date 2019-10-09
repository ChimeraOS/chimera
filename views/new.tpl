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

<form action="/shortcuts" method="post" enctype="multipart/form-data">
	<div class="header">Name:</div>
	<input type="text" name="name" />

	<input type="hidden" value="{{platform}}" name="platform">
<!--
	<div class="header">Platform:</div>
	<select name="platform">
		<option value="nes">Nintendo</option>
		<option value="snes">Super Nintendo</option>
		<option value="genesis">Sega Genesis</option>
	</select>
-->

	<div class="header">Hidden:</div>
	<input type="checkbox" name="hidden" />

	<div class="header">Banner:</div>
	<input type="file" name="banner" />

	<div class="header">Content:</div>
	<input type="file" name="content" />

	<input type="submit" value="Add" />
</form>
