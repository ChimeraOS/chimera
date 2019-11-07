% rebase('base.tpl')

% if isInstalledOverview:
<a href="/flatpak/available">
    <img src="/images/add.png" alt="Add new shortcut" title="Add new shortcut"></img>
</a>
% end

% for app in app_list:
  <a href="/flatpak/app/{{ app['flatpakAppId'] }}">
      <img src="https://flathub.org/{{ app['iconDesktopUrl'] }}" alt="{{ app['name'] }}" title="{{ app['name'] }}"></img>
  </a>
% end