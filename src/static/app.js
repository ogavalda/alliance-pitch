// Behaviour only. All text and numbers come from content/*.yaml through the DATA object.
const DATA = JSON.parse(document.getElementById('data').textContent);
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const esc = s => s;

// reveal + progress + nav highlight
const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) e.target.classList.add('in') }), {threshold: .12});
$$('.reveal').forEach(e => io.observe(e));
const secs = $$('main section'), links = $$('header.nav a');
function onScroll() {
  const h = document.documentElement;
  $('#bar').style.width = (h.scrollTop / (h.scrollHeight - h.clientHeight) * 100) + '%';
  let cur = secs[0]; secs.forEach(s => { if (s.getBoundingClientRect().top < 140) cur = s });
  links.forEach(a => a.classList.toggle('on', a.getAttribute('href') === '#' + cur.id));
}
addEventListener('scroll', onScroll); onScroll();
addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT') return;
  const i = secs.findIndex(s => s.getBoundingClientRect().top > -60 && s.getBoundingClientRect().top < 200);
  const k = i < 0 ? 0 : i;
  if (e.key === 'ArrowRight' && secs[k + 1]) secs[k + 1].scrollIntoView({behavior: 'smooth'});
  if (e.key === 'ArrowLeft' && secs[k - 1]) secs[k - 1].scrollIntoView({behavior: 'smooth'});
});

function tabs(container, items, render, labelOf) {
  const box = $(container);
  box.innerHTML = items.map((it, i) => `<button class="tab ${i ? '' : 'on'}" data-i="${i}">${labelOf(it)}</button>`).join('');
  const go = i => { [...box.children].forEach((b, j) => b.classList.toggle('on', j === i)); render(items[i], i) };
  [...box.children].forEach((b, i) => b.onclick = () => go(i));
  go(0);
}

// hero network toggle
if ($('#net-off')) $$('[data-n]').forEach(b => b.onclick = () => {
  $$('[data-n]').forEach(x => x.classList.remove('on')); b.classList.add('on');
  $('#net-off').style.display = b.dataset.n === '1' ? 'none' : 'block';
  $('#net-on').style.display = b.dataset.n === '1' ? 'block' : 'none';
});

// jobs
if ($('#jtabs')) tabs('#jtabs', DATA.jobs,
  j => $('#jout').innerHTML = `<h3>${j.title}</h3><p>${j.detail}</p><p><b>${j.value}</b></p>`, j => j.title);

// feeder demo
if ($('#mtabs')) {
  const keys = Object.keys(DATA.demo.feeder), labels = JSON.parse($('#mtabs').dataset.labels);
  tabs('#mtabs', keys, k => {
    const f = DATA.demo.feeder[k];
    $('#chart').innerHTML = f.svg; $('#pk').textContent = f.peak + ' ' + DATA.demo.unit; $('#hr').textContent = f.hours_over + ' h';
    const v = $('#vd'); v.textContent = DATA.demo.verdicts[k]; v.style.color = f.hours_over ? '#b00052' : '#256a3b';
  }, k => labels[k]);
}

// comparison table
if ($('#ftabs')) {
  const F = DATA.form;
  const draw = hl => {
    const sym = F.scale;
    $('#ftable').innerHTML = `<tr><th>${F.col_option}</th>` + F.requirements.map((r, k) => `<th ${k === hl ? 'style="background:#f8e9ed"' : ''}>${r}</th>`).join('') + `<th>${F.col_weakness}</th></tr>` +
      F.options.map(o => `<tr class="${o.highlight ? 'hl' : ''}"><td><b>${o.name}</b></td>` +
        o.values.map((v, k) => `<td class="${v}" ${k === hl ? 'style="background:#f8e9ed"' : ''}>${sym[v]}</td>`).join('') + `<td>${o.weakness}</td></tr>`).join('');
  };
  tabs('#ftabs', F.requirements, (_, i) => draw(i), r => r);
}

// roles and asks
if ($('#rtabs')) tabs('#rtabs', DATA.roles, r => {
  $('#rgive').innerHTML = `<div class="kicker" style="margin:0">${DATA.bring_label}</div><p>${r.bring}</p>`;
  $('#rget').innerHTML = `<div class="kicker" style="margin:0">${DATA.get_label}</div><p>${r.get}</p>`;
}, r => r.name);
if ($('#atabs')) tabs('#atabs', DATA.asks,
  a => $('#aout').innerHTML = `<div class="kicker" style="margin:0">${DATA.next_step_label}</div><p>${a.text}</p>`, a => a.name);

// questions
if ($('#qs')) {
  $('#qs').innerHTML = DATA.questions.map((q, i) => `<div class="q"><i>${i + 1}</i><div><div class="kicker" style="margin:0">${q.tag}</div><h3>${q.title}</h3><p>${q.text}</p></div></div>`).join('');
  $('#copyq').onclick = () => {
    const t = DATA.questions.map((q, i) => `${i + 1}. ${q.title}\n   ${q.text}`).join('\n\n');
    const ok = () => $('#cm').textContent = DATA.copied, no = () => $('#cm').textContent = DATA.copy_failed;
    navigator.clipboard ? navigator.clipboard.writeText(t).then(ok, no) : no();
  };
}

// stack toggle (tool landscape)
if ($('#stabs')) $$('[data-s]').forEach(b => b.onclick = () => {
  $$('[data-s]').forEach(x => x.classList.remove('on')); b.classList.add('on');
  $('#stk-today').style.display = b.dataset.s === 'today' ? 'block' : 'none';
  $('#stk-core').style.display = b.dataset.s === 'core' ? 'block' : 'none';
});

// tool map colour mode
if ($('#mtoggle')) $$('[data-mc]').forEach(b => b.onclick = () => {
  $$('[data-mc]').forEach(x => x.classList.remove('on')); b.classList.add('on');
  $('#mapbox').dataset.mode = b.dataset.mc;
  $('.leg-who').style.display = b.dataset.mc === 'who' ? 'flex' : 'none';
  $('.leg-geo').style.display = b.dataset.mc === 'geo' ? 'flex' : 'none';
});
