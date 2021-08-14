% rebase('base.tpl')

% for shortName, displayName in platforms.items():
<div class="img-container">
	<a href="/library/{{shortName}}"><img src="images/{{shortName}}.png" alt="{{displayName}}"/></a>
</div>
% end
