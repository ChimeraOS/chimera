% rebase('base.tpl')

% for platform in platforms.values():
<div class="img-container">
	<a href="/library/{{platform['id']}}"><img src="images/{{platform['id']}}.png" alt="{{platform['name']}}"></a>
</div>
% end
