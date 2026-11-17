---
layout: default
title: "概览"
description: "每日追踪 GitHub 热门实用开源项目，当前收录 226 个项目，附 DeepSeek 每日用量统计。"
nav_active: index
---

<section class="hero hero--collage" data-enter aria-labelledby="hero-h">
  <div class="wrap">
    <div class="hero-text grid hero__grid">
      <div class="hero__text span-5">
        <p class="hero-notice">北京时间 <b>2026-11-18 01:19</b> 同步 · 今日 API 花费 <b>¥0.0562</b></p>
        <h1 id="hero-h">GitHub 热门开源项目 每日筛选雷达</h1>
        <p class="hero__lead">每日自动抓取 GitHub Trending 与高星新仓，通过四维权重模型剔除刷星与空壳仓库，再由 DeepSeek 生成中文简介与分类。</p>
        <div class="btn-row">
          <a class="btn btn--primary" href="rising.html">查看本周增速榜<svg class="m-arrow" viewBox="0 0 12 12" aria-hidden="true"><path class="m-arrow__stem" d="M1 6h8"/><path class="m-arrow__head" d="M4.5 2.5 8 6l-3.5 3.5"/></svg></a>
          <a class="btn btn--secondary" href="new.html">7 日新收录</a>
        </div>
        <dl class="hero-facts">
          <div><dt>已收录项目</dt><dd data-m-count>226</dd></div>
          <div><dt>追踪仓库</dt><dd data-m-count>245</dd></div>
          <div><dt>累计 API 花费</dt><dd class="mono-num">¥0.2119</dd></div>
        </dl>
      </div>
      <div class="hero__art span-6 start-7" role="img" aria-label="GitHub 热门项目雷达的增速榜界面与四维评分卡片">
        <div class="ly-piece ly-piece--main d-win" aria-hidden="true">
          <div class="d-win__bar"><span class="d-win__dots"><i></i><i></i><i></i></span><span>gh-radar · 本周增速快照</span></div>
          <div class="d-win__body">
            <div class="d-side">
              <span><i></i>概览</span>
              <span class="is-on"><i></i>本周增速</span>
              <span><i></i>7 日新仓</span>
              <span><i></i>每日 Usage</span>
              <span class="d-side__label">热门分类</span>
              <span><i></i>AI / Agent</span>
              <span><i></i>开发工具</span>
              <span><i></i>后端框架</span>
            </div>
            <div class="d-main">
              <div class="d-main__head"><h4>本周增速 Top 30</h4><span class="d-btn">共 226 项</span></div>
              <div class="d-tabs"><span class="is-on">7日增量</span><span>综合评分 ≥55</span><span>高分 ≥85</span></div>
              <div class="d-rows"><div class="d-row"><span class="d-thumb" aria-hidden="true">KI</span><div><b>libracoder/kiri</b><small>Rust · ⭐ 9.5k</small></div><span class="num">+14.3k</span><span class="d-chip">85 分</span></div><div class="d-row"><span class="d-thumb" aria-hidden="true">CR</span><div><b>storytold/craft-anything</b><small>Rust · ⭐ 35.2k</small></div><span class="num">+10.0k</span><span class="d-chip">76 分</span></div><div class="d-row"><span class="d-thumb" aria-hidden="true">UN</span><div><b>dream-num/univer</b><small>TypeScript · ⭐ 28.6k</small></div><span class="num">+9.8k</span><span class="d-chip">89 分</span></div><div class="d-row"><span class="d-thumb" aria-hidden="true">AS</span><div><b>meta/astryx</b><small>TypeScript · ⭐ 29.9k</small></div><span class="num">+8.8k</span><span class="d-chip">96 分</span></div><div class="d-row"><span class="d-thumb" aria-hidden="true">T3</span><div><b>pingdotgg/t3code</b><small>TypeScript · ⭐ 63.3k</small></div><span class="num">+8.6k</span><span class="d-chip">97 分</span></div></div>
            </div>
          </div>
        </div>
        <div class="ly-piece ly-piece--note d-card" aria-hidden="true" data-ly-steps="700">
          <div class="d-card__row"><h5>四维准入校验</h5><span class="d-chip" data-step data-step-at="4">已收录</span></div>
          <div class="d-note__line" data-step><i>✓</i><span><b>增速权重 35%</b> · 排除单日暴涨噪音</span></div>
          <div class="d-note__line" data-step><i>✓</i><span><b>健康与活跃 45%</b> · 连续 45 天快照</span></div>
          <div class="d-note__line" data-step><i>✓</i><span><b>DeepSeek Flash</b> · 单仓库仅分析一次</span></div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section ground-surface" id="features" aria-labelledby="features-h">
  <div class="wrap">
    <div class="section-head section-head--split">
      <div>
        <h2 id="features-h">三段式自动采集管线。<span class="muted">先滤刷星再出简介</span></h2>
        <p>每日自动同步、防刷星评分与中文摘要，历史结果永久缓存。</p>
      </div>
      <a class="link" href="new.html">查看 7 日新收录</a>
    </div>
    <div class="grid grid--top">
      <div class="span-5 stack-5">
        <div class="radar-feature-list">
          <div class="radar-feature-item"><strong>硬过滤前置</strong><span class="muted">排除 Fork、归档与文档过短的空壳仓库</span></div>
          <div class="radar-feature-item"><strong>缓存优先分析</strong><span class="muted">仅对新增项目调用 DeepSeek，历史不重复扣费</span></div>
          <div class="radar-feature-item"><strong>公开账单核验</strong><span class="muted">每日 Usage 简表与 JSON 同步提交至仓库</span></div>
        </div>
      </div>
      <div class="panel span-6 start-7">
        <div class="dg" data-diagram='{&quot;layout&quot;: &quot;bowtie&quot;, &quot;alt&quot;: &quot;GitHub Trending 日榜、周榜与 30 天高星新仓汇入四维过滤引擎，经 DeepSeek Flash 分类与摘要后生成 12 个技术分类与每日 Usage 账单。&quot;, &quot;sources&quot;: [{&quot;label&quot;: &quot;Trending 日榜&quot;, &quot;icon&quot;: &quot;github&quot;, &quot;sub&quot;: &quot;每日热榜&quot;}, {&quot;label&quot;: &quot;Trending 周榜&quot;, &quot;icon&quot;: &quot;ui:trending-up&quot;, &quot;sub&quot;: &quot;7日增量&quot;}, {&quot;label&quot;: &quot;高星新仓&quot;, &quot;icon&quot;: &quot;ui:star&quot;, &quot;sub&quot;: &quot;30天 &gt;300⭐&quot;}], &quot;core&quot;: {&quot;label&quot;: &quot;四维评分引擎&quot;, &quot;icon&quot;: &quot;ui:funnel&quot;}, &quot;targets&quot;: [{&quot;label&quot;: &quot;DeepSeek Flash&quot;, &quot;icon&quot;: &quot;ui:cpu&quot;, &quot;sub&quot;: &quot;中文摘要&quot;}, {&quot;label&quot;: &quot;12 个主分类&quot;, &quot;icon&quot;: &quot;ui:layers&quot;, &quot;sub&quot;: &quot;结构归档&quot;}, {&quot;label&quot;: &quot;每日 Usage&quot;, &quot;icon&quot;: &quot;ui:chart-column&quot;, &quot;sub&quot;: &quot;账单透明&quot;}]}'></div>
      </div>
    </div>
  </div>
</section>

<section class="section ground-inverse" id="workflow" aria-labelledby="workflow-h" style="--hm: 2">
  <div class="wrap">
    <div class="section-head section-head--split">
      <div>
        <h2 id="workflow-h">四维权重评分模型。<span class="muted">用近 45 天数据剔除短时刷星</span></h2>
        <p>对近 45 天 Star 曲线与项目维护状态建立定量评估，55 分准入线过滤纯宣传页或脉冲刷榜项目。</p>
      </div>
      <a class="link" href="rising.html">浏览评分榜单</a>
    </div>
    <div class="radar-weight-grid">
      <div class="radar-weight-card">
        <div class="radar-weight-top"><p class="t-stat">35%</p><h3>7 日 Star 增速</h3></div>
        <p>计算最近 7 天真实增量，衡量社区短期关注度而非历史包袱。</p>
        <div class="radar-weight-foot mono-num">单日增量 &gt;80% 直接扣 10 分</div>
        <svg class="radar-weight-svg" viewBox="0 0 260 216" fill="none" role="img" aria-hidden="true"><rect x="22" y="148" width="20" height="34" rx="5" fill="var(--accent)" fill-opacity="0.35"/><rect x="54" y="134" width="20" height="48" rx="5" fill="var(--accent)" fill-opacity="0.45"/><rect x="86" y="120" width="20" height="62" rx="5" fill="var(--accent)" fill-opacity="0.55"/><rect x="118" y="108" width="20" height="74" rx="5" fill="var(--accent)" fill-opacity="0.65"/><rect x="150" y="86" width="20" height="96" rx="5" fill="var(--accent)" fill-opacity="0.75"/><rect x="182" y="64" width="20" height="118" rx="5" fill="var(--accent)" fill-opacity="0.85"/><rect x="214" y="38" width="20" height="144" rx="5" fill="var(--accent)" fill-opacity="0.95"/><line x1="16" y1="62" x2="244" y2="62" stroke="currentColor" stroke-opacity="0.28" stroke-dasharray="4 4" stroke-width="1.5"/><text x="20" y="28" fill="currentColor" font-size="11" font-family="var(--font-mono)" opacity="0.7">7D VELOCITY · CAP 80%</text></svg>
      </div>
      <div class="radar-weight-card">
        <div class="radar-weight-top"><p class="t-stat">25%</p><h3>仓库健康度</h3></div>
        <p>检查开源协议、文档篇幅与贡献者结构，过滤空壳项目。</p>
        <div class="radar-weight-foot mono-num">建库 &lt;7 天且单人提交扣 15 分</div>
        <svg class="radar-weight-svg" viewBox="0 0 260 216" fill="none" role="img" aria-hidden="true"><text x="20" y="28" fill="currentColor" font-size="11" font-family="var(--font-mono)" opacity="0.7">HEALTH GATES</text><text x="20" y="64" fill="currentColor" font-size="12" opacity="0.82">README &gt;= 200c</text><rect x="20" y="74" width="220" height="14" rx="7" fill="currentColor" fill-opacity="0.08"/><rect x="20" y="74" width="204" height="14" rx="7" fill="var(--accent)"/><text x="20" y="116" fill="currentColor" font-size="12" opacity="0.82">License &amp; Docs</text><rect x="20" y="126" width="220" height="14" rx="7" fill="currentColor" fill-opacity="0.08"/><rect x="20" y="126" width="178" height="14" rx="7" fill="var(--accent)" fill-opacity="0.82"/><text x="20" y="168" fill="currentColor" font-size="12" opacity="0.82">Contributors</text><rect x="20" y="178" width="220" height="14" rx="7" fill="currentColor" fill-opacity="0.08"/><rect x="20" y="178" width="146" height="14" rx="7" fill="var(--accent)" fill-opacity="0.65"/></svg>
      </div>
      <div class="radar-weight-card">
        <div class="radar-weight-top"><p class="t-stat">20%</p><h3>持续演进力</h3></div>
        <p>追踪连续 45 天历史快照变化与最近提交，剔除停更项目。</p>
        <div class="radar-weight-foot mono-num">滚动保留 45 天增量快照序列</div>
        <svg class="radar-weight-svg" viewBox="0 0 260 216" fill="none" role="img" aria-hidden="true"><text x="20" y="28" fill="currentColor" font-size="11" font-family="var(--font-mono)" opacity="0.7">45D SNAPSHOT WINDOW</text><polygon points="22,190 22,174 58,162 94,146 130,128 166,98 202,78 238,50 238,190" fill="var(--accent)" fill-opacity="0.14"/><polyline points="22,174 58,162 94,146 130,128 166,98 202,78 238,50" stroke="var(--accent)" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/><circle cx="22" cy="174" r="4.5" fill="var(--accent)"/><circle cx="58" cy="162" r="4.5" fill="var(--accent)"/><circle cx="94" cy="146" r="4.5" fill="var(--accent)"/><circle cx="130" cy="128" r="4.5" fill="var(--accent)"/><circle cx="166" cy="98" r="4.5" fill="var(--accent)"/><circle cx="202" cy="78" r="4.5" fill="var(--accent)"/><circle cx="238" cy="50" r="4.5" fill="var(--accent)"/><line x1="20" y1="190" x2="240" y2="190" stroke="currentColor" stroke-opacity="0.16" stroke-width="1.5"/></svg>
      </div>
      <div class="radar-weight-card">
        <div class="radar-weight-top"><p class="t-stat">20%</p><h3>可运行实用性</h3></div>
        <p>结合形态标签、安装命令与模型摘要，保留即开即用工具。</p>
        <div class="radar-weight-foot mono-num">综合评分 ≥55 分方可入榜</div>
        <svg class="radar-weight-svg" viewBox="0 0 260 216" fill="none" role="img" aria-hidden="true"><text x="20" y="28" fill="currentColor" font-size="11" font-family="var(--font-mono)" opacity="0.7">PRACTICALITY SCORE &gt;= 55</text><rect x="20" y="56" width="104" height="38" rx="8" fill="currentColor" fill-opacity="0.06" stroke="currentColor" stroke-opacity="0.16"/><text x="72" y="79" text-anchor="middle" fill="currentColor" font-size="12" font-weight="500">CLI 工具</text><rect x="136" y="56" width="104" height="38" rx="8" fill="currentColor" fill-opacity="0.06" stroke="currentColor" stroke-opacity="0.16"/><text x="188" y="79" text-anchor="middle" fill="currentColor" font-size="12" font-weight="500">Agent</text><rect x="20" y="108" width="104" height="38" rx="8" fill="currentColor" fill-opacity="0.06" stroke="currentColor" stroke-opacity="0.16"/><text x="72" y="131" text-anchor="middle" fill="currentColor" font-size="12" font-weight="500">Web 应用</text><rect x="136" y="108" width="104" height="38" rx="8" fill="currentColor" fill-opacity="0.06" stroke="currentColor" stroke-opacity="0.16"/><text x="188" y="131" text-anchor="middle" fill="currentColor" font-size="12" font-weight="500">SDK / 库</text><rect x="20" y="164" width="220" height="32" rx="8" fill="var(--accent)" fill-opacity="0.16"/><text x="130" y="184" text-anchor="middle" fill="var(--accent)" font-size="12" font-weight="600">DeepSeek 中文功能摘要</text></svg>
      </div>
    </div>
  </div>
</section>

<section class="section ground-base" id="statement" aria-label="开源雷达筛选原则">
  <div class="wrap">
    <div data-moment="liquid-type" class="section-head" style="max-width:none">
      <h2 class="mo-lt__type radar-statement">开源热榜过滤刷星噪音 只留可用工具</h2>
      <p>好项目不该埋没在脉冲刷榜与营销文宣里。每项收录结果均经过 45 天曲线复核，并支持全站分类索引、关键词检索与多列数值排序。</p>
    </div>
    <div class="radar-statement-grid">
      <div class="radar-statement-card">
        <span class="radar-weight-icon" aria-hidden="true"><svg class="radar-icon" width="24" height="24" viewBox="0 0 256 256" fill="none" aria-hidden="true"><circle cx="128" cy="128" r="96" stroke="currentColor" stroke-width="18"/><path d="M128 72V128L168 152" stroke="currentColor" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
        <h3>45 天滚动快照追踪</h3>
        <p>持续保存每日 Star 增量与提交时间戳，不依赖单日 Trending 瞬时榜单做收录决策。</p>
      </div>
      <div class="radar-statement-card">
        <span class="radar-weight-icon" aria-hidden="true"><svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><rect x="48" y="48" width="160" height="160" rx="16" stroke="currentColor" stroke-width="18"/><rect x="92" y="92" width="72" height="72" rx="8" stroke="currentColor" stroke-width="18"/><path d="M96 48V24M160 48V24M96 232V208M160 232V208M48 96H24M48 160H24M232 96H208M232 160H208" stroke="currentColor" stroke-width="18" stroke-linecap="round"/></svg></span>
        <h3>12 个领域与形态归档</h3>
        <p>由 DeepSeek Flash 自动生成一句话中文简介，并区分 CLI、Agent、库与完整应用形态。</p>
      </div>
      <div class="radar-statement-card">
        <span class="radar-weight-icon" aria-hidden="true"><svg class="radar-icon" width="24" height="24" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M232 56L136 152L96 112L24 184" stroke="currentColor" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/><path d="M232 120V56H168" stroke="currentColor" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
        <h3>每日 API 账单可查</h3>
        <p>所有大模型 Token 消耗与人民币花费按天公开于首页与 JSON 文件，杜绝隐藏成本。</p>
      </div>
    </div>
  </div>
</section>

<section class="section ground-surface" id="categories" aria-labelledby="categories-h">
  <div class="wrap">
    <div class="grid grid--top">
      <div class="span-5 radar-split-copy">
        <h2 id="categories-h">12 个技术分类索引</h2>
        <p>当前共收录 226 个开源项目，点击任意领域直接查看对应子分类与评分排名。</p>
        <div class="radar-cat-list"><div class="radar-cat-item"><a class="radar-cat-row" href="categories/ai.html"><svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><rect x="48" y="48" width="160" height="160" rx="16" stroke="currentColor" stroke-width="18"/><rect x="92" y="92" width="72" height="72" rx="8" stroke="currentColor" stroke-width="18"/><path d="M96 48V24M160 48V24M96 232V208M160 232V208M48 96H24M48 160H24M232 96H208M232 160H208" stroke="currentColor" stroke-width="18" stroke-linecap="round"/></svg><span>AI</span></a><span class="radar-cat-row-count mono-num">107</span></div><div class="radar-cat-item"><a class="radar-cat-row" href="categories/devtools.html"><svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><rect x="32" y="48" width="192" height="160" rx="16" stroke="currentColor" stroke-width="18"/><path d="M72 96L108 128L72 160M124 160H176" stroke="currentColor" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/></svg><span>开发工具</span></a><span class="radar-cat-row-count mono-num">12</span></div><div class="radar-cat-item"><a class="radar-cat-row" href="categories/frontend.html"><svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><rect x="32" y="48" width="192" height="160" rx="16" stroke="currentColor" stroke-width="18"/><path d="M32 104H224M104 104V208" stroke="currentColor" stroke-width="18"/></svg><span>前端</span></a><span class="radar-cat-row-count mono-num">9</span></div><div class="radar-cat-item"><a class="radar-cat-row" href="categories/backend.html"><svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M128 32L216 80V176L128 224L40 176V80L128 32Z" stroke="currentColor" stroke-width="18" stroke-linejoin="round"/><path d="M40 80L128 128L216 80M128 128V224" stroke="currentColor" stroke-width="18" stroke-linejoin="round"/></svg><span>后端</span></a><span class="radar-cat-row-count mono-num">3</span></div><div class="radar-cat-item"><a class="radar-cat-row" href="categories/data.html"><svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><ellipse cx="128" cy="68" rx="80" ry="32" stroke="currentColor" stroke-width="18"/><path d="M48 68V188C48 205.7 83.8 220 128 220C172.2 220 208 205.7 208 188V68" stroke="currentColor" stroke-width="18"/><path d="M48 128C48 145.7 83.8 160 128 160C172.2 160 208 145.7 208 128" stroke="currentColor" stroke-width="18"/></svg><span>数据</span></a><span class="radar-cat-row-count mono-num">2</span></div><div class="radar-cat-item"><a class="radar-cat-row" href="categories/ops.html"><svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M76 196H188C210.1 196 228 178.1 228 156C228 135.4 212.5 118.4 192.5 116.2C186.1 84.3 158 60 124 60C86.4 60 56 90.4 56 128C56 130.7 56.2 133.4 56.5 136C39.2 139.5 26 154.8 26 173C26 185.7 36.3 196 49 196H76Z" stroke="currentColor" stroke-width="18" stroke-linejoin="round"/></svg><span>运维与云原生</span></a><span class="radar-cat-row-count mono-num">6</span></div><div class="radar-cat-item"><a class="radar-cat-row" href="categories/security.html"><svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M48 56L128 32L208 56V120C208 172 172 208 128 224C84 208 48 172 48 120V56Z" stroke="currentColor" stroke-width="18" stroke-linejoin="round"/></svg><span>安全</span></a><span class="radar-cat-row-count mono-num">12</span></div><div class="radar-cat-item"><a class="radar-cat-row" href="categories/productivity.html"><svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M144 24L48 144H128L112 232L208 112H128L144 24Z" stroke="currentColor" stroke-width="18" stroke-linejoin="round"/></svg><span>效率与自托管</span></a><span class="radar-cat-row-count mono-num">9</span></div><div class="radar-cat-item"><a class="radar-cat-row" href="categories/media.html"><svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><rect x="32" y="48" width="192" height="160" rx="16" stroke="currentColor" stroke-width="18"/><path d="M104 96L164 128L104 160V96Z" stroke="currentColor" stroke-width="18" stroke-linejoin="round"/></svg><span>多媒体</span></a><span class="radar-cat-row-count mono-num">16</span></div><div class="radar-cat-item"><a class="radar-cat-row" href="categories/apps.html"><svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><rect x="64" y="28" width="128" height="200" rx="16" stroke="currentColor" stroke-width="18"/><path d="M112 192H144" stroke="currentColor" stroke-width="18" stroke-linecap="round"/></svg><span>移动与桌面</span></a><span class="radar-cat-row-count mono-num">20</span></div><div class="radar-cat-item"><a class="radar-cat-row" href="categories/learning.html"><svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M48 48H112C120.8 48 128 55.2 128 64V208C128 199.2 120.8 192 112 192H48V48Z" stroke="currentColor" stroke-width="18" stroke-linejoin="round"/><path d="M208 48H144C135.2 48 128 55.2 128 64V208C128 199.2 135.2 192 144 192H208V48Z" stroke="currentColor" stroke-width="18" stroke-linejoin="round"/></svg><span>学习资源</span></a><span class="radar-cat-row-count mono-num">8</span></div><div class="radar-cat-item"><a class="radar-cat-row" href="categories/other.html"><svg class="radar-icon" width="18" height="18" viewBox="0 0 256 256" fill="none" aria-hidden="true"><path d="M128 32L216 80V176L128 224L40 176V80L128 32Z" stroke="currentColor" stroke-width="18" stroke-linejoin="round"/><path d="M40 80L128 128L216 80M128 128V224" stroke="currentColor" stroke-width="18" stroke-linejoin="round"/></svg><span>其他</span></a><span class="radar-cat-row-count mono-num">22</span></div></div>
      </div>
      <div class="panel radar-cat-panel span-6 start-7">
        <svg class="radar-cat-svg" viewBox="0 0 540 520" fill="none" role="img" aria-label="各技术领域收录项目数量分布柱状图"><text x="16" y="24" fill="currentColor" font-size="13" font-weight="600" opacity="0.8">主要技术领域项目分布（Top 10）</text><text x="16" y="66" fill="currentColor" font-size="13" font-weight="500">AI</text><rect x="132" y="52" width="290" height="18" rx="9" fill="currentColor" fill-opacity="0.08"/><rect x="132" y="52" width="290" height="18" rx="9" fill="var(--accent)" fill-opacity="0.92"/><text x="436" y="66" fill="currentColor" font-size="12" font-family="var(--font-mono)">107 (47.3%)</text><text x="16" y="112" fill="currentColor" font-size="13" font-weight="500">其他</text><rect x="132" y="98" width="290" height="18" rx="9" fill="currentColor" fill-opacity="0.08"/><rect x="132" y="98" width="60" height="18" rx="9" fill="var(--accent)" fill-opacity="0.87"/><text x="436" y="112" fill="currentColor" font-size="12" font-family="var(--font-mono)">22 (9.7%)</text><text x="16" y="158" fill="currentColor" font-size="13" font-weight="500">移动与桌面</text><rect x="132" y="144" width="290" height="18" rx="9" fill="currentColor" fill-opacity="0.08"/><rect x="132" y="144" width="54" height="18" rx="9" fill="var(--accent)" fill-opacity="0.82"/><text x="436" y="158" fill="currentColor" font-size="12" font-family="var(--font-mono)">20 (8.8%)</text><text x="16" y="204" fill="currentColor" font-size="13" font-weight="500">多媒体</text><rect x="132" y="190" width="290" height="18" rx="9" fill="currentColor" fill-opacity="0.08"/><rect x="132" y="190" width="43" height="18" rx="9" fill="var(--accent)" fill-opacity="0.77"/><text x="436" y="204" fill="currentColor" font-size="12" font-family="var(--font-mono)">16 (7.1%)</text><text x="16" y="250" fill="currentColor" font-size="13" font-weight="500">安全</text><rect x="132" y="236" width="290" height="18" rx="9" fill="currentColor" fill-opacity="0.08"/><rect x="132" y="236" width="33" height="18" rx="9" fill="var(--accent)" fill-opacity="0.72"/><text x="436" y="250" fill="currentColor" font-size="12" font-family="var(--font-mono)">12 (5.3%)</text><text x="16" y="296" fill="currentColor" font-size="13" font-weight="500">开发工具</text><rect x="132" y="282" width="290" height="18" rx="9" fill="currentColor" fill-opacity="0.08"/><rect x="132" y="282" width="33" height="18" rx="9" fill="var(--accent)" fill-opacity="0.67"/><text x="436" y="296" fill="currentColor" font-size="12" font-family="var(--font-mono)">12 (5.3%)</text><text x="16" y="342" fill="currentColor" font-size="13" font-weight="500">前端</text><rect x="132" y="328" width="290" height="18" rx="9" fill="currentColor" fill-opacity="0.08"/><rect x="132" y="328" width="24" height="18" rx="9" fill="var(--accent)" fill-opacity="0.62"/><text x="436" y="342" fill="currentColor" font-size="12" font-family="var(--font-mono)">9 (4.0%)</text><text x="16" y="388" fill="currentColor" font-size="13" font-weight="500">效率与自托管</text><rect x="132" y="374" width="290" height="18" rx="9" fill="currentColor" fill-opacity="0.08"/><rect x="132" y="374" width="24" height="18" rx="9" fill="var(--accent)" fill-opacity="0.57"/><text x="436" y="388" fill="currentColor" font-size="12" font-family="var(--font-mono)">9 (4.0%)</text><text x="16" y="434" fill="currentColor" font-size="13" font-weight="500">学习资源</text><rect x="132" y="420" width="290" height="18" rx="9" fill="currentColor" fill-opacity="0.08"/><rect x="132" y="420" width="22" height="18" rx="9" fill="var(--accent)" fill-opacity="0.52"/><text x="436" y="434" fill="currentColor" font-size="12" font-family="var(--font-mono)">8 (3.5%)</text><text x="16" y="480" fill="currentColor" font-size="13" font-weight="500">运维与云原生</text><rect x="132" y="466" width="290" height="18" rx="9" fill="currentColor" fill-opacity="0.08"/><rect x="132" y="466" width="16" height="18" rx="9" fill="var(--accent)" fill-opacity="0.47"/><text x="436" y="480" fill="currentColor" font-size="12" font-family="var(--font-mono)">6 (2.7%)</text></svg>
      </div>
    </div>
  </div>
</section>

<section class="section ground-base" id="usage" aria-labelledby="usage-h" markdown="1">
  <div class="wrap" markdown="1">
    <div class="grid grid--top" markdown="1">
      <div class="span-5 radar-split-copy">
        <h2 id="usage-h">DeepSeek 每日 Usage 与花费</h2>
        <p>仅保留每日总 Tokens 与人民币花费，数据来源于模型接口实际返回值，历史结果永久缓存。</p>
        <div class="radar-usage-mini">
          <div class="radar-usage-mini-item"><span>已计费分类</span><strong class="mono-num">24 次</strong></div>
          <div class="radar-usage-mini-item"><span>Prompt 缓存命中</span><strong class="mono-num">18.7%</strong></div>
        </div>
        <div class="btn-row"><a class="btn btn--secondary btn--sm" href="usage.html">查看全部日期</a></div>
      </div>
      <div class="span-6 start-7 radar-usage-panel" markdown="1">
        <div class="radar-usage-ledger ui ui-ledger" markdown="1">
          <div class="radar-usage-ledger-head"><span>近 7 日 DeepSeek 用量趋势</span><span class="mono-num">累计 ¥0.2119</span></div>
          <svg class="radar-usage-svg" viewBox="0 0 520 176" fill="none" role="img" aria-label="近 7 日 DeepSeek Token 消耗趋势柱状图"><rect x="55.0" y="20" width="44" height="112" rx="6" fill="currentColor" fill-opacity="0.06"/><rect x="55.0" y="24" width="44" height="108" rx="6" fill="var(--accent)"/><text x="77.0" y="156" text-anchor="middle" fill="currentColor" font-size="11" font-family="var(--font-mono)" opacity="0.72">11-14</text><rect x="177.0" y="20" width="44" height="112" rx="6" fill="currentColor" fill-opacity="0.06"/><rect x="177.0" y="57" width="44" height="75" rx="6" fill="var(--accent)"/><text x="199.0" y="156" text-anchor="middle" fill="currentColor" font-size="11" font-family="var(--font-mono)" opacity="0.72">11-15</text><rect x="299.0" y="20" width="44" height="112" rx="6" fill="currentColor" fill-opacity="0.06"/><rect x="299.0" y="29" width="44" height="103" rx="6" fill="var(--accent)"/><text x="321.0" y="156" text-anchor="middle" fill="currentColor" font-size="11" font-family="var(--font-mono)" opacity="0.72">11-16</text><rect x="421.0" y="20" width="44" height="112" rx="6" fill="currentColor" fill-opacity="0.06"/><rect x="421.0" y="20" width="44" height="112" rx="6" fill="var(--accent)"/><text x="443.0" y="156" text-anchor="middle" fill="currentColor" font-size="11" font-family="var(--font-mono)" opacity="0.72">11-17</text></svg>
          <div class="radar-table-wrap" markdown="1">

| 日期 | 总 Tokens | 花费 (¥) |
|---|---|---|
| 2026-11-17 | 25,933 | ¥0.0562 |
| 2026-11-16 | 23,740 | ¥0.0575 |
| 2026-11-15 | 17,276 | ¥0.0367 |
| 2026-11-14 | 24,914 | ¥0.0614 |

          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section ground-surface" id="faq" aria-labelledby="faq-h">
  <div class="wrap">
    <div class="grid grid--top">
      <div class="span-5 radar-split-copy">
        <h2 id="faq-h">开源雷达常见问题</h2>
        <p>关于四维筛选规则、DeepSeek 计费统计与自部署的完整说明。</p>
        <div class="radar-faq-badge"><span class="radar-weight-icon" aria-hidden="true"><svg class="radar-icon" width="28" height="28" viewBox="0 0 256 256" fill="none" aria-hidden="true"><circle cx="128" cy="128" r="96" stroke="currentColor" stroke-width="18"/><path d="M100 100A28 28 0 1 1 136 126.8C128 131.6 128 136 128 144" stroke="currentColor" stroke-width="18" stroke-linecap="round"/><circle cx="128" cy="180" r="10" fill="currentColor"/></svg></span><p class="t-small muted">采集脚本、评分权重、每日快照与 DeepSeek Usage 均提交于 GitHub 仓库，全流程透明可复现。</p></div>
      </div>
      <div class="span-6 start-7"><div class="faq"><div class="faq__item"><h3>开源雷达每天什么时候同步并刷新榜单？</h3><p>GitHub Actions 每天北京时间 09:17 至 23:17 检查一次，首次发布成功后当天跳过重复时段。</p></div><div class="faq__item"><h3>四维评分模型如何避免刷星仓库上榜？</h3><p>单日 Star 增量占 7 日 80% 以上扣 10 分，建库不足 7 天且单人提交扣 15 分，空壳仓库直接排除。</p></div><div class="faq__item"><h3>DeepSeek 每日 Usage 数字是估算还是真实返回？</h3><p>统计值直接读取 DeepSeek API 返回的 total_tokens 并按单价折算，历史项目永久缓存不重复扣费。</p></div><div class="faq__item"><h3>开源雷达如何使用 overrides.yaml 自定义分类？</h3><p>编辑 overrides.yaml 可覆盖分类或置顶；Fork 后启用 Pages 并配置 DEEPSEEK_API_KEY 即可运行。</p></div><div class="faq__item"><h3>开源雷达在哪里获取原始 JSON 与 Usage 接口？</h3><p>每次同步自动提交 docs/data.json 与 docs/usage.json，可直接用于站外订阅或二次分析。</p></div></div></div>
    </div>
  </div>
</section>
