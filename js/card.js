// neon-card-multi.js
(() => {
  // Все активные экземпляры (чтобы останавливать другие при запуске нового)
  const instances = new Set();

  // Создаём экземпляр поведения для одной карточки
  function createCardInstance(cardEl) {
    const playBtn = cardEl.querySelector('.neon-play-btn');
    const icon = cardEl.querySelector('#neonIconPlay') || cardEl.querySelector('svg');
    const bars = Array.from(cardEl.querySelectorAll('.neon-bar'));
    const currentLine = cardEl.querySelector('#neonCurrentLine');
    const transcriptEl = cardEl.querySelector('#neonTranscript');

    // Опционально: путь к аудиофайлу, указан в data-audio карточки
    const audioSrc = cardEl.dataset.audio || null;
    const audio = audioSrc ? new Audio(audioSrc) : null;
    if (audio) audio.crossOrigin = 'anonymous';
    let audioCtx = null, analyser = null, source = null, dataArray = null;
    let synthAnim = null;
    let usingSynth = false;
    let utter = null;

    // Инициализируем web audio analyser для данного audio (лениво)
    function ensureAudioAnalyser() {
      if (!audio || audioCtx) return;
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      try {
        source = audioCtx.createMediaElementSource(audio);
        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 128;
        dataArray = new Uint8Array(analyser.frequencyBinCount);
        source.connect(analyser);
        analyser.connect(audioCtx.destination);
      } catch (e) {
        // Некоторый браузер/кросс-источник может ломать создание; в таком случае fallback в TTS
        console.warn('Audio analyser init failed', e);
      }
    }

    function updateVisualizerAudio() {
      if (!analyser) return;
      analyser.getByteFrequencyData(dataArray);
      for (let i = 0; i < bars.length; i++) {
        const v = dataArray[i] || 0;
        const h = Math.max(6, (v / 255) * 40);
        bars[i].style.height = h + 'px';
      }
      if (!audio.paused) requestAnimationFrame(updateVisualizerAudio);
    }

    function startSynthAnim() {
      stopSynthAnim();
      let t = 0;
      synthAnim = setInterval(() => {
        bars.forEach((b, idx) => {
          const h = 6 + Math.abs(Math.sin((t + idx) / 3)) * (18 + idx * 2);
          b.style.height = h + 'px';
        });
        t++;
      }, 70);
    }
    function stopSynthAnim() {
      if (synthAnim) { clearInterval(synthAnim); synthAnim = null; }
      bars.forEach(b => b.style.height = '6px');
    }

    function setPlayingUI(isPlaying) {
      if (isPlaying) {
        if (icon) icon.innerHTML = '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" fill="#021218"/>';
        playBtn.classList.add('playing');
        playBtn.setAttribute('aria-pressed', 'true');
      } else {
        if (icon) icon.innerHTML = '<path d="M5 3v18l15-9L5 3z" fill="#021218" />';
        playBtn.classList.remove('playing');
        playBtn.setAttribute('aria-pressed', 'false');
      }
    }

    function stopAllMediaInInstance() {
      // остановить audio
      if (audio && !audio.paused) {
        audio.pause();
        try { audio.currentTime = 0; } catch (e) {}
      }
      // остановить TTS
      if (usingSynth) {
        speechSynthesis.cancel();
        usingSynth = false;
      }
      // остановить анимацию
      stopSynthAnim();
      setPlayingUI(false);
      // если есть audioCtx — не закрываем, оставим для повторного использования
    }

    function startSpeechSynthesis() {
      // выключаем audio если был
      if (audio && !audio.paused) { audio.pause(); setPlayingUI(false); }

      const text = (transcriptEl && transcriptEl.textContent) ? transcriptEl.textContent : '';
      usingSynth = true;
      utter = new SpeechSynthesisUtterance(text);
      utter.lang = 'ru-RU';
      utter.onstart = () => { setPlayingUI(true); startSynthAnim(); };
      utter.onend = () => { setPlayingUI(false); stopSynthAnim(); usingSynth = false; };
      utter.onerror = () => { setPlayingUI(false); stopSynthAnim(); usingSynth = false; };
      speechSynthesis.cancel();
      speechSynthesis.speak(utter);
    }

    function playPause() {
      // Если есть аудио-файл и он готов — используем его
      if (audio && audio.readyState > 2) {
        // переключаем воспроизведение
        if (audio.paused) {
          // остановим остальные карточки
          instances.forEach(inst => { if (inst !== instance) inst.stop(); });
          ensureAudioAnalyser();
          audio.play().then(() => {
            setPlayingUI(true);
            updateVisualizerAudio();
          }).catch((e) => {
            console.warn('audio play failed, fallback to TTS', e);
            startSpeechSynthesis();
          });
        } else {
          audio.pause();
          setPlayingUI(false);
        }
        return;
      }

      // Если аудио есть, но не готово — попробуем загрузить / play => will fallback
      if (audio && !audio.paused) { audio.pause(); setPlayingUI(false); return; }

      // fallback: speechSynthesis
      if (usingSynth && speechSynthesis.speaking) {
        speechSynthesis.cancel();
        stopSynthAnim();
        usingSynth = false;
        setPlayingUI(false);
        return;
      }

      // остановить другие карты
      instances.forEach(inst => { if (inst !== instance) inst.stop(); });

      startSpeechSynthesis();
    }

    // expose instance controls
    const instance = {
      stop() {
        stopAllMediaInInstance();
      }
    };

    // bind click
    playBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      playPause();
    });

    // If audio exists, try to mark ready
    if (audio) {
      // audio.addEventListener('ended', () => { setPlayingUI(false); stopSynthAnim(); });
      audio.addEventListener('ended', () => {
        try { audio.currentTime = 0; } catch (e) {/* ignore*/}
        setPlayingUI(false);
        stopSynthAnim();
    });
      audio.addEventListener('play', () => { setPlayingUI(true); });
      audio.addEventListener('pause', () => { setPlayingUI(false); stopSynthAnim(); });
      audio.addEventListener('error', (e) => { console.warn('audio error', e); });
      // If the audio canplay, we can use it
      audio.addEventListener('canplay', () => { /* ready */ });
    }

    return instance;
  }

  // Найти все карточки и инициализировать
  document.addEventListener('DOMContentLoaded', () => {
    const cards = Array.from(document.querySelectorAll('.neon-card'));
    cards.forEach(card => {
      const inst = createCardInstance(card);
      // сохраняем экземпляры в Set
      instances.add(inst);
    });

    // При удалении карточки со страницы — очищаем Set (если нужно)
    // Можно расширить: при SPA переходах — удалять экземпляры
  });
})();
