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

  // ---- 高品質 voice 検出用キーワード（iOS Enhanced / Microsoft Online Natural / Google WaveNet 等） ----
  var QUALITY_KEYWORDS = [
    'enhanced',   // Apple Enhanced（ユーザーが Settings から DL）
    'premium',    // Google Premium / 高品質バリアント
    'natural',    // Microsoft Natural（Edge 系の neural voice）
    'neural',     // 汎用 neural TTS
    'online',     // Microsoft Online voice（実質 neural）
    'wavenet',    // Google WaveNet
    'studio'      // Google Studio voice
  ];

  // voice の品質スコア（大きいほど高品質）
  function scoreVoiceQuality(v) {
    var s = 0;
    var lower = (v.name || '').toLowerCase();
    for (var i = 0; i < QUALITY_KEYWORDS.length; i++) {
      if (lower.indexOf(QUALITY_KEYWORDS[i]) >= 0) { s += 100; break; }
    }
    if (v.localService === true) s += 10; // ユーザーがローカルに DL したっぽい voice
    if (v.default === true) s += 3;
    return s;
  }

  // ---- State ----
  var voices = { female: null, male: null };
  var queue = [];            // [{ text, voiceType: 'female'|'male', element }]
  var position = 0;
  var isPlaying = false;
  var isPaused = false;
  var rate = parseFloat(localStorage.getItem('tts-rate') || '1.0');
  if (!isFinite(rate) || rate < 0.5 || rate > 2) rate = 1.0;

  // ---- 文末で文字列を分割（テーブル行用フォールバック・センテンス wrap しない場合に使用） ----
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
    return parts.filter(function (s) { return s.length > 0 && s.length <= 240; });
  }

  // ---- テキストノードを「。！？」で分割し <span class="tts-sentence" data-tts-sentence-id=N> でラップ ----
  // インライン要素（<strong>, <a> 等）を跨ぐ文にも対応。
  // 戻り値: [{ id, text }] — id は文ごとの一意ID（playback queue の sentenceId に対応）
  var __nextSentenceId = 0;
  function wrapTextNodesIntoSentences(container) {
    var sentences = [];
    var buffer = '';

    function flushSentence() {
      var t = buffer.replace(/\s+/g, ' ').trim();
      if (t && t.length <= 240) {
        sentences.push({ id: __nextSentenceId, text: t });
        __nextSentenceId += 1;
      } else if (t.length > 240) {
        // 安全上限超過: 240字でぶった切って次へ（極めて長い文への保険）
        sentences.push({ id: __nextSentenceId, text: t.slice(0, 240) });
        __nextSentenceId += 1;
      }
      buffer = '';
    }

    // text node 一覧を収集
    var textNodes = [];
    var walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, null, false);
    var n;
    while ((n = walker.nextNode())) {
      var parent = n.parentElement;
      if (!parent) continue;
      if (parent.tagName === 'SCRIPT' || parent.tagName === 'STYLE') continue;
      // 既にラップ済みのノードはスキップ（idempotent）
      if (parent.classList && parent.classList.contains('tts-sentence')) continue;
      textNodes.push(n);
    }

    textNodes.forEach(function (textNode) {
      var text = textNode.textContent;
      if (!text) return;

      // 全角空白だけのノードは buffer に足すだけ（DOM は変更しない）
      if (!text.replace(/\s/g, '').length) {
        buffer += text;
        return;
      }

      // 文末位置を検出
      var positions = [];
      for (var i = 0; i < text.length; i++) {
        if ('。！？!?'.indexOf(text[i]) >= 0) positions.push(i + 1);
      }

      var fragment = document.createDocumentFragment();
      var prev = 0;

      function appendPiece(piece) {
        if (!piece) return;
        var span = document.createElement('span');
        span.className = 'tts-sentence';
        span.dataset.ttsSentenceId = String(__nextSentenceId);
        span.appendChild(document.createTextNode(piece));
        fragment.appendChild(span);
        buffer += piece;
      }

      if (positions.length === 0) {
        // 文末なし → 全部 1 つのピースとして追加（文は継続中）
        appendPiece(text);
      } else {
        // 文末ごとに分割
        positions.forEach(function (pos) {
          appendPiece(text.slice(prev, pos));
          flushSentence(); // 文確定 → __nextSentenceId++
          prev = pos;
        });
        // 末尾の残り（次の text node に続く可能性あり）
        if (prev < text.length) appendPiece(text.slice(prev));
      }

      textNode.parentNode.replaceChild(fragment, textNode);
    });

    // 全 text node 処理後、buffer が残っていたら最後の文として確定
    flushSentence();

    return sentences;
  }

  // ---- 再生キューを構築（センテンス wrap も同時に実行） ----
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

      // バルーン (.speech) → 男性声・センテンス wrap
      if (block.classList && block.classList.contains('speech')) {
        var bubble = block.querySelector('.speech__bubble');
        if (bubble) {
          var sList = wrapTextNodesIntoSentences(bubble);
          sList.forEach(function (s) {
            items.push({ text: s.text, voiceType: 'male', block: block, sentenceId: s.id });
          });
        }
        return;
      }

      // テーブル: 行ごと（センテンス wrap せず、行全体をハイライト対象に）
      if (block.tagName === 'TABLE') {
        var rows = block.querySelectorAll('tr');
        Array.prototype.forEach.call(rows, function (row) {
          var cells = Array.prototype.map.call(
            row.querySelectorAll('th, td'),
            function (c) { return (c.textContent || '').trim(); }
          ).filter(Boolean).join('、');
          if (cells) items.push({ text: cells, voiceType: 'female', block: row, sentenceId: null });
        });
        return;
      }

      // リスト: li ごとにセンテンス wrap
      if (block.tagName === 'UL' || block.tagName === 'OL') {
        Array.prototype.forEach.call(block.querySelectorAll('li'), function (li) {
          var sList = wrapTextNodesIntoSentences(li);
          sList.forEach(function (s) {
            items.push({ text: s.text, voiceType: 'female', block: li, sentenceId: s.id });
          });
        });
        return;
      }

      // 見出し・段落・disclaimer・blockquote 等 → センテンス wrap
      var sList2 = wrapTextNodesIntoSentences(block);
      sList2.forEach(function (s) {
        items.push({ text: s.text, voiceType: 'female', block: block, sentenceId: s.id });
      });
    });

    return items;
  }

  // ---- ハイライト管理 ----
  function clearAllHighlights() {
    var els = article.querySelectorAll('.tts-sentence.tts-reading, tr.tts-reading');
    Array.prototype.forEach.call(els, function (el) { el.classList.remove('tts-reading'); });
  }

  // ハイライト中の要素が「ウィジェットに被らない安全領域」内に来るよう自動スクロール。
  // 安全領域 = 上部の余白 〜 ウィジェット上端の少し上まで。
  // 既に安全領域内にある場合は何もしない（ジッター回避）。
  function smartScroll(el) {
    if (!el || !el.getBoundingClientRect) return;
    var rect = el.getBoundingClientRect();
    var vh = window.innerHeight || document.documentElement.clientHeight;

    // ウィジェットが画面下を占有している分を控除して、安全領域を計算
    var widgetTop = vh; // デフォルト: ウィジェットなし → ビューポート全部使える
    if (widget) {
      var wRect = widget.getBoundingClientRect();
      if (wRect && wRect.height > 0) widgetTop = wRect.top;
    }
    var safeTop = vh * 0.12;          // 上端から 12% は読み手の文脈用に余白
    var safeBottom = widgetTop - 16;  // ウィジェット上端 - 16px マージン
    if (safeBottom <= safeTop) safeBottom = vh; // 安全領域が確保できない場合のフォールバック
    var safeHeight = safeBottom - safeTop;

    // 既に安全領域内ならスクロールしない（ジッター回避）
    if (rect.top >= safeTop && rect.bottom <= safeBottom) return;

    // 要素のサイズに応じて目標位置を計算
    var targetTop;
    if (rect.height >= safeHeight) {
      // 要素が安全領域より大きい場合は top を safeTop に合わせる
      targetTop = safeTop;
    } else {
      // 安全領域内のやや上寄りに配置（カラオケ風: 次の文に視線が移しやすい位置）
      targetTop = safeTop + (safeHeight - rect.height) * 0.3;
    }

    var deltaY = rect.top - targetTop;
    if (Math.abs(deltaY) < 4) return; // ごく小さな差分はスクロールしない
    try {
      window.scrollBy({ top: deltaY, behavior: 'smooth' });
    } catch (e) {
      window.scrollBy(0, deltaY);
    }
  }

  function highlightItem(item) {
    clearAllHighlights();
    if (item.sentenceId !== null && item.sentenceId !== undefined) {
      // センテンス単位ハイライト（インライン要素を跨ぐ場合は複数 span）
      var spans = article.querySelectorAll('[data-tts-sentence-id="' + item.sentenceId + '"]');
      Array.prototype.forEach.call(spans, function (s) { s.classList.add('tts-reading'); });
      if (spans.length > 0) smartScroll(spans[0]);
    } else if (item.block) {
      // テーブル行など、ブロック単位ハイライト
      item.block.classList.add('tts-reading');
      smartScroll(item.block);
    }
  }

  // ---- Voice 選択（高品質を優先） ----
  function selectVoices() {
    var all = speechSynthesis.getVoices() || [];
    var jp = all.filter(function (v) { return v.lang && v.lang.toLowerCase().indexOf('ja') === 0; });
    if (jp.length === 0) return;

    // 品質スコア降順でソート（同スコア内は元の getVoices() 順を維持）
    jp.sort(function (a, b) { return scoreVoiceQuality(b) - scoreVoiceQuality(a); });

    // 品質ソート済の jp を上から舐めて、最初に pattern にマッチした voice を返す
    // → 同じ voice 名でも高品質バリアントが優先される
    function findByPatterns(patterns) {
      for (var i = 0; i < jp.length; i++) {
        var name = (jp[i].name || '').toLowerCase();
        for (var j = 0; j < patterns.length; j++) {
          if (name.indexOf(patterns[j].toLowerCase()) >= 0) return jp[i];
        }
      }
      return null;
    }

    voices.female = findByPatterns(JP_FEMALE_PATTERNS) || jp[0];
    voices.male = findByPatterns(JP_MALE_PATTERNS)
      || (function () {
           for (var k = 0; k < jp.length; k++) if (jp[k] !== voices.female) return jp[k];
           return jp[0];
         })();
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

    // センテンス／ブロック単位でハイライト＆スマートスクロール
    highlightItem(item);

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
    clearAllHighlights();
    updateUI();
  }

  function skipNextSection() {
    // 現在位置以降で最初の <h2> ブロックに紐付くキュー要素を探す
    for (var i = position + 1; i < queue.length; i++) {
      var el = queue[i].block;
      if (el && el.tagName === 'H2') {
        position = i;
        try { speechSynthesis.cancel(); } catch (e) {}
        if (isPlaying && !isPaused) {
          setTimeout(playFromCurrent, 50);
        } else {
          // 停止中ならハイライトだけ移動
          highlightItem(queue[i]);
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
