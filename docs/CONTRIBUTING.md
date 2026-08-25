# 🤝 Руководство для контрибьюторов (Contributing Guidelines)

Мы приветствуем вклад сообщества в развитие **Antigravity Unlocker**! Проект является полностью открытым, и вы можете предлагать улучшения, новые функции или добавлять проверенные стабильные узлы прокси.

---

## 🚀 Как внести свой вклад

1. **Форкните репозиторий** на GitHub.
2. Создайте новую ветку:
   ```bash
   git checkout -b feature/awesome-improvement
   ```
3. Внесите изменения и протестируйте их:
   ```powershell
   python tools/diagnostics.py
   ```
4. Закоммитьте изменения с понятным сообщением (по стандарту Conventional Commits):
   ```bash
   git commit -m "feat: add new verified EU SNI proxy nodes"
   ```
5. Отправьте Pull Request в ветку `main`.

---

## 📋 Правила добавления новых прокси-узлов в `PROXIES_POOL`

Если вы хотите предложить новый зарубежный SNI-прокси в [`tools/proxy_manager.py`](../tools/proxy_manager.py):
* Узел должен поддерживать сквозной TLS (порт 443) для домена `cloudcode-pa.googleapis.com`.
* Задержка (ping) не должна превышать 600 мс из европейской части РФ.
* Узел не должен требовать авторизации или внедрять сторонние сертификаты (чистый TCP/TLS Passthrough).
