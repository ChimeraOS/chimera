% rebase('base.tpl', content_share_only=get('content_share_only'))

<script src="/public/alpinejs@3.12.0.min.js"></script>

<style>

</style>

<div style="max-width: 600px; margin: auto; padding-top: 2em;" >
  <h2>Bulk Upload</h2>
  <form>
    <input type="file" class="filepond" name="bulk_files" multiple border-style="solid"
    />
  </form>
  <div style="text-align: center; margin-top: 1em;">
    <p>Or click to select files for bulk upload.</p>

  </div>
  <a href="/library/{{platform}}" style="display: inline-block; margin-top: 1em; color: black; text-decoration: underline;">
    Back to Library
  </a>
  
</div>

<script>
const bulk_upload_allowed = {{'true' if user_steamgriddb_key_set else 'false'}}
FilePond.setOptions({
  server : '/shortcuts/file-upload',
  chunkUploads : true,
  chunkSize : 1000000, // 1 MB
  beforeAddFile: (file) => {
    if (!bulk_upload_allowed) {
      alert('You are still using the default SteamGridDB API key provided with Chimera. Bulk uploading requires users to uplaod their own API Key. Go to system settings to update the key.')
      return false;
    }
    return true;
  }
})

FilePond.parse(document.body);
const pond = FilePond.find(document.querySelector('.filepond'));
let shortcut_creation_in_progress = false;
pond.on('processfile', (error, file) => {
  
  const md = {game_name : file.filenameWithoutExtension, file_name: file.filename, content: file.serverId, platform: "{{platform}}"}
  shortcut_creation_in_progress = true;
  
  fetch("/shortcuts/auto/new", {
    method: "POST", 
    headers: {"Content-Type": "application/json"}, 
    body: JSON.stringify(md)
  }).finally(() => {
    
    shortcut_creation_in_progress = false;
  })
})

window.addEventListener('beforeunload', (e) => {
  if (pond.getFiles().some(f => f.status === FilePond.FileStatus.PROCESSING) || shortcut_creation_in_progress) {
    e.preventDefault();
    e.returnValue = ''; // Chrome requires returnValue to be set
  }
});


</script>
