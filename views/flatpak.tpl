% rebase('base.tpl')

% if isInstalledOverview:
<a href="/flatpak/available">
    <img src="/images/add.png" alt="Add new shortcut" title="Add new shortcut"></img>
</a>
% end

% for app in app_list:
  <a href="/flatpak/app/{{ app.flatpak_id }}">
      <img src="{{ app.image_url }}" alt="{{ app.name }}" title="{{ app }}"></img>
  </a>
% end