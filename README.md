
# learning analytics for reveal.js

## Table of Contents

- [Demo](#demo)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
    - [Pseudonymous Tracking](#pseudonymous-tracking)
      - [The Consent Banner](#the-consent-banner)
  - [Advanced Usage](#advanced-usage)
    - [Hints](#hints)
      - [Audios and Videos](#audios-and-videos)
      - [Quizzes](#quizzes)
    - [Default Configuration](#default-configuration)
  - [Request Body to Tracking API](#request-body-to-tracking-api)
- [License](#license)

This repository contains a Django application, which uses tracking data to create
a dashboard with visualizations. The tracking is heavily based on the 
[reveal.js tracking plugin](https://github.com/pantajoe/reveal.js-tracking)
with some slight adjustments to support learning analytics.

## Demo

To view the demo of this plug-in, make sure you have Docker,
[docker-compose](https://github.com/docker/compose/releases), and
[grunt](https://gruntjs.com/getting-started) installed.

1. Install project dependencies with `npm install`
2. Build the containers with `docker-compose build`
3. And then fire up the API and the demo presentation with `docker-compose up`
4. Setup the database with `docker-compose run web python3 manage.py migrate`
5. Create a superuser for the lecturer with ` docker-compose run -e DJANGO_SUPERUSER_PASSWORD=my_password web python3 manage.py createsuperuser --noinput --username admin --email admin@mail.de`

On `http://localhost:8000`, you can enjoy the demo presentation.

On `http://localhost:8910`, you can enjoy the demo dashboard - but you have to track some data first.

If you delete your cookies, then you are treated as a new user.
Have fun!


## Reveal.js tracking plugin
Based on [reveal.js tracking plugin](https://github.com/pantajoe/reveal.js-tracking)
with some adjustments and additions:

This plug-in allows detailed tracking of interactions within a reveal.js
presentation. You are capable of defining to which API to send the tracking data
to. Tracked interactions are

- dwell times
- slide transitions
- clicking links
- playing and pausing media (audio recordings, videos)
- tracking quizzes
- tracking shortcuts

It also includes a configurable consent banner that respects the viewers'
privacy - content of banner has to be adjusted to conform GDPR.

If you only want to track slide transitions (Reveal's `slidechanged` event) and
opening/closing of the overview (Reveal's `overviewshown` and `overviewhidden`
events) and send them to Google Analytics, try the plug-in
[reveal-ga](https://github.com/stevegrunwell/reveal-ga) instead.

### Usage

#### Basic Usage

Simply download this folder – you only need the `tracking.css` in the `css`
folder and `tracking.js` in the `js` folder – and add it to your reveal.js
presentation's plug-in directory, so your directory structure looks like this:

```tree
├── plugin
│   ├── ... (other plugins)
│   ├── tracking
│   │   ├── css
│   │   │   ├── tracking.css
│   │   ├── js
│   │   │   ├── tracking.js
│   ├── ... (other plugins)
```

When initializing `Reveal`, add this plug-in as a dependency:

```javascript
Reveal.initialize({
  ...,
  dependencies: [
    ...,
    { src: 'plugin/tracking/js/tracking.js', async: false },
    ...
  ],
  ...
});
```

For the configuration of this plug-in, add a `tracking` section to your
reveal.js configuration:

```javascript
Reveal.initialize({
  ...,
  tracking: {
    apiConfig: {
      authenticationAPI: {
        // configure the APIs where to request a user and session token from
        validateUserTokenEndpoint: 'http://localhost:8910/api/validate-user-token/',
        validateSessionTokenEndpoint: 'http://localhost:8910/api/validate-session-token/',
        requestTokenEndpoint: 'http://localhost:8910/api/generate-session-token/',
        },
        trackingAPI: 'http://localhost:8910/api/events/',
    },
    // configure the consent banner
    consentBanner: {
      infoText: 'This presentation uses pseudonymous tracking for Learning Analytics.',
      moreLink: {
        href: 'https://my.platform/privacy',
      },
    },
    // track dwell times
    dwellTime: true,
    // track link visits
    links: true,
    // track media interactions
    media: true,
    // track slide transitions
    slideTransitions: true,
    // track shortcuts
    shortCuts: true,
    //define list of shortcuts to track
    shortCutsToTrack: ['shift-?'],
    // track events from other reveal.js plug-ins
    revealDependencies: {
      // track events from reveal.js-quiz plug-in
      quiz: true,
    },
  },
  ...
});
```

#### Pseudonymous Tracking

In order to be able to associate multiple tracked sessions for one person, a
token is requested from an authentication API via `POST`
(`tracking.apiConfig.authenticationAPI.requestTokenEndpoint`). This token is
then sent with every tracked session to the tracking API. This token is stored
in the cookie for next sessions. Thus, the real
user remains anonymous while the tracked data has an increased value.

This plug-in also allows to set a
`tracking.apiConfig.authenticationAPI.validateTokenEndpoint`. This is used when
a user token already exists in a cookie or the local storage. The existing token
is sent via `POST` in the request body (`{ user_token: 'a-nice-user-token' }`)
to this endpoint and expects a result like this:

```jsonc
{
  "valid": true, // or false, depending on whether the token is valid or not.
}
```

If the API deems the token as invalid, a new token is requested. This mechanism
ensures that the cookie was not manually generated and still exists on the
platform the associated tracking data is sent to.

Also, this mechanism allows the expiration of a token if desired.

It is also possible to leave out the `validationTokenEndpoint` although it is
not recommended.

The `generateTokenEndpoint` (thus, the entire `authenticationAPI` option) option
can be left out as well. The plug-in will work despite these options not being
set and send tracking data to the tracking API. However, since no user token
will be sent with each tracking request, the data collected will be completely
anonymous.

#### The Consent Banner

The consent banner is displayed at the top of the presentation if enabled:

The consent banner should be filled with informations to conform the GDPR like:
 - Cookies that are saved
 - Data processing that is done
 - Storage duration of data
 - Information regarding pseudonymization

Any styles, HTML classes and texts for the consent banner can be configured. See
[Advanced Usage](#advanced-usage).

The person gives her consent by clicking on the button "I'd like that!". If so,
the user token is requested from the authentication API if this options is
enabled. If not, the given consent is saved: Only with a given consent will the
plug-in send data to the tracking API (don't worry, any data is tracked
client-side prior to the consent being given nonetheless).

If you have an own consent banner, you can disable this one:

```javascript
{
  ...,
  tracking: {
    ...,
    consentBanner: false,
    ...
  },
  ...
}
```

But keep in mind, that you have to tell this plug-in when a consent has been
given. Simply do that by calling:

```javascript
Reveal.getPlugin('tracking').giveConsent();
```

or to remove the consent:

```javascript
Reveal.getPlugin('tracking').removeConsent();
```

### Advanced Usage

Here are list of configuration options with their defaults:

| configuration option                                | default value                                                            | explanation                                                                                                                                                                                     |
|-----------------------------------------------------|--------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `apiConfig.authenticationAPI.validateTokenEndpoint` | `undefined`                                                              | *optional*: API URL to validate existing user token                                                                                                                                       |
| `apiConfig.authenticationAPI.generateTokenEndpoint` | `undefined`                                                              | *optional*: API URL to request user token from                                                                                                                                            |
| `apiConfig.trackingAPI`                             | `undefined`                                                              | API URL where to transmit tracking data to                                                                                                                                                      |
| `consentBanner.closeButton`                         | `{ class: 'content-banner--close', text: '&times;' }`                    | configuration for close button of consent banner                                                                                                                                                |
| `consentBanner.consentButton`                       | `{ class: 'content-banner--button', text: 'I\'d like that!' }`           | configuration for consent button of consent banner                                                                                                                                              |
| `consentBanner.infoText`                            | `'This presentation uses pseudonymous tracking for Learning Analytics.'` | info text for consent banner                                                                                                                                                                    |
| `consentBanner.moreLink`                            | `{ class: 'consent-banner--more-link', text: 'Learn more' }`             | configuration for 'Learn more' link of consent banner (**The `href` option is necessary if the consent banner is enabled**)                                                                     |
| `dwellTimes`                                        | `true`                                                                   | whether to track dwell times. You can configure whether to track dwell times per slide and total dwell time by setting `dwellTimes.perSlide` and `dwellTimes.total` to `true` or `false`        |
| `links`                                             | `true`                                                                   | whether to track clicks on links. You can configure whether to track clicks on internal links (pointing to slides) and external links by setting `links.internal` and `links.external` to `true` or `false` |
| `media`                                             | `true`                                                                   | whether to track interactions on audios and videos. You can configure whether to track interactions on audios and videos by setting `media.audio` and `media.video` to `true` or `false`        |
| `slideTransitions`                                  | `true`                                                                   | whether to track slide transitions                                                                                                                                                              |
|`shortcuts`										| `true` 								 |whether to track shortcuts
|`shortCutsToTrack`									| `['shift-?']`  					|which shortcuts to track
| `revealDependencies.quiz`                           | `false`                                                                  | whether to track events in reveal.js plug-in [reveal.js-quiz](https://gitlab.com/schaepermeier/reveal.js-quiz)                                                                                  |

#### Hints

##### Audios and Videos

If you want to track audio and video events (play/pause), both video and audio
tags need a DOM ID in this format:

```javascript
/(audio|video)player-%horizontalIndex%-%verticalIndex%(-%mediaIndex%)?>/
```

For instance, on a slide with a horizontal index of 4 and a vertical index of 2,
the second audio file has the following ID: `audioplayer-4-2-1`. (The
`mediaIndex` starts at `0`.)

The plug-in
[audio-slideshow](https://github.com/rajgoel/reveal.js-plugins/tree/master/audio-slideshow)
does that automatically for audios.

For videos you need to this manually.

##### Quizzes

If you want to track quizzes, here are the conditions:

- this plug-in needs to be in the `dependencies` section *after* the quiz
  plug-in
- when adding the quiz plug-in to the `dependencies`, do not set `async` to
  `true` and do not provide the `callback`. Simply put: `{ src: 'plugin/quiz/quiz.js' }`
  before `{ src: 'plugin/tracking/tracking.js' }`
- instead, provide the configuration options for the quiz plug-in in a `quiz`
  section when initializing reveal.js:

```javascript
Reveal.initialize({
  ...,
  dependencies: [
    ...,
    { src: 'plugin/quiz/quiz.js' },
    { src: 'plugin/tracking/tracking.js' },
    ...,
  ],
  ...,
  tracking: ...,
  quiz: {
    ...,
    preventUnanswered: true,
    skipStartButton: false,
  }
});
```

- make sure that the option `skipStartButton` is set to `false`. Otherwise the
  start event cannot be tracked

#### Default Configuration

```javascript
{
  apiConfig: {},
  consentBanner: {
    closeButton: {
      class: 'consent-banner--close',
      text: '&times;',
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
  links: true,
  media: true,
  slideTransitions: true,
  shortCuts: true,  
  shortCutsToTrack: ['shift-?'],
  revealDependencies: {
    quiz: false,
  },
}
```

### Request Body to Tracking API

This is a sample request body in JSON format that is be sent to the tracking
API. There is only one request per session and this is sent when the user closes
the presentation (event `window.onpagehide`).

```jsonc
 {
	\\ list with 10 events
   "timeline":[
      {
         "type":"dwellTimePerSlide",
         "dwellTime":"00:00:05",
         "absolute_url":"http://localhost:8000/demo/#/",
         "dateTime":"2022-09-26T05:40:50.471Z"
      },
      {
         "type":"slideTransition",
         "transitionDetails":{
            "vertical":0,
            "horizontal":1
         },
         "timestamp":"00:00:05",
         "absolute_url":"http://localhost:8000/demo/#/",
         "dateTime":"2022-09-26T05:40:50.471Z"
      },
      {
         "type":"dwellTimePerSlide",
         "dwellTime":"00:00:00",
         "absolute_url":"http://localhost:8000/demo/#/1",
         "dateTime":"2022-09-26T05:40:50.950Z"
      },
      {
         "type":"slideTransition",
         "transitionDetails":{
            "vertical":0,
            "horizontal":1
         },
         "timestamp":"00:00:05",
         "absolute_url":"http://localhost:8000/demo/#/1",
         "dateTime":"2022-09-26T05:40:50.950Z"
      },
      {
         "type":"shortcut",
         "shortcut":"control-shift-f",
         "absolute_url":"http://localhost:8000/demo/#/2",
         "dateTime":"2022-09-26T05:40:52.684Z"
      },
      {
         "type":"shortcut",
         "shortcut":"shift-?",
         "absolute_url":"http://localhost:8000/demo/#/2",
         "dateTime":"2022-09-26T05:40:53.955Z"
      },
      {
         "type":"shortcut",
         "shortcut":"shift-?",
         "absolute_url":"http://localhost:8000/demo/#/2",
         "dateTime":"2022-09-26T05:40:54.827Z"
      },
      {
         "type":"shortcut",
         "shortcut":"shift-?",
         "absolute_url":"http://localhost:8000/demo/#/2",
         "dateTime":"2022-09-26T05:40:55.244Z"
      },
      {
         "type":"shortcut",
         "shortcut":"shift-?",
         "absolute_url":"http://localhost:8000/demo/#/2",
         "dateTime":"2022-09-26T05:40:55.644Z"
      },
      {
         "type":"dwellTimePerSlide",
         "dwellTime":"00:00:07",
         "absolute_url":"http://localhost:8000/demo/#/2",
         "dateTime":"2022-09-26T05:40:57.958Z"
      }
   ],
   \\ metadata
   "presentationUrl":"http://localhost:8000/demo/",
   "totalNumberOfSlides":12,
   "userToken":"3265557c-cfe4-47e2-8420-0fa5c084e9e1",
   "sessionToken":"ad900d31-c092-4070-a6d8-d99b04038a90"
}
```
## Django dashboard

The django application provides a basic dashboard visualizing tracked data from the [plugin](#reveal.js-tracking-plugin). Following visualizations are provided:
 - Trend analysis on number of sessions, unique users, and new users
 - Slide usage behaviour
 - Quiz usage & performance
 - Shortcut usage

### Usage

For a customized usage the `settings.py` file at Django/Django has to be configured. 
For an in-depth guide how to adjust that file check out the [Django documentation](https://docs.djangoproject.com/en/4.1/ref/settings/).

To start using the dashboard you have to create structural DB objects. To do go into the Django admin view at http://localhost:8910/admin/ and create entries for `TimePeriod`,  `Module`, and `Course` that fit your educational use case. Additionally create a `SlideSet` for each reveal.js presentation you want to track.

The dashboard allows to filter regarding `Course` and `SlideSet` objects.

## License

MIT licensed

Copyright (C) 2022 Fabian Ingenhorst
