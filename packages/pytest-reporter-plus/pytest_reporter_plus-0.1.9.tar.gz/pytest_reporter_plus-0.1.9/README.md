# 🧪 pytest-reporter-plus

A powerful, plug-and-play Pytest plugin to generate **HTML + JSON reports**, detect **flaky tests**, and optionally **send reports via email**. Works beautifully with or without `xdist`.

---

## ✨ Features

🧩 Unified Test Reports: Get a single, easy-to-read HTML report summarizing all your test results — no hassle, just clarity.

🔄 Flaky Test Detection: Automatically flags flaky tests so you can spot and fix inconsistent failures quickly.

![Screenshot 2025-05-28 at 3 43 17 PM](https://github.com/user-attachments/assets/6fd7a419-58c1-4651-96f7-093ced1f02ee)

📸 Screenshot Support: View screenshots directly in the report to understand failures faster.

📝 Comprehensive output capture: All your test logs with loggers, print() statements, and screenshots are automatically captured and embedded in the report...

![ezgif-744a5d34a4c46d](https://github.com/user-attachments/assets/209cd2c0-d33b-48ec-b58b-8c8991ce35be)

📧 Email Test Reports: Send your reports via email effortlessly using SendGrid integration.

![Screenshot 2025-05-28 at 4 38 49 PM](https://github.com/user-attachments/assets/3f40e206-5dfd-45e9-a511-4dd206cf3318)

🐢 Spot Slow Tests: Highlights the slowest tests so you know where to optimize your suite.

![ezgif-64896277dcf8f8](https://github.com/user-attachments/assets/f5616a07-0dd9-40ed-aa9a-cf9adee3a0b8)

⏱️ Sort & Filter: Easily sort tests by duration or filter by custom tags and skip status to focus on what matters.

![ezgif-3056394be0e9a4](https://github.com/user-attachments/assets/bb60c50a-4709-42f3-8571-19cbd76a93cf)

---

##  Why use pytest-reporter-plus?
Stop wasting time writing and maintaining custom pytest reporter hooks like pytest_runtest_makereport!
With pytest-reporter-plus, you get a beautiful, lightweight HTML report out of the box — no extra coding needed.

Just install, run your tests, and let the plugin handle all the reporting magic. Focus on what matters: writing and running your tests.



## 🚀 Installation

```bash
pip install pytest-reporter-plus
# or with Poetry
poetry add --dev pytest-reporter-plus
```


## 🧾 Usage
Generate HTML + JSON reports:

```bash
pytest -p pytest_reporter_plus.plugin --json-report
```
You’ll get:

report.html – a clean, styled HTML report

playwright_report.json – structured data for integrations

## Available Options
| Option                  | Description                                                        | Default                  | Choices                  |
| ----------------------- | ------------------------------------------------------------------ | ------------------------ | ------------------------ |
| `--json-report`         | Path to save individual JSON test reports                          | `playwright_report.json` | *Any valid file path*    |
| `--automation-tool`     | Specify automation tool used for testing                           | `playwright`             | `playwright`, `selenium` |
| `--capture-screenshots` | When to capture screenshots                                        | `failed`                 | `failed`, `all`, `none`  |
| `--html-output`         | Directory to output HTML reports                                   | `report_output`          | *Any valid directory*    |
| `--screenshots`         | Directory where screenshots will be stored                         | `screenshots`            | *Any valid directory*    |
| `--send-email`          | Send HTML report via email after the test run                      | `False`                  | `True`, `False`          |
| `--detect-flake`        | Detect flaky tests based on reruns in the current or last few runs | `False`                  | `True`, `False`          |


## 🔁 Flaky Test Detection
If a test is retried multiple times (e.g. due to a --reruns plugin), the report will flag it as FLAKY.

In the HTML report, you’ll see a badge like:

![Screenshot 2025-05-28 at 3 43 17 PM](https://github.com/user-attachments/assets/6fd7a419-58c1-4651-96f7-093ced1f02ee)


## 📧 Email Report (Optional)
Send the HTML report via email using --send-email.

### Setup Environment Variables
Create an emailenv file in your project folder that has the following

```commandline
sender_email=you@example.com
recipient_email=team@example.com
report_path=report.html
subject=Your Test Report
smtp_server=smtp.sendgrid.net
smtp_port=587
email_password=your_sendgrid_api_key

```

## Run
```commandline
pytest --send-email
```

## 🤝 Contributions
PRs, issues, and feature requests are welcome! Let's make this tool more awesome together.

### Setting up the project is pretty simple
```
docker build -t pytest-reporter-plus .
docker run -it pytest-reporter-plus /bin/bash 
```

## 📛 Naming
Why pytest-reporter-plus?

Because it does more than just reporting – it’s your enhanced test summary companion ✨


## 📜 License

MIT
