% rebase('base.tpl')

% for shortName, displayName in platforms.items():
	<a href="/platforms/{{shortName}}"><img src="images/{{shortName}}.png" alt="{{displayName}}"/></a>
% end
