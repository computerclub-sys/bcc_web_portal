import os
import re

tpl_dir = 'portal/templates/portal'

def clean_html(filename):
    path = os.path.join(tpl_dir, filename)
    with open(path, 'r') as f:
        html = f.read()

    # Add load static and csrf
    html = "{% load static %}\n" + html

    # Remove NextJS scripts
    html = re.sub(r'<script[^>]*_next[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    # Remove self.__next_f pushes
    html = re.sub(r'<script>\s*\(?self\.__next_f.*?</script>', '', html, flags=re.DOTALL)
    
    # Preloads and css
    html = re.sub(r'<link rel="preload"[^>]*>', '', html)
    html = re.sub(r'<link rel="stylesheet"[^>]*href="/_next[^>]*>', r'<link rel="stylesheet" href="{% static \'portal/css/style.css\' %}" />', html)

    # Media paths
    html = re.sub(r'(/_next/static/media/[^"\']+)', r"{% static 'portal/media/\1' %}", html)
    html = re.sub(r'/_next/static/media/([^"\']+)', r"{% static 'portal/media/\1' %}", html)

    # favicon
    html = re.sub(r'href="/favicon.ico"', r'href="{% static \'portal/favicon.ico\' %}"', html)

    # Update URLs
    html = re.sub(r'href="/login"', r'href="{% url \'login\' %}"', html)
    html = re.sub(r'href="/register"', r'href="{% url \'register\' %}"', html)

    # Forms
    html = re.sub(r'<form class="([^"]*)">', r'<form class="\1" method="POST" action="">\n{% csrf_token %}', html)

    # Messages block injection right before form
    messages_html = """
    {% if messages %}
    <div class="mb-4">
        {% for message in messages %}
        <div class="p-3 bg-red-500/20 border border-red-500 rounded text-red-100 text-sm mb-2">{{ message }}</div>
        {% endfor %}
    </div>
    {% endif %}
    """
    html = html.replace('<form', messages_html + '<form', 1)

    with open(path, 'w') as f:
        f.write(html)

for f in ['index.html', 'login.html', 'register.html']:
    clean_html(f)

print("Templates cleaned!")
