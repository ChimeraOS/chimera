% rebase('base.tpl')
<body>
  % if streaming:
  <div class="img-container">
    <a href="/streaming/net/stop"><img src="/images/stop.png" alt="Stop Streaming"></a>
  </div>
  %end
  % if recording:
  <div class="img-container">
    <a href="/record/stop"><img src="/images/stop.png" alt="Stop Recording"></a>
  </div>
  %end
  % if not (recording or streaming):
  <div class="img-container">
    <a href="/record/start"><img src="/images/record.png" alt="Start Recording"></a>
  </div>
  <div class="img-container">
    <a href="/streaming/net/start"><img src="/images/stream.png" alt="Start Streaming on LAN"></a>
  </div>
  <form action="/streaming/config">
    <button>Configure FFmpeg</button>
  </form>
  % end
</body>

