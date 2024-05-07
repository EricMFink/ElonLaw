---
layout: page
title: Teaching
permalink: /teaching/
---
{% for class in site.data.classes %}

<div class="image-container">
	<img src="{{ site.baseurl }}/assets/img/teaching/{{ class.img }}" alt="{{ class.title }}">
	<div class="overlay-text"><a href="{{ site.url }}/{{ class.url }}">{{ class.title }}</a></div>
</div>

{% endfor %}