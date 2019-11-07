% rebase('base.tpl')

<a href="/platforms/{{platform}}/new">
    <img src="/images/add.png" alt="Add new shortcut" title="Add new shortcut"></img>
</a>

% for s in shortcuts:
    <a href="/platforms/{{platform}}/edit/{{s['name']}}">
        <img class="{{s['hidden']}}" src="{{s['banner']}}" alt="{{s['name']}}" title="{{s['name']}}"></img>
    </a>
% end
