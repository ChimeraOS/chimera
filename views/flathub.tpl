% rebase('base.tpl')

% if isInstalledOverview:
<a class="flathub-new" href="/platforms/flathub/new">
    <img src="/images/add.png" alt="Add new shortcut" title="Add new shortcut"></img>
</a>
% end

% for app in app_list:
<a class="flathub-link" href="/platforms/flathub/edit/{{ app.flatpak_id }}">
    <div class="flathub">
      <img src="{{ app.image_url }}" alt="{{ app.name }}" title="{{ app }}"></img>
      <h3>{{app.name}}</h3>
    </div>
</a>
% end