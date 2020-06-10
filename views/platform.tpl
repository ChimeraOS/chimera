% rebase('base.tpl')

<a href="/platforms/{{platform}}/new">
    <img src="/images/add.png" alt="Add new shortcut" title="Add new shortcut"/>
</a>

% for s in shortcuts:
    <a href="/platforms/{{platform}}/edit/{{s['name']}}">
        % if s['banner'] == None :
            <div class="missing {{s['hidden']}}">
                <img src="/images/add.png" alt="{{s['name']}}" title="{{s['name']}}"/>
                <span class="missing-text">{{s['name']}}</span>
            </div>
        % else :
            <img class="{{s['hidden']}}" src="{{s['banner']}}" alt="{{s['name']}}" title="{{s['name']}}"/>
    </a>
% end
