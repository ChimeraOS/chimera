% rebase('base.tpl')
We use FFmpeg for streaming and recording, here you can configure inputs and used video and audio codecs.
<h4>Inputs</h4>
<hr>
Current Inputs
% for i in range(len(inputs)):
<form action="/streaming/remove_input/{{i}}" method="post" enctype="multipart/form-data">
    <input type="text" value="{{inputs[i]}}" id="input{{i}}" readonly>
    <button>Remove Input</button>
</form>
%end
New Input
<form action="/streaming/add_input" method="post" enctype="multipart/form-data">
    <input type="text" id="new_input" name="new_input">
    <button>Add Input</button>
</form>
