/*
 * 鉄道マップ全国版 — 記事 TTS (Text-to-Speech) ウィジェット
 *
 * 動作:
 *  - 右下に折りたたみ式の音声読み上げボタンを表示（記事ページ＝<main class="article"> 配下のみ）
 *  - 本文 → 日本語女性声 / バルーン (.speech) → 日本語男性声 を可能な限り選択
 *  - 再生 / 一時停止 / 停止 / 次のセクションへスキップ
 *  - 速度（0.5〜2x）を localStorage に保存して次回も反映
 *  - 読み上げ中の段落をハイライト＋スクロール追従
 *  - 除外: .page-meta / .map-cta / .related / 「関連情報・参考リンク」h2以降
 *
 * 制約（OS依存・回避不可）:
 *  - iOS Safari: バックグラウンド／画面ロックで再生停止（iOS 仕様）
 *  - Android Chrome: Google TTS の有無で音声品質に差
 *  - 男女声: voice 一覧に該当声がない環境では fallback で同じ声に統一
 */

(function () {
  'use strict';

  // 記事要素がなければ何もしない（index/about 等の非記事ページ）
  var article = document.querySelector('main.article');
  if (!article) return;

  // SpeechSynthesis 未対応ブラウザではフォールバック（ウィジェット自体非表示）
  if (!('speechSynthesis' in window) || !('SpeechSynthesisUtterance' in window)) return;

  // ---- 各OSの代表的な日本語TTS voice 名（優先順） ----
  var JP_FEMALE_PATTERNS = [
    'Kyoko', 'O-ren', 'Haruka', 'Nanami', 'Ayumi', 'Sayaka', 'Mizuki', 'Tomoko',
    'Google 日本語', 'ja-jp-standard-a', 'ja-jp-standard-c'
  ];
  var JP_MALE_PATTERNS = [
    'Otoya', 'Keita', 'Ichiro', 'Hattori',
    'ja-jp-standard-b', 'ja-jp-standard-d'
  ];

  // ---- State ----
  var voices = { female: null, male: null };
  var queue = [];            // [{ text, voiceType: 'female'|'male', element }]
  var position = 0;
  var currentElement = null;
  var isPlaying = false;
  var isPaused = false;
  var rate = parseFloat(localStorage.getItem('tts-rate') || '1.0');
  if (!isFinite(rate) || rate < 0.5 || rate > 2) rate = 1.0;

  // ---- 文末で文字列を分割（句読点を保持） ----
  function splitSentences(text) {
    if (!text) return [];
    var parts = [];
    var current = '';
    var terminators = '。！？!?';
    for (var i = 0; i < text.length; i++) {
      var ch = text[i];
      current += ch;
      if (terminators.indexOf(ch) >= 0) {
        var t = current.trim();
        if (t) parts.push(t);
        current = '';
      }
    }
    var tail = current.trim();
    if (tail) parts.push(tail);
    // 安全上限: 1 utterance あたり 240字（Chrome の 15秒制限への対策）
    return parts.filter(function (s) { return s.length > 0 && s.length <= 240; });
  }

  // ---- DOM Walker: 再生キューを構築 ----
  function buildQueue() {
    var items = [];
    var inSkipSection = false;

    Array.prototype.forEach.call(article.children, function (block) {
      // 除外: ステータス情報・地図CTA・関連ページ
      if (block.matches && block.matches('.page-meta, .map-cta, .related')) return;

      // 「関連情報・参考リンク」h2 を検出したら以降を全スキップ
      if (block.tagName === 'H2' && /関連情報/.test(block.textContent || '')) {
        inSkipSection = true;
        return;
      }
      if (inSkipSection) return;

      // バルーン (.speech) → 男性声
      if (block.classList && block.classList.contains('speech')) {
        var bubble = block.querySelector('.speech__bubble');
        var bText = bubble ? bubble.textContent.trim() : '';
        if (bText) splitSentences(bText).forEach(function (s) {
          items.push({ text: s, voiceType: 'male', element: block });
        });
        return;
      }

      // テーブル: 行ごと
      if (block.tagName === 'TABLE') {
        var rows = block.querySelectorAll('tr');
        Array.prototype.forEach.call(rows, function (row) {
          var cells = Array.prototype.map.call(
            row.querySelectorAll('th, td'),
            function (c) { return (c.textContent || '').trim(); }
          ).filter(Boolean).join('、');
          if (cells) items.push({ text: cells, voiceType: 'female', element: row });
        });
        return;
      }

      // リスト: li ごと
      if (block.tagName === 'UL' || block.tagName === 'OL') {
        Array.prototype.forEach.call(block.querySelectorAll('li'), function (li) {
          var liText = (li.textContent || '').replace(/\s+/g, ' ').trim();
          if (liText) splitSentences(liText).forEach(function (s) {
            items.push({ text: s, voiceType: 'female', element: li });
          });
        });
        return;
      }

      // 見出し・段落・disclaimer・blockquote 等
      var text = (block.textContent || '').replace(/\s+/g, ' ').trim();
      if (text) splitSentences(text).forEach(function (s) {
        items.push({ text: s, voiceType: 'female', element: block });
      });
    });

    return items;
  }

  // ---- Voice 選択 ----
  function selectVoices() {
    var all = speechSynthesis.getVoices() || [];
    var jp = all.filter(function (v) { return v.lang && v.lang.toLowerCase().indexOf('ja') === 0; });
    if (jp.length === 0) return;

    function findByPatterns(patterns) {
      for (var i = 0; i < patterns.length; i++) {
        var p = patterns[i].toLowerCase();
        for (var j = 0; j < jp.length; j++) {
          if (jp[j].name.toLowerCase().indexOf(p) >= 0) return jp[j];
        }
      }
      return null;
    }

    voices.female = findByPatterns(JP_FEMALE_PATTERNS) || jp[0];
    voices.male = findByPatterns(JP_MALE_PATTERNS)
      || jp.find(function (v) { return v !== voices.female; })
      || jp[0];
  }

  function ensureVoicesLoaded() {
    return new Promise(function (resolve) {
      var ready = speechSynthesis.getVoices();
      if (ready && ready.length > 0) {
        selectVoices();
        return resolve();
      }
      var done = false;
      function onChanged() {
        if (done) return;
        done = true;
        selectVoices();
        resolve();
      }
      speechSynthesis.addEventListener
        ? speechSynthesis.addEventListener('voiceschanged', onChanged)
        : (speechSynthesis.onvoiceschanged = onChanged);
      setTimeout(onChanged, 1500); // タイムアウトフォールバック
    });
  }

  // ---- Playback ----
  function playFromCurrent() {
    if (position >= queue.length) {
      stop();
      return;
    }
    var item = queue[position];

    // ハイライト（要素が変わった時だけ DOM 操作）
    if (currentElement !== item.element) {
      if (currentElement) currentElement.classList.remove('tts-reading');
      item.element.classList.add('tts-reading');
      try {
        item.element.scrollIntoView({ block: 'center', behavior: 'smooth' });
      } catch (e) {
        item.element.scrollIntoView();
      }
      currentElement = item.element;
    }

    var u = new SpeechSynthesisUtterance(item.text);
    u.lang = 'ja-JP';
    u.rate = rate;
    if (item.voiceType === 'male' && voices.male) u.voice = voices.male;
    else if (voices.female) u.voice = voices.female;

    u.onend = function () {
      if (!isPlaying || isPaused) return;
      position += 1;
      playFromCurrent();
    };
    u.onerror = function () {
      // エラーは飛ばして次へ
      position += 1;
      if (isPlaying && !isPaused) playFromCurrent();
    };
    try {
      speechSynthesis.speak(u);
    } catch (e) {
      // 何らかの理由で speak が失敗したら次へ
      position += 1;
      if (isPlaying && !isPaused) playFromCurrent();
    }
  }

  function play() {
    // 一時停止からの復帰
    if (isPaused) {
      try { speechSynthesis.resume(); } catch (e) {}
      isPaused = false;
      isPlaying = true;
      updateUI();
      return;
    }
    if (queue.length === 0) queue = buildQueue();
    if (queue.length === 0) return;
    isPlaying = true;
    isPaused = false;
    updateUI();
    ensureVoicesLoaded().then(function () {
      playFromCurrent();
    });
  }

  function pause() {
    try { speechSynthesis.pause(); } catch (e) {}
    isPaused = true;
    isPlaying = true; // 状態としては再生中・一時停止
    updateUI();
  }

  function stop() {
    try { speechSynthesis.cancel(); } catch (e) {}
    isPlaying = false;
    isPaused = false;
    position = 0;
    if (currentElement) {
      currentElement.classList.remove('tts-reading');
      currentElement = null;
    }
    updateUI();
  }

  function skipNextSection() {
    // 現在位置以降で最初の <h2> を探す
    for (var i = position + 1; i < queue.length; i++) {
      var el = queue[i].element;
      if (el.tagName === 'H2') {
        position = i;
        try { speechSynthesis.cancel(); } catch (e) {}
        if (isPlaying && !isPaused) {
          setTimeout(playFromCurrent, 50);
        } else {
          // 停止中ならハイライトだけ移動
          if (currentElement) currentElement.classList.remove('tts-reading');
          el.classList.add('tts-reading');
          try { el.scrollIntoView({ block: 'center', behavior: 'smooth' }); }
          catch (e) { el.scrollIntoView(); }
          currentElement = el;
        }
        return;
      }
    }
    // 残りセクションなし
    stop();
  }

  function setRate(newRate) {
    var r = parseFloat(newRate);
    if (!isFinite(r)) r = 1.0;
    rate = r;
    try { localStorage.setItem('tts-rate', String(rate)); } catch (e) {}
    // 再生中なら現在の utterance をキャンセルして同位置から再生し直し（rate 変更を即時反映）
    if (isPlaying && !isPaused && speechSynthesis.speaking) {
      try { speechSynthesis.cancel(); } catch (e) {}
      setTimeout(function () {
        if (isPlaying && !isPaused) playFromCurrent();
      }, 50);
    }
  }

  // ---- UI ----
  var widget, fab, playBtn, pauseBtn, stopBtn, skipBtn, closeBtn, rateSelect;

  function createUI() {
    widget = document.createElement('div');
    widget.id = 'tts-widget';
    widget.className = 'tts-widget';
    widget.dataset.state = 'collapsed';
    widget.innerHTML = [
      '<button class="tts-widget__fab" type="button" aria-label="この記事を音声で聞く">',
      '  <span class="tts-widget__fab-icon" aria-hidden="true">▶</span>',
      '  <span class="tts-widget__fab-label">音声で聞く</span>',
      '</button>',
      '<div class="tts-widget__panel" role="dialog" aria-label="音声読み上げコントロール">',
      '  <div class="tts-widget__header">',
      '    <span class="tts-widget__title">▶ この記事を音声で聞く</span>',
      '    <button class="tts-widget__close" type="button" aria-label="閉じる">✕</button>',
      '  </div>',
      '  <div class="tts-widget__controls">',
      '    <button class="tts-widget__play" type="button">▶ 再生</button>',
      '    <button class="tts-widget__pause" type="button" hidden>⏸ 一時停止</button>',
      '    <button class="tts-widget__stop" type="button">⏹ 停止</button>',
      '    <button class="tts-widget__skip" type="button" aria-label="次のセクションへ" title="次のセクションへ">⏭</button>',
      '  </div>',
      '  <div class="tts-widget__rate">',
      '    <label for="tts-rate-select">速度</label>',
      '    <select id="tts-rate-select">',
      '      <option value="0.5">0.5x</option>',
      '      <option value="0.75">0.75x</option>',
      '      <option value="1">1x</option>',
      '      <option value="1.25">1.25x</option>',
      '      <option value="1.5">1.5x</option>',
      '      <option value="2">2x</option>',
      '    </select>',
      '  </div>',
      '  <p class="tts-widget__note">※ 画面OFFや別タブ・バックグラウンドで再生が中断する場合があります</p>',
      '</div>'
    ].join('\n');
    document.body.appendChild(widget);

    fab = widget.querySelector('.tts-widget__fab');
    playBtn = widget.querySelector('.tts-widget__play');
    pauseBtn = widget.querySelector('.tts-widget__pause');
    stopBtn = widget.querySelector('.tts-widget__stop');
    skipBtn = widget.querySelector('.tts-widget__skip');
    closeBtn = widget.querySelector('.tts-widget__close');
    rateSelect = widget.querySelector('#tts-rate-select');

    rateSelect.value = String(rate);

    fab.addEventListener('click', function () { widget.dataset.state = 'expanded'; });
    closeBtn.addEventListener('click', function () {
      // 閉じるときに再生中なら停止
      if (isPlaying) stop();
      widget.dataset.state = 'collapsed';
    });
    playBtn.addEventListener('click', play);
    pauseBtn.addEventListener('click', pause);
    stopBtn.addEventListener('click', stop);
    skipBtn.addEventListener('click', skipNextSection);
    rateSelect.addEventListener('change', function (e) { setRate(e.target.value); });
  }

  function updateUI() {
    if (!playBtn || !pauseBtn) return;
    if (isPlaying && !isPaused) {
      playBtn.hidden = true;
      pauseBtn.hidden = false;
    } else {
      playBtn.hidden = false;
      pauseBtn.hidden = true;
    }
  }

  // ---- 初期化（defer なので DOM はパース済み） ----
  createUI();
  ensureVoicesLoaded(); // バックグラウンドで voice 一覧を準備

  // ページ離脱時にクリーンアップ
  window.addEventListener('beforeunload', function () {
    try { speechSynthesis.cancel(); } catch (e) {}
  });
})();
