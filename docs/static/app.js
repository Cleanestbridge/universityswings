// ---- Demo data (tour only; no bookings)
const EVENTS = [
  { id:1, date:'2025-09-06', university:'Indiana University', city:'Bloomington', state:'IN', type:'Tailgate Stop', status:'past' },
  { id:2, date:'2025-10-11', university:'Ohio State University', city:'Columbus', state:'OH', type:'Tailgate Stop', status:'past' },
  { id:3, date:'2025-10-25', university:'University of Wisconsin', city:'Madison', state:'WI', type:'Tailgate Stop', status:'open' },
  { id:4, date:'2025-11-08', university:'University of Michigan', city:'Ann Arbor', state:'MI', type:'Tailgate Stop', status:'open' },
  { id:5, date:'2025-11-15', university:'Purdue University', city:'West Lafayette', state:'IN', type:'Club Night', status:'open' },
  { id:6, date:'2025-11-22', university:'Penn State University', city:'State College', state:'PA', type:'Tailgate Stop', status:'hold' },
];

// ---- Utilities
const $ = (s,root=document)=>root.querySelector(s);
const $$ = (s,root=document)=>Array.from(root.querySelectorAll(s));
const toast = (msg)=>{
  const el = $('#toast');
  if (!el) return;
  el.textContent = msg;
  el.classList.add('show');
  setTimeout(()=>el.classList.remove('show'), 1800);
};

// ---- Mobile nav
const mobileToggle = $('.mobile-toggle');
const mobileMenu = $('#mobileMenu');
if (mobileToggle && mobileMenu) {
  mobileToggle.addEventListener('click', ()=>{
    const open = mobileMenu.classList.toggle('open');
    mobileToggle.setAttribute('aria-expanded', String(open));
  });
}

// ---- Smooth scroll for local anchors
$$('a[href^="#"]').forEach(a=>{
  a.addEventListener('click', e=>{
    const id = a.getAttribute('href');
    const target = document.querySelector(id);
    if(target){ e.preventDefault(); target.scrollIntoView({ behavior:'smooth', block:'start' }); }
  })
});

// ---- Schedule rendering
const eventsEl = $('#events');

function renderEvents(list){
  if (!eventsEl) return;
  eventsEl.innerHTML = '';
  if(list.length===0){
    eventsEl.innerHTML = `<div class="note">No events found. Try clearing filters.</div>`;
    return;
  }
  for(const ev of list){
    const d = new Date(ev.date+'T12:00:00');
    const pretty = d.toLocaleDateString(undefined, { month:'short', day:'numeric', year:'numeric' });
    const card = document.createElement('article');
    card.className = 'event';
    card.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; gap:10px">
        <h3 style="margin:0">${ev.university}</h3>
        <span class="badge">${ev.type}</span>
      </div>
      <div class="meta">${pretty} • ${ev.city}, ${ev.state}</div>
      <div style="display:flex; gap:10px; flex-wrap:wrap">
        <button class="btn" data-ics data-title="University Swings at ${ev.university}" data-date="${ev.date}">Add to calendar</button>
        <button class="btn outline" data-prefill-request data-university="${ev.university}" data-citystate="${ev.city}, ${ev.state}">Request us here</button>
      </div>
    `;
    eventsEl.appendChild(card);
  }
}

// ---- Filters
const search = $('#search');
const state = $('#state');
const month = $('#month');
const clearFilters = $('#clearFilters');

function applyFilters(){
  const q = (search?.value || '').trim().toLowerCase();
  const st = state?.value || '';
  const mo = month?.value || '';
  const filtered = EVENTS.filter(e=>{
    const matchesQ = !q || `${e.university} ${e.city}`.toLowerCase().includes(q);
    const matchesState = !st || e.state===st;
    const matchesMonth = !mo || (new Date(e.date+'T12:00:00').getMonth()+1)==Number(mo);
    return matchesQ && matchesState && matchesMonth;
  });
  renderEvents(filtered);
}

[search,state,month].forEach(el=>{ if (el) el.addEventListener('input', applyFilters); });
if (clearFilters) {
  clearFilters.addEventListener('click', ()=>{
    if (search) search.value='';
    if (state) state.value='';
    if (month) month.value='';
    applyFilters();
  });
}

// ---- Request form (demo: mailto & localStorage)
const requestForm = $('#requestForm');
document.addEventListener('click', (e)=>{
  const icsBtn = e.target.closest?.('[data-ics]');
  const prefillBtn = e.target.closest?.('[data-prefill-request]');
  if(icsBtn){
    const title = icsBtn.getAttribute('data-title');
    const date = icsBtn.getAttribute('data-date');
    const dt = new Date(date+'T14:00:00'); // 2pm local placeholder
    const dtEnd = new Date(dt.getTime()+2*60*60*1000);
    const pad = n=>String(n).padStart(2,'0');
    const fmt = d=>`${d.getUTCFullYear()}${pad(d.getUTCMonth()+1)}${pad(d.getUTCDate())}T${pad(d.getUTCHours())}${pad(d.getUTCMinutes())}00Z`;
    const ics = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//University Swings//EN
BEGIN:VEVENT
UID:${crypto.randomUUID()}
DTSTAMP:${fmt(new Date())}
DTSTART:${fmt(dt)}
DTEND:${fmt(dtEnd)}
SUMMARY:${title}
DESCRIPTION:Mobile golf simulator campus tour
END:VEVENT
END:VCALENDAR`;
    const blob = new Blob([ics], { type:'text/calendar' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = `${title.replace(/\s+/g,'_')}.ics`; a.click();
    setTimeout(()=>URL.revokeObjectURL(url), 1000);
  }
  if(prefillBtn){
    $('#rUniversity')?.value = prefillBtn.getAttribute('data-university') || '';
    $('#rCityState')?.value = prefillBtn.getAttribute('data-citystate') || '';
    document.querySelector('#request')?.scrollIntoView({ behavior:'smooth', block:'start' });
  }
});

if (requestForm) {
  requestForm.addEventListener('submit', (e)=>{
    e.preventDefault();
    const name = $('#rName')?.value.trim();
    const email = $('#rEmail')?.value.trim();
    const university = $('#rUniversity')?.value.trim();
    if(!name || !email || !university){ toast('Please complete name, email, and university'); return; }
    const payload = {
      name,
      email,
      university,
      cityState: $('#rCityState')?.value.trim(),
      window: $('#rWindow')?.value.trim(),
      message: $('#rMessage')?.value.trim(),
      ts: Date.now()
    };
    // store locally for demo
    const all = JSON.parse(localStorage.getItem('ug.tourRequests')||'[]');
    all.push(payload);
    localStorage.setItem('ug.tourRequests', JSON.stringify(all));

    const body = encodeURIComponent(
      `Tour stop request\n\nName: ${payload.name}\nEmail: ${payload.email}\nUniversity: ${payload.university}\nCity/State: ${payload.cityState}\nPreferred window: ${payload.window}\nMessage: ${payload.message}`
    );
    window.location.href = `mailto:hello@universitygolf.com?subject=Tour%20Stop%20Request&body=${body}`;
    toast('Thanks! Opening your email client…');
    requestForm.reset();
  });
}

// ---- Init
renderEvents(EVENTS);   // show initial list
applyFilters();         // then filter if inputs exist
