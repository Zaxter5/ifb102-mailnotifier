import talkey
tts = talkey.Talkey(
    # These languages are given better scoring by the language detector
    # to minimise the chance of it detecting a short string completely incorrectly.
    # Order is not important here
    preferred_languages=['en', 'af', 'el', 'fr'],

    # The factor by which preferred_languages gets their score increased, defaults to 80.0
    preferred_factor=80.0,

    # The order of preference of using a TTS engine for a given language.
    # Note, that networked engines (Google, Mary) is disabled by default, and so is dummy
    # default: ['google', 'mary', 'espeak', 'festival', 'pico', 'flite', 'dummy']
    # This sets eSpeak as the preferred engine, the other engines may still be used
    #  if eSpeak doesn't support a requested language.
    engine_preference=['espeak'],

    # Here you segment the configuration by engine
    # Key is the engine SLUG, in this case ``espeak``
    espeak={
        # Specify the engine options:
        'options': {
            'enabled': True,
        },

        # Specify some default voice options
        'defaults': {
                'words_per_minute': 150,
                'variant': 'f4',
        },

        # Here you specify language-specific voice options
        # e.g. for english we prefer the mbrola en1 voice
        'languages': {
            'en': {
                'voice': 'english-mb-en1',
                'words_per_minute': 130
            },
        }
    }
)
tts.say('Old McDonald had a farm')