# Kids Comic Library (Powered by AI)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()
[![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)]()
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)]()
[![Gemini](https://img.shields.io/badge/AI-Google_Gemini_1.5-orange.svg)]()

> A robust, Neo-Brutalist web platform designed to generate, manage, and read educational children's comics using the power of Generative AI.

---

## 📑 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Project Architecture](#project-architecture)
3. [Technology Stack](#technology-stack)
4. [Core Features](#core-features)
5. [User Roles & RBAC](#user-roles--rbac)
6. [Design System (Neo-Brutalism)](#design-system-neo-brutalism)
7. [Directory Structure](#directory-structure)
8. [Database Schema](#database-schema)
9. [AI Engine & Prompt Engineering](#ai-engine--prompt-engineering)
10. [Prerequisites & Installation](#prerequisites--installation)
11. [Environment Configuration](#environment-configuration)
12. [Usage Guide](#usage-guide)
13. [Internal API Reference](#internal-api-reference)
14. [Security & Best Practices](#security--best-practices)
15. [Deployment](#deployment)
16. [Contributing Guidelines](#contributing-guidelines)
17. [License & Acknowledgments](#license--acknowledgments)

---

## 🚀 Executive Summary

The **Kids Comic Library** is an end-to-end web application that allows administrators to dynamically generate rich, age-appropriate children's stories with moral lessons using the **Google Gemini AI API**. These generated stories are managed via a robust draft/publish pipeline and presented to parents and children in a highly engaging, colorful, and accessible "Neo-Brutalist" interface. 

Additionally, the platform supports manual PDF comic uploads, seamlessly extracting text for AI analysis and rendering the PDFs natively in the browser without relying on external PDF viewers or new tabs, ensuring a perfectly sandboxed user experience.

---

## 🏗️ Project Architecture

The application follows a monolithic Model-View-Controller (MVC) architectural pattern:

- **Model:** SQLite3 is used as the primary data store, managed through native Python `sqlite3` connectors with custom `detect_types` parsing to handle timestamp conversion automatically.
- **View:** Jinja2 templating engine dynamically renders HTML pages. The UI is strictly governed by a custom CSS framework residing in `style.css` that dictates the Neo-Brutalist aesthetic.
- **Controller:** Flask handles routing, session management (authentication), file uploads (via `werkzeug.utils.secure_filename`), and API interactions with Google Gemini.

The system is highly decoupled between the **Admin Area** (content creation and management) and the **Parent Area** (content consumption).

---

## 💻 Technology Stack

### Backend
* **Python 3.13+**: Core runtime environment.
* **Flask**: Lightweight WSGI web application framework.
* **SQLite3**: Serverless, zero-configuration relational database.
* **Google Generative AI SDK (`google-generativeai`)**: Interfaces with the Gemini 1.5 Flash model for lightning-fast text generation.
* **PyMuPDF (`fitz`)**: Robust PDF parsing and text extraction for manually uploaded comic books.

### Frontend
* **HTML5 & Jinja2**: Semantic markup and dynamic server-side rendering.
* **Vanilla CSS3**: Custom Neo-Brutalist design system utilizing CSS Grid, Flexbox, and CSS Variables.
* **Vanilla JavaScript (ES6)**: DOM manipulation, asynchronous fetching, and PDF rendering.
* **PDF.js (Mozilla)**: Native, canvas-based PDF rendering for a seamless, in-app reading experience.
* **Font Awesome**: Iconography for administrative dashboards.

---

## ✨ Core Features

* **AI Story Generation:** Generate completely unique stories by defining a Theme, Moral, Character, and Target Age.
* **AI Editor Studio:** Perform 20+ specialized AI operations on existing stories (e.g., translate to Spanish, simplify for a 3-year-old, generate reading comprehension questions).
* **Native PDF Previewing:** PDFs are rendered directly into HTML5 `<canvas>` elements using PDF.js, preventing tab hijacking and maintaining UI consistency.
* **Text Extraction:** Automatically parses text from uploaded PDF comics to provide context to the AI Editor Studio.
* **Draft & Publish Workflow:** Administrators can safely edit and review stories as drafts before publishing them to the live library.
* **Advanced Filtering:** Parents can filter the live library by Age, Theme, and Moral.

---

## 🔐 User Roles & RBAC

The application employs Role-Based Access Control (RBAC) via session variables to ensure strict separation of concerns.

### 1. The Administrator (`role: admin`)
* **Access:** `/admin/*`
* **Capabilities:** 
  * Access the Admin Dashboard to view all drafts and published stories.
  * Generate new AI stories.
  * Upload manual PDF/Image comics.
  * Access the AI Editor Studio to manipulate story text.
  * Publish, unpublish, and permanently delete content.

### 2. The Parent (`role: parent`)
* **Access:** `/parent/*`
* **Capabilities:**
  * Access the Parent Dashboard (Library).
  * Filter live stories based on child-specific criteria.
  * Read stories in a distraction-free, beautifully styled reading view.

---

## 🎨 Design System (Neo-Brutalism)

The frontend is built entirely on a custom "Neo-Brutalist" design system. This choice was made to maximize user engagement, especially for a younger demographic, by offering a bold, playful, and highly interactive interface.

**Key Design Principles:**
1. **Stark Contrasts:** Utilitarian white backgrounds juxtaposed against hyper-vivid colors (Cyan, Yellow, Hot Pink, Purple).
2. **Hard Shadows:** Use of solid, non-blurred drop shadows (e.g., `box-shadow: 10px 10px 0px #000;`) to create artificial depth.
3. **Thick Borders:** All interactive elements and containers feature heavy, 3px solid black borders.
4. **Bold Typography:** Utilization of Google Fonts:
   - `Anton` for massive, impactful headers.
   - `Space Grotesk` for highly legible, geometric body text and buttons.
5. **Micro-Interactions:** Elements actively respond to hover states by physically translating down and reducing shadow depth, simulating the pressing of a physical button.

---

## 📁 Directory Structure

```text
unemployment_project/
├── .env                    # Environment variables (IGNORED BY GIT)
├── .gitignore              # Git ignore rules for security and cleanliness
├── app.py                  # MAIN APPLICATION ENTRY POINT (Flask Routes, AI Logic)
├── alter_db.py             # Database migration and utility script
├── database.db             # SQLite database (Generated at runtime)
├── README.md               # Extensive project documentation
├── requirements.txt        # Python dependency list
│
├── static/
│   ├── css/
│   │   └── style.css       # Core Neo-Brutalist design system
│   ├── js/
│   │   └── main.js         # Frontend interactive logic
│   └── uploads/            # Directory for user-uploaded PDF/Image files
│
└── templates/              # Jinja2 HTML Templates
    ├── admin_dashboard.html
    ├── admin_login.html
    ├── ai_editor.html      # Workspace for 20+ AI operations
    ├── base.html           # Global layout, CDN links (PDF.js), and Navigation
    ├── generate_story.html # Form to query the Gemini API
    ├── index.html          # Public landing page
    ├── parent_dashboard.html
    ├── parent_login.html
    ├── preview_story.html  # Admin preview route
    ├── read_story.html     # Parent reading route
    └── upload_story.html   # Manual comic upload interface
```

---

## 🗄️ Database Schema

The database utilizes SQLite3 and is automatically initialized upon the first run of the application.

### Table: `users`
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique user identifier |
| `username` | TEXT | NOT NULL UNIQUE | Login username |
| `password` | TEXT | NOT NULL | Login password (MVP: plaintext) |
| `role` | TEXT | NOT NULL | RBAC role (`admin` or `parent`) |

### Table: `stories`
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique story identifier |
| `title` | TEXT | NOT NULL | Story title |
| `moral` | TEXT | NOT NULL | The primary lesson taught |
| `theme` | TEXT | NOT NULL | Genre or thematic setting |
| `age` | INTEGER | NOT NULL | Target demographic age |
| `character` | TEXT | NOT NULL | Main character description |
| `content` | TEXT | NOT NULL | The actual story text / paragraphs |
| `status` | TEXT | NOT NULL | `draft` or `published` |
| `file_path` | TEXT | NULL | Path to uploaded PDF/Image |
| `is_upload` | INTEGER | DEFAULT 0 | Boolean flag indicating manual upload |
| `extracted_text` | TEXT | NULL | Text extracted via PyMuPDF for AI context |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date of creation |

---

## 🧠 AI Engine & Prompt Engineering

This project heavily leverages **Google's Gemini 1.5 Flash** model for all generative tasks.

### Base Generation Prompt
The core story generation is achieved via strict parameter injection:
```python
prompt = (
    f"Write a short children's comic story for a {age}-year-old. "
    f"The main character is a {character}. "
    f"The theme is {theme}. "
    f"The moral lesson is {moral}. "
    f"The story should be fun, simple, engaging, and end with a clear moral. "
    f"Format the story in short paragraphs. Each paragraph describes one comic panel. "
    f"Include what the illustration would show at the start of each panel description in brackets, e.g. [Illustration: ...]"
)
```

### AI Editor Studio Operations
The AI Editor Studio features a dictionary of over 20 distinct system prompts designed to mutate existing story content. Examples include:
* *"Summarize the story in 3 sentences."*
* *"Simplify the language for a 3-year-old."*
* *"Change the tone to be very humorous and silly."*
* *"Generate 3 reading comprehension questions for children."*

When an action is requested, the system concatenates the specific instruction with the existing text (or PyMuPDF extracted text) and asynchronously streams the result back to the frontend UI.

---

## 🛠️ Prerequisites & Installation

### Prerequisites
1. **Python 3.10+**: Ensure Python and `pip` are installed on your system.
2. **Git**: For cloning the repository.
3. **Google Gemini API Key**: You must obtain a free API key from Google AI Studio.

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rohith2157/unemployment_project.git
   cd unemployment_project
   ```

2. **Create a Virtual Environment (Highly Recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ Environment Configuration

The application requires environment variables to interface with the Gemini API securely.

1. Create a file named `.env` in the root of the project directory.
2. Add your Google Gemini API key to the file exactly as follows:

```env
GEMINI_API_KEY=your_actual_api_key_goes_here
```
> **Security Note:** The `.env` file is heavily guarded by the `.gitignore` rules. Never commit this file to version control to prevent API key leakage.

---

## 🎮 Usage Guide

### Starting the Server
Start the Flask development server by running:
```bash
python app.py
```
The application will be available at `http://127.0.0.1:5000/`.

### Default Credentials
Upon initialization, the database automatically seeds two default users:
* **Admin:** Username: `admin` | Password: `admin123`
* **Parent:** Username: `parent` | Password: `parent123`

### The Workflow
1. Log in as an **Admin**.
2. Navigate to the **Dashboard** and click **Generate AI Comic**.
3. Fill out the parameters and generate the story.
4. Save it as a **Draft**.
5. Open the **AI Editor Studio** to refine the text or translate it.
6. Return to the dashboard and click **Publish**.
7. Log out, and log in as a **Parent**.
8. Navigate the **Library** and read the newly published story in the immersive Neo-Brutalist viewer.

---

## 📡 Internal API Reference

The application features internal RESTful endpoints used by the frontend JavaScript for seamless, page-reload-free interactions.

### `POST /api/ai_action`
Processes an AI manipulation request from the AI Editor Studio.

**Request Payload (JSON):**
```json
{
    "story_id": 12,
    "action_id": 5
}
```

**Success Response (200 OK):**
```json
{
    "result": "The AI generated text goes here..."
}
```

**Error Response (403/404):**
```json
{
    "error": "Unauthorized / Story not found"
}
```

---

## 🛡️ Security & Best Practices

1. **Secure Filenames:** All uploaded files are sanitized using Werkzeug's `secure_filename()` to prevent Directory Traversal attacks (Path Injection).
2. **Parameter Binding:** All SQLite3 database queries utilize strict parameterized binding (`?` operators) to entirely mitigate SQL Injection vulnerabilities.
3. **API Key Security:** API keys are never hardcoded and are strictly loaded from process environment variables via `python-dotenv`.
4. **Sandboxed PDF Rendering:** By utilizing `pdf.js` on HTML5 Canvases instead of standard `<iframe>` tags, the application prevents arbitrary script execution from malicious PDFs and keeps the user securely inside the application context.

---

## ☁️ Deployment

### Local Network Sharing (Ngrok)
To instantly share your local development server with collaborators:
1. Install [Ngrok](https://ngrok.com/).
2. Start your Flask app: `python app.py`
3. In a new terminal, run: `ngrok http 5000`
4. Share the provided HTTPS URL.

### Production Deployment (e.g., Render, Heroku)
1. Update `app.py` to bind to the dynamic port assigned by the host:
   ```python
   port = int(os.environ.get("PORT", 5000))
   app.run(host="0.0.0.0", port=port)
   ```
2. Replace the Flask development server with a production WSGI server like Gunicorn.
3. Add a `Procfile` to the root directory:
   ```text
   web: gunicorn app:app
   ```
4. Set the `GEMINI_API_KEY` in your hosting provider's Environment Secrets dashboard.

---

## 🤝 Contributing Guidelines

We welcome contributions to the Kids Comic Library! Please follow these steps to contribute:

1. **Fork the repository.**
2. **Create a Feature Branch:** `git checkout -b feature/AmazingNewFeature`
3. **Commit your changes:** Ensure your commit messages are descriptive. `git commit -m "Add AmazingNewFeature"`
4. **Push to the Branch:** `git push origin feature/AmazingNewFeature`
5. **Open a Pull Request (PR):** Submit your PR against the `main` branch with a thorough description of your changes.

**Code Style Guidelines:**
* Python code should adhere to PEP-8 standards.
* HTML/CSS additions must strictly follow the established Neo-Brutalist design tokens found in `style.css` (e.g., using `var(--color-primary)` and maintaining 3px solid borders).

---

## 📄 License & Acknowledgments

This project is licensed under the **MIT License**. You are free to modify, distribute, and use this project in private and commercial settings.

**Acknowledgments:**
* Google DeepMind for the incredible Gemini 1.5 model APIs.
* The Mozilla Foundation for maintaining PDF.js.
* PyMuPDF developers for blazing-fast local document parsing.

---
*Developed with dedication by the Open Source Community.*
