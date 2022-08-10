% rebase('base.tpl')
<body>
  % if recording:
  <div class="img-container">
    <a href="/record/stop"><img src="/images/stop.png" alt="Stop Recording"></a>
  </div>
  % else:
  <div class="img-container">
    <a href="/record/start"><img src="/images/record.png" alt="Start Recording"></a>
  </div>
  <form action="/streaming/config">
    <button>Configure FFmpeg</button>
  </form>
  % end
</body>

