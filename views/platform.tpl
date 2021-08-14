% rebase('base.tpl')

<div class="img-container">
    <a href="/library/{{platform}}/new">
        <img src="/images/add.png" alt="Add new shortcut" title="Add new shortcut"/>
    </a>
</div>

% from urllib.parse import quote
% for s in shortcuts:
<a href="/library/{{platform}}/edit/{{quote(s['name'])}}">
    <div class="img-container {{s['hidden']}}">
        % if s['banner'] == None :
            <span class="missing-text">{{s['name']}}</span>
        % else :
            <img class="{{s['hidden']}}" src="{{quote(s['banner'])}}" alt="{{s['name']}}" title="{{s['name']}}"/>
        % end
    </div>
</a>
% end
