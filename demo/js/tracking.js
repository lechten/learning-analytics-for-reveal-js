/*!
 * reveal.js-tracking plugin v1.0.0
 * Joe Pantazidis <joe.pantazidis@outlook.de>
 * MIT licensed
 *
 * Copyright (C) 2020 Joe Pantazidis
 */

/**
 * A basic Timer class to capture dwell times.
 */
class Timer {
  constructor() {
    this.hours   = 0;
    this.minutes = 0;
    this.seconds = 0;
  }

  start() {
    if (this.timer) {
      console.log('The timer is already running.');
    } else {
      let self = this;
      this.timer = setInterval(() => {
        self._incrementSecond();
      }, 1000);
    }
  }

  reset() {
    this.clear();
    this.start();
  }

  clear() {
    if (this.timer) {
      clearInterval(this.timer);
      delete this.timer;
    }
    this.hours   = 0;
    this.minutes = 0;
    this.seconds = 0;
  }

  toString() {
    let hourString   = (this.hours   > 9 ? this.hours   : '0' + this.hours);
    let minuteString = (this.minutes > 9 ? this.minutes : '0' + this.minutes);
    let secondString = (this.seconds > 9 ? this.seconds : '0' + this.seconds);

    return (hourString + ':' + minuteString + ':' + secondString);
  }

  _incrementSecond() {
    this.seconds++;
    if (this.seconds >= 60) {
      this.seconds = 0;
      this.minutes++;
      if (this.minutes >= 60) {
        this.minutes = 0;
        this.hours++;
      }
    }
  }
};

/**
 * Tracking plug-in for reveal.js
 */
const RevealTracking = window.RevealTracking || (function () {
  /**
   * apiConfig: {
   *   authenticationAPI: {
   *     validateTokenEndpoint: 'https://learning.analytics/api/authentication/validate-token',
   *     requestTokenEndpoint: 'https://learning.analytics/api/authentication/generate-token',
   *   },
   *   trackingAPI: 'https://learning.analytics/api/tracking',
   * },
   * consentBanner: {
   *   closeButton: {
   *     class: 'consent-banner--close',
   *     text: '&times;',
   *   },
   *   consentButton: {
   *     class: 'consent-banner--button',
   *     text: 'I\'d like that!',
   *   },
   *   infoText: 'This presentation uses pseudonymous tracking for Learning Analytics.',
   *   moreLink: {
   *     class: 'consent-banner--more-link',
   *     href: 'https://learning.analytics/privacy',
   *     text: 'Learn more',
   *   },
   * },
   * dwellTimes: {
   *   total: true,
   *   perSlide: true,
   * },
   * links: {
   *   internal: true,
   *   external: true,
   * },
   * media: {
   *   * audio-slideshow plug-in is helpful
   *   audio: true,
   *   video: true,
   * },
   * slideTransitions: true,
   * revealDependencies: {
   *   * requires quiz plug-in
   *   quiz: true,
   *   otherPluginInTheFuture: true,
   * },
   */
  const defaultConfig = {
    apiConfig: {},
    consentBanner: {
      closeButton: {
        class: 'consent-banner--decline',
        text: 'Decline tracking!',
      },
      consentButton: {
        class: 'consent-banner--button',
        text: 'I\'d like that!',
      },
      infoText: 'This presentation uses pseudonymous tracking for Learning Analytics.',
      moreLink: {
        class: 'consent-banner--more-link',
        text: 'Learn more',
      },
    },
    dwellTimes: true,
    shortCuts: true,
    shortCutsToTrack: ['shift-?'],
    links: true,
    media: true,
    slideTransitions: true,
    revealDependencies: {
      quiz: false,
    },
  };

  // overwrite default config with manual config
  const config = {...defaultConfig, ...Reveal.getConfig().tracking};
  // this object is sent to the trackingAPI on window#unload
  let postBody = { timeline: [] };
  let consentGiven = false;
  let userToken;
  let sessionToken;

  let globalTimer = new Timer(),
      slideTimer  = new Timer();
  let quizTimers  = {};

  /** 
   * Validate API configuration for tracking plug-in.
   */
  if (config.apiConfig.trackingAPI == undefined) {
    console.error('You have no trackingAPI configured where to send tracking data to!');
    return;
  }

  if (
    config.apiConfig.authentication == undefined ||
    config.apiConfig.authentication.requestTokenEndpoint == undefined
  ) {
    console.warn(
      _strip(`
        You have no authenticationAPI configured.
        The tracking requests will not have tokens and the tracking data will be completely anonymous. 
        Please consider setting apiConfig.authentication.requestTokenEndpoint and
        apiConfig.authentication.validateTokenEndpoint.
      `)
    );
  } else if (
    config.apiConfig.authentication.requestTokenEndpoint != undefined &&
    config.apiConfig.authentication.validateUserTokenEndpoint == undefined&&
    config.apiConfig.authentication.validateSessionTokenEndpoint == undefined

  ) {
    console.warn(
      _strip(`
        You have no validateTokenEndpoint configured in the authenticationAPI.
        Tokens will not be validated prior to the transmission of tracking data.
        You might lose data!
        Please consider setting apiConfig.authentication.validateTokenEndpoint.
      `)
    );
  }

  // Main Logic: public functions

  /**
   * Load the user token:
   * - from cookies
   * - from HTML local storage
   * - from authentication API
   */
  async function loadUserToken() {
    userToken = _getCookie('user_token');
    if (userToken) {
      userToken= await _userTokenIsValid();
      sessionToken = window.sessionStorage.getItem('session_token');

      if (userToken && sessionToken) {
        sessionToken = await _sessionTokenIsValid()
      }else{
        await _requestUserSessionToken();
      }

      if (userToken) consentGiven = true;
    }
  }

  /**
   * Display menu to open cookie options.
   */
  function addCookieMenu() {
    if (config.consentBanner != false) {
      _loadStylesheet();
      let cbConfig = config.consentBanner;

      // create consent banner node
      let consentMenu = document.createElement('div');
      consentMenu.classList.add('consent-menu');
      consentMenu.innerHTML = _strip(`
        <button class="consent-menu--button">Cookie options</button>
      `);

      // define event listeners for closing the banner and giving consent
      consentMenu.querySelector(`.consent-menu--button`).addEventListener('click', function() {
        showConsentBanner(true);
      });

      // add consent banner to DOM
      document.body.prepend(consentMenu);
    }
  }

  /**
   * Display consent banner.
   */
  function showConsentBanner(manual_open = false) {
    if (manual_open || (userToken == undefined && config.consentBanner != false)){
      _loadStylesheet();
      let cbConfig = config.consentBanner;

      // create consent banner node
      let consentBanner = document.createElement('div');
      consentBanner.classList.add('consent-banner');
      consentBanner.innerHTML = _strip(`
        <p class="consent-banner--info-text">
          ${cbConfig.infoText}
          <a class="${cbConfig.moreLink.class}" href="${cbConfig.moreLink.href || '#'}" target="_blank">${cbConfig.moreLink.text}</a>
        </p>
        <button class="${cbConfig.consentButton.class}">${cbConfig.consentButton.text}</button>
        <a class="${cbConfig.closeButton.class}">${cbConfig.closeButton.text}</a>
      `);

      // define event listeners for closing the banner and giving consent
      consentBanner.querySelector(`.${cbConfig.closeButton.class}`)
          .addEventListener('click', function() {
        consentBanner.remove();
        consentGiven = false;
        userToken = null;
        _removeCookie('user_token');
        window.sessionStorage.removeItem('session_token')
      });

      consentBanner.querySelector(`.${cbConfig.consentButton.class}`).addEventListener('click', function() {
        consentBanner.remove();
        consentGiven = true;
        _requestUserSessionToken(manual_open).catch(err => console.error(err));
      });

      // add consent banner to DOM
      document.body.prepend(consentBanner);
    }
  }

  /**
   * Start all necessary timers.
   */
  function startTimers() {
    if (_tracksDwellTimePerSlide()) {
      globalTimer.start();
      slideTimer.start();
    } else {
      globalTimer.start();
    }
  }

  /**
   * Add all event listeners for tracking.
   */
  function addEventListeners() {
    _trackClosing();
    _trackDwellTimes();
    _trackLinks();
    _trackSlideTransitions();
    _trackMediaActions();
    _trackQuizzes();
    _trackKeyboard();
  }

  /**
   * Adds metadata, such as the presentation's URL and its total number of slides.
   */
  function addMetadata() {
    // remove the hash parameters (from reveal.js)
    postBody.presentationUrl = window.location.href.replace(/(#(.+)?)/, '');
    postBody.totalNumberOfSlides = Reveal.getTotalSlides();
  }

  // Consent Banner: helper functions

  /**
   * Load consent banner stylesheet.
   */
  function _loadStylesheet() {
    let script;
    if (document.currentScript) {
      script = document.currentScript;
    } else {
      script = document.querySelector('script[src$="/tracking.js"]');
    }
    if (script) {
      path = script.src.replace(/js/g, 'css');
    }
    let link  = window.document.createElement('link');
    link.rel  = 'stylesheet';
    link.type = 'text/css';
    link.href = path;

    window.document.getElementsByTagName('head')[0].appendChild(link);
  }

  /**
   * Query authentication API to check whether the current user
   * token is valid.
   */
  async function _userTokenIsValid() {
    if (
      config.apiConfig.authentication == undefined ||
      config.apiConfig.authentication.validateUserTokenEndpoint == undefined ||
      config.apiConfig.authentication.validateSessionTokenEndpoint == undefined
    ) {
      return true;
    }

    try {
      let response = await fetchRetry(config.apiConfig.authentication.validateUserTokenEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_token: userToken,
          total_slides: Reveal.getTotalSlides(),
          absolute_url: window.location.href
        }),
      });
      let data = await response.json();
      window.localStorage.setItem("user_token", data.user_token)

      return data.user_token;
    } catch(err) {
      console.error(err);
      return false;
    }
  }

  /**
   * Query authentication API to check whether the current user
   * token is valid.
   */
  async function _sessionTokenIsValid() {
    if (
      config.apiConfig.authentication == undefined ||
      config.apiConfig.authentication.validateUserTokenEndpoint == undefined ||
      config.apiConfig.authentication.validateSessionTokenEndpoint == undefined
    ) {
      return true;
    }

    try {
      let response = await fetchRetry(config.apiConfig.authentication.validateSessionTokenEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_token: userToken,
          session_token: sessionToken,
          total_slides: Reveal.getTotalSlides(),
          absolute_url: window.location.href
        }),
      });
      let data = await response.json();
      window.localStorage.setItem("user_token", data.user_token)
      window.sessionStorage.setItem("session_token", data.session_token)


      return data.session_token;
    } catch(err) {
      console.error(err);
      return false;
    }
  }

  /**
   * Request user token from authentication API.
   */
  async function _requestUserSessionToken( confirmation = false) {
    //return if only a confirmation of tracking consent was given (no new token necessary)
    if (confirmation) return;

    if (
      config.apiConfig.authentication == undefined ||
      config.apiConfig.authentication.requestTokenEndpoint == undefined
    ) {
      userToken = null;
      _removeCookie('user_token');
      return;
    }

    try {
      let response = await fetchRetry(config.apiConfig.authentication.requestTokenEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_token: window.localStorage.getItem("user_token"),
          total_slides: Reveal.getTotalSlides(),
          absolute_url: window.location.href
        }),
      });
      let data = await response.json();

      _setCookie('user_token', data.user_token);
      window.sessionStorage.setItem('session_token', data.session_token);
      userToken = data.user_token
      sessionToken = data.session_token


    } catch(err) {
      console.error(err)
      userToken = null;
    }
  }

  // Tracking logic: helper functions

  /**
   * Track shortcuts
   */
  function _trackKeyboard() {
    if(_tracksShortCuts){
      window.addEventListener("keydown", (evt) => {
         shortcut.track(evt.key.toLowerCase(), true);
      });
      window.addEventListener("keyup", (evt) => {
         shortcut.track(evt.key.toLowerCase(), false);
      });
    }
  }

  /**
   * Reads list of shortcuts to track for from config:
   * e.g.: ['control-shift-f', 'shift-f', 'shift-?']
   */
  let shortcut = {
  // (A) SET SHORTCUT KEYS TO LISTEN TO
  listen : config.shortCutsToTrack,

  // (B) KEY PRESS SEQUENCE TRACKER
  sequence : [],
  track : (key, direction) => {
    // (B1) PREVENT AUTO CLEANING
    if (shortcut.junk != null) { clearTimeout(shortcut.junk); }

    // (B2) KEY DOWN
    if (direction) { if (!shortcut.sequence.includes(key)) {
      shortcut.sequence.push(key);
    }}

    // (B3) KEY UP
    else {
      let idx = shortcut.sequence.indexOf(key);
      if (idx != -1) { shortcut.sequence.splice(idx, 1); }
    }

   // (B4) HIT SHORTCUT?
    if (shortcut.sequence.length != 0) {
      let seq = shortcut.sequence.join("-");
      if (shortcut.listen.includes(seq)) {
        shortcut.sequence = [];
        let eventData = {
          shortcut: seq,
        };
        _track('shortcut', eventData);

      }

      // (B5) PREVENT "STUCK SEQUENCE" WHEN USER LEAVES PAGE
      // E.G. OPEN NEW TAB WHILE IN MIDDLE OF KEY PRESS SEQUENCE
      else {
        shortcut.junk = setTimeout(shortcut.clean, 600)
      }
    }
  },

  // (C) AUTO CLEANUP
  junk : null,
  clean : () => {
    shortcut.junk = null;
    shortcut.sequence = [];
  }
};

  /**
   * Track dwell time per slide.
   */
  function _trackDwellTimes() {
    if (_tracksDwellTimePerSlide()) {
      Reveal.addEventListener('slidechanged', function(event) {
        _track('dwellTimePerSlide', {
          dwellTime: slideTimer.toString(),
        },
        );

        slideTimer.reset();
      });
    }
  }

  /**
   * Track last dwell time per slide and total dwell time.
   * Also send data to trackingAPI.
   */
  function _trackClosing() {
    window.addEventListener('unload', function() {
      if (_tracksDwellTimePerSlide()) {
        _track('dwellTimePerSlide', {
          dwellTime: slideTimer.toString(),
        });
      }

      if (_tracksTotalDwellTime()) {
        _track('totalDwellTime', {
          totalDwellTime: globalTimer.toString(),
        });
      }

      _track('end', {
        finalProgress: Reveal.getProgress(),
      });

      _sendTrackingData();
    });
  }

  /**
   * Track clicks on links.
   */
  function _trackLinks() {
    if (_tracksInternalLinks() || _tracksExternalLinks()) {
      document.addEventListener('click', function(event) {
        if (!Array.from(Reveal.getCurrentSlide().querySelectorAll('a')).includes(event.target)) return true;
        let baseURL = window.location.href.replace((new RegExp(window.location.hash) || ''), '');
        let path = event.target.href.replace(baseURL, '');

        if (path == '#') return true;

        let isInternalLink = path.startsWith('#');

        if ((isInternalLink && _tracksInternalLinks()) || (!isInternalLink && _tracksExternalLinks())) {
          let linkType = isInternalLink ? 'internalLink' : 'externalLink';
          let href     = isInternalLink ? path           : event.target.href;

          _track('link', {
            timestamp: globalTimer.toString(),
            metadata: {
              href: href,
              linkText: event.target.text,
            },
            linkType:linkType,
          });
        }
      });
    }
  }

  /**
   * Track audio and video (play, pause, progress).
   */
  function _trackMediaActions() {
    if (_tracksAudio() || _tracksVideo()) {
      function trackMediaEvents() {
        _getMedia().forEach(function(media) {
          let mediaType = media.tagName.toLowerCase();

          if (!media.onplay) {
            media.onplay = function () {
              _track('media', {
                mediaEvent: 'play',
                timestamp: globalTimer.toString(),
                metadata: {
                  id: this.id,
                  mediaSource: this.currentSrc,
                },
                mediaType: mediaType,
              });
            };
          }

          if (!media.onpause) {
            media.onpause = function () {
              _track('media', {
                mediaEvent: 'pause',
                finished: this.ended,
                progress: this.currentTime / this.duration,
                timestamp: globalTimer.toString(),
                metadata: {
                  id: this.id,
                  mediaSource: this.currentSrc,
                },
                mediaType: mediaType,
              });
            };
          }
        });
      }

      Reveal.addEventListener('ready',          trackMediaEvents);
      Reveal.addEventListener('fragmentshown',  trackMediaEvents);
      Reveal.addEventListener('fragmenthidden', trackMediaEvents);
      Reveal.addEventListener('slidechanged',   trackMediaEvents);
    }
  }

  /**
   * Track slide transitions.
   */
  function _trackSlideTransitions() {
    if (config.slideTransitions) {
      Reveal.addEventListener('slidechanged', function(event) {

        let eventData = {
          transitionDetails: _transitionDirection(_slideData(event.previousSlide), _slideData(event.currentSlide)),
          timestamp: globalTimer.toString(),
        };

        _track('slideTransition', eventData);
      });
    }
  }

  /**
   * Track quizzes from plug-in
   * [reveal.js-quiz](https://gitlab.com/schaepermeier/reveal.js-quiz).
   * Includes score, and whether they were started and completed.
   */
  function _trackQuizzes() {
    if (config.revealDependencies.quiz) {
      let quizConfig = Reveal.getConfig().quiz || {};
      quizConfig.events = quizConfig.events || {};

      function trackQuizStart() {
        let quizName = Reveal.getCurrentSlide().querySelector('[data-quiz]').dataset.quiz;
        if (!quizName) return true;

        let quiz = window[quizName];
        if (!quiz) return true;

        if (quizTimers[quizName] instanceof Timer) {
          quizTimers[quizName].reset();
        } else {
          quizTimers[quizName] = new Timer();
          quizTimers[quizName].start();
        }

        let quizMetadata = {
          id: quizName,
          name: quiz.info.name,
          topic: quiz.info.main,
          numberOfQuestions: quiz.questions.length,
        }

        _track('quiz', {
          quizEvent: 'start',
          timestamp: globalTimer.toString(),
          metadata: quizMetadata,
        });
      }

      function trackQuizComplete(options) {
        let quizName = Reveal.getCurrentSlide().querySelector('[data-quiz]').dataset.quiz;
        if (!quizName) return true;

        let quiz = window[quizName];
        if (!quiz) return true;

        let dwellTime;
        if (quizTimers[quizName] instanceof Timer) {
          dwellTime = quizTimers[quizName].toString();
          quizTimers[quizName].clear();
        }

        let quizMetadata = {
          id: quizName,
          name: quiz.info.name,
          topic: quiz.info.main,
          numberOfQuestions: quiz.questions.length,
        }

        _track('quiz', {
          quizEvent: 'complete',
          dwellTime: dwellTime,
          completed: true,
          score: options.score,
          timestamp: globalTimer.toString(),
          metadata: quizMetadata,
        });
      }

      if (quizConfig.events.onStartQuiz) {
        let existingCallback = quizConfig.events.onStartQuiz;
        quizConfig.events.onStartQuiz = function() {
          trackQuizStart();
          existingCallback();
        }
      } else {
        quizConfig.events.onStartQuiz = function() {
          trackQuizStart();
        }
      }

      if (quizConfig.events.onCompleteQuiz) {
        let existingCallback = quizConfig.events.onCompleteQuiz;
        quizConfig.events.onCompleteQuiz = function(options) {
          trackQuizComplete(options);
          existingCallback(options);
        }
      } else {
        quizConfig.events.onCompleteQuiz = function(options) {
          trackQuizComplete(options);
        }
      }

      // initialize the quizzes
      prepareQuizzes(quizConfig);
    }
  }

  // Helper methods.

  /**
   * Helper method to add event to timeline.
   */
  function _track(eventType, eventData, options = {}) {
    let event;
    eventData.absolute_url = window.location.href
    eventData.dateTime = new Date()

    if (eventType != 'totalDwellTime') {
      event = _createEvent(eventType, eventData, options);
    }

    switch (eventType) {
      case 'totalDwellTime':
      case 'end':
        postBody = {
          ...postBody,
          ...eventData,
        }
        break;

      case 'dwellTimePerSlide':
        //postBody.dwellTimes = postBody.dwellTimes || [];
        postBody.timeline.push(event);
        break;

      default:
        postBody.timeline.push(event);
        break;
    }

    if (postBody.timeline.length >= 10){
      _sendTrackingData();
    }
  }

  /**
   * Helper function to generate an event object for the timeline.
   */
  function _createEvent(eventType, eventData, options = {}) {
    let slide = options.slide || Reveal.getCurrentSlide();

    let event = {
      type: eventType,
      ...eventData,
    }

    //if (eventType != 'slideTransition') event.slideData = _slideData(slide);

    return event;
  }


  /**
   * Get slide metadata: slide number, and indices.
   */
  function _slideData(slide) {
    let indices = Reveal.getIndices(slide);
    let slideNumber = Reveal.getSlides().indexOf(slide) + 1;

    return {
      slideNumber: slideNumber,
      horizontalIndex: indices.h,
      verticalIndex: indices.v || 0
    };
  }

  /**
   * Determine the direction of a slide transition
   */
  function _transitionDirection(prevSlide, nextSlide){
    let verticalMovement = nextSlide["verticalIndex"] - prevSlide["verticalIndex"]
    let horizontalMovement = nextSlide["horizontalIndex"] - prevSlide["horizontalIndex"]

    return {
      vertical: verticalMovement,
      horizontal: horizontalMovement
    };
  }


  /**
   * Transmits a JSON in this format:
   * 
   * {
   *   userToken: string,
   *   presentationUrl: string,
   *   numberOfTotalSlides: integer,
   *   finalProgress: float|integer,
   *   totalDwellTime: string,
   *   dwellTimes: Array,
   *   timeline: Array
   * }
   */
  function _sendTrackingData() {
    if (consentGiven) {
      if (_getCookie('user_token')) {
        postBody.userToken = _getCookie('user_token');
      } else {
        console.warn('No user token is given.');
      }
      if (window.sessionStorage.getItem('session_token')) {
        postBody.sessionToken = window.sessionStorage.getItem('session_token');
      } else {
        console.warn('No session token is given.');
      }

      // transmit tracking dat
      var formData = new FormData();
      formData.append('csrfmiddlewaretoken', _getCookie('csrftoken'));
      formData.append('data', JSON.stringify(postBody))
      navigator.sendBeacon(config.apiConfig.trackingAPI, formData);

      //reset postBody for new events
      postBody = { timeline: [] };
      addMetadata()

    } else {
      console.warn('The user has not accepted to being tracked. No tracking data will be sent.');
    }
  }

  /**
   * Adapter for fetch API with retries.
   */
  async function fetchRetry(url, options, retries = 3) {
    try {
      return await fetch(url, options);
    } catch(err) {
      if (retries === 1) throw err;
      return await fetchRetry(url, options, retries - 1);
    }
  };

  /**
   * Retrieve cookie by key.
   */
  function _getCookie(key) {
    let cookie = document.cookie.split(';').filter(cookie => cookie.trim().startsWith(`${key}=`))[0];
    if (cookie) {
      return cookie.trim().split('=')[1];
    }
    return null;
  }

  /**
   * Set cookie for a given key and value.
   */
  function _setCookie(key, value) {
    if (key && value) {
      let date = new Date();
      date.setTime(date.getTime() + (365 * 24 * 60 * 60 * 1000));
      document.cookie = `${key}=${value}; expires=${date.toGMTString()}`;
    }
  }

  /**
   * Delete cookie by key.
   */
  function _removeCookie(key) {
    if (key) {
      document.cookie = `${key}=; expires=Thu, 01 Jan 1970 00:00:00 GMT`;
    }
  }

  /**
   * Get all media
   */
  function _getMedia() {
    function _mediaSelector() {
      if (_tracksAudio() && _tracksVideo()) {
        return 'audio, video';
      } else if(_tracksAudio()) {
        return 'audio';
      } else {
        return 'video';
      }
    }

    return document.querySelectorAll(_mediaSelector());
  }

  /**
   * Remove unnecessary spaces and line breaks from string.
   */
  function _strip(string) {
    return string.trim().replace(/(\s)+/g, ' ').replace(/\n/g, '');
  }

  /**
   * Returns whether the tracking plug-in is allowed
   * to track the total dwell time.
   */
  function _tracksTotalDwellTime() {
    return config.dwellTimes === true || config.dwellTimes.total;
  }

  /**
   * Returns whether the tracking plug-in is allowed
   * to track keyboard shortcuts.
   */
  function _tracksShortCuts() {
    return config.shortCuts === true;
  }

  /**
   * Returns whether the tracking plug-in is allowed
   * to track the dwell time per slide.
   */
  function _tracksDwellTimePerSlide() {
    return config.dwellTimes === true || config.dwellTimes.perSlide;
  }

  /**
   * Returns whether the tracking plug-in is allowed
   * to track internal link clicks.
   */
  function _tracksInternalLinks() {
    return config.links === true || config.links.internal;
  }

  /**
   * Returns whether the tracking plug-in is allowed
   * to track external link clicks.
   */
  function _tracksExternalLinks() {
    return config.links === true || config.links.external;
  }

  /**
   * Returns whether the tracking plug-in is allowed
   * to track audio interactions.
   */
  function _tracksAudio() {
    return config.media === true || config.media.audio;
  }

  /**
   * Returns whether the tracking plug-in is allowed
   * to track video interactions.
   */
  function _tracksVideo() {
    return config.media === true || config.media.video;
  }

  // Return plug-in object
  return {
    VERSION: '1.0.0',
    init: function() {
      // Register event listeners for tracking
      addEventListeners();
      // Load and verify user token if it exists,
      // then show the consent banner if applicable.
      loadUserToken().then(()=> showConsentBanner());
      addCookieMenu()
      if (Reveal.isReady()) {
        startTimers();
        addMetadata();
      } else {
        Reveal.addEventListener('ready', function() {
          startTimers();
          addMetadata();
        });
      }
    },
    giveConsent: function() {
      consentGiven = true;
    },
    removeConsent: function() {
      consentGiven = false;
    }
  }
})();

if (RevealTracking) Reveal.registerPlugin('tracking', RevealTracking);
