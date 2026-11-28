# japan-ir-index
Japan IR Index — Japanese and English corporate disclosure research frontend.
# Language selection

The packaged frontend selects Japanese or English at the neutral homepage from browser
preferences, remembering explicit choices made through the header language switch.
Direct language links remain in their requested edition. The build and packaging hooks
are maintained on the source repository's `claude/japan-ir-continuation-gj9jmm` branch.

## Publishing a story

Whenever a story is published, add it to the Japanese and English article archives
and feeds with its publication date and edition-specific link. The Pages build uses
each feed to show the four newest stories on the corresponding homepage, including
the featured story. Before uploading the site, it checks that every story under
each edition’s insights directory appears in its archive and feed.
