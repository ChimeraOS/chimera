% rebase('base.tpl')
We use FFmpeg for streaming and recording, here you can configure inputs and used video and audio codecs.
<h4>Inputs</h4>
<hr>
% for i in range(len(inputs)):
<form action="/streaming/remove_input/{{i}}" method="post" enctype="multipart/form-data">
    <input type="text" value="{{inputs[i]}}" id="input{{i}}" readonly>
    <button>Remove Input</button>
<hr>
</form>
%end
New Input
<form action="/streaming/add_input" method="post" enctype="multipart/form-data">
    <input type="text" id="new_input" name="new_input">
    <button>Add Input</button>
<hr>
</form>

<h4>Video Codec and options</h4>
<hr>
% for i in range(len(vcodecs)):
<form action="/streaming/remove_vcodec/{{i}}" method="post" enctype="multipart/form-data">
    <input type="text" value="{{vcodecs[i]}}" id="vcodecs{{i}}" readonly>
    <button>Remove Video Codec</button>
<hr>
</form>
%end
New Video Codec
<form action="/streaming/add_vcodec" method="post" enctype="multipart/form-data">
    <input type="text" id="new_vcodec" name="new_vcodec">
    <button>Add Video Codec</button>
<hr>
</form>

<h4>Audio Codec and options</h4>
<hr>
% for i in range(len(acodecs)):
<form action="/streaming/remove_acodec/{{i}}" method="post" enctype="multipart/form-data">
    <input type="text" value="{{acodecs[i]}}" id="acodecs{{i}}" readonly>
    <button>Remove Audio Codec</button>
<hr>
</form>
%end
New Audio Codec
<form action="/streaming/add_acodec" method="post" enctype="multipart/form-data">
    <input type="text" id="new_acodec" name="new_acodec">
    <button>Add Audio Codec</button>
<hr>
</form>
