/* 共通サイトナビのハンバーガー化（スマホ）。
 *
 * 全ページ共通の <header class="site-header"> 内 <nav class="site-nav"> を、
 * スマホ幅ではドロップダウン式のハンバーガーメニューに昇格させる。
 *
 * 設計（プログレッシブ・エンハンスメント）:
 *   - JS 無効時: CSS 側のフォールバックで「1行横スクロールのナビ」が出る（崩れない）
 *   - JS 有効時: <html> に .js を付け、ハンバーガーボタンを動的に挿入。
 *               CSS の `html.js`（≤600px）ルールでドロップダウンに切り替わる。
 *
 * map.html のハンバーガー挙動（外側クリック / Escape で閉じる）を踏襲。
 * ヘッダー markup は各ページで複製されているため、ボタンは DOM 生成して
 * 各ページの HTML には手を入れない方針（このファイル + script タグ1行のみ）。
 *
 * 2026-06 ファーストビュー最適化の一環。
 */
(function () {
  document.documentElement.classList.add('js');

  function init() {
    var inner = document.querySelector('.site-header__inner');
    var nav = inner && inner.querySelector('.site-nav');
    if (!inner || !nav) return;
    if (!nav.id) nav.id = 'site-nav';

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'nav-toggle';
    btn.setAttribute('aria-label', 'メニュー');
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-controls', nav.id);
    btn.textContent = '☰'; /* ☰ */
    inner.appendChild(btn);

    var isOpen = function () { return nav.classList.contains('open'); };
    var open = function () { nav.classList.add('open'); btn.setAttribute('aria-expanded', 'true'); };
    var close = function () { nav.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); };

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      isOpen() ? close() : open();
    });

    /* メニュー外クリックで閉じる */
    document.addEventListener('click', function (e) {
      if (!isOpen()) return;
      if (nav.contains(e.target) || btn.contains(e.target)) return;
      close();
    });

    /* Escape で閉じてボタンにフォーカスを戻す（a11y） */
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isOpen()) { close(); btn.focus(); }
    });

    /* ナビ内リンクをタップしたら閉じる（遷移時の体感を整える） */
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) close();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
