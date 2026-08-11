// RapidClean Portable Toilet Rental Works — site interactions
document.addEventListener('DOMContentLoaded', function () {

  /* Mobile drawer nav */
  var burger = document.querySelector('.hamburger');
  var drawer = document.querySelector('.mobile-nav');
  var scrim = document.querySelector('.mobile-nav-scrim');
  var closeBtn = document.querySelector('.mn-close');

  function openDrawer(){
    drawer.classList.add('is-open');
    scrim.classList.add('is-open');
    burger.classList.add('is-open');
    burger.setAttribute('aria-expanded','true');
    document.body.style.overflow='hidden';
  }
  function closeDrawer(){
    drawer.classList.remove('is-open');
    scrim.classList.remove('is-open');
    burger.classList.remove('is-open');
    burger.setAttribute('aria-expanded','false');
    document.body.style.overflow='';
  }
  if (burger){
    burger.addEventListener('click', function(){
      drawer.classList.contains('is-open') ? closeDrawer() : openDrawer();
    });
  }
  if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
  if (scrim) scrim.addEventListener('click', closeDrawer);

  /* Mobile submenu toggle (Services) */
  document.querySelectorAll('.mn-toggle').forEach(function(btn){
    btn.addEventListener('click', function(){
      var sub = document.getElementById(btn.getAttribute('aria-controls'));
      var open = sub.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  /* Desktop Services dropdown: hover handled in CSS; add click/keyboard support */
  var servicesItem = document.querySelector('.nav-list li.services-item');
  if (servicesItem){
    var trigger = servicesItem.querySelector('.nav-link');
    trigger.addEventListener('click', function(e){
      e.preventDefault();
      servicesItem.classList.toggle('open');
      trigger.setAttribute('aria-expanded', servicesItem.classList.contains('open') ? 'true':'false');
    });
    document.addEventListener('click', function(e){
      if (!servicesItem.contains(e.target)) servicesItem.classList.remove('open');
    });
    document.addEventListener('keydown', function(e){
      if (e.key === 'Escape') servicesItem.classList.remove('open');
    });
  }

  /* FAQ accordion */
  document.querySelectorAll('.faq-item').forEach(function(item){
    var q = item.querySelector('.faq-q');
    if(!q) return;
    q.addEventListener('click', function(){
      var wasOpen = item.classList.contains('is-open');
      item.parentElement.querySelectorAll('.faq-item').forEach(function(i){ i.classList.remove('is-open'); i.querySelector('.faq-q').setAttribute('aria-expanded','false'); });
      if (!wasOpen){ item.classList.add('is-open'); q.setAttribute('aria-expanded','true'); }
    });
  });

  /* Quote / contact form — client-side confirmation (no backend wired) */
  document.querySelectorAll('form[data-quote-form]').forEach(function(form){
    form.addEventListener('submit', function(e){
      e.preventDefault();
      var note = form.querySelector('.form-success');
      form.querySelectorAll('input,select,textarea,button').forEach(function(el){ el.disabled = true; });
      if (note) note.style.display = 'block';
      form.scrollIntoView({behavior:'smooth', block:'center'});
    });
  });

  /* Header shadow on scroll */
  var header = document.querySelector('.site-header');
  if (header){
    window.addEventListener('scroll', function(){
      header.style.boxShadow = window.scrollY > 8 ? '0 6px 18px rgba(22,29,39,.08)' : 'none';
    }, {passive:true});
  }

  /* Footer year */
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();
});
