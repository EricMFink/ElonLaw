---
layout: page
title: Publications
permalink: /publications/
---

{% for publication in site.data.publications %}

{{ publication.author }}, <a href="{{ site.baseurl }}/assets/pdf/{{ publication.pdf }}.pdf" target="_blank">{{ publication.title }}</a>, {% if publication.journal %}{{ publication.volume }} _{{ publication.journal }}_ {{ publication.page }} {% endif %}{% if publication.institution %}{{ publication.institution }} {% endif %}({{ publication.date }})

{% endfor %}