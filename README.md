# Bijar CKB Spellchecker

[![Wikipedia Project Page](https://img.shields.io/badge/Project%20Page-Wikipedia-blue)](https://ckb.wikipedia.org/wiki/Wikipedia:Bijar)
[![Discussion](https://img.shields.io/badge/Discussion-ckb.wiki%20Talk%20Page-blue)](https://w.wiki/Fy4N)
[![GitHub contributors](https://img.shields.io/github/contributors/KurdishWikipedia/bijar)](https://github.com/KurdishWikipedia/bijar/graphs/contributors)
[![GitHub stars](https://img.shields.io/github/stars/KurdishWikipedia/bijar)](https://github.com/KurdishWikipedia/bijar/stargazers)
[![Project Status: In Development](https://img.shields.io/badge/status-in%20development-blue.svg)](https://github.com/KurdishWikipedia/bijar/)
[![GitHub last commit](https://img.shields.io/github/last-commit/KurdishWikipedia/bijar)](https://github.com/KurdishWikipedia/bijar/commits/main)
[![GitHub issues](https://img.shields.io/github/issues/KurdishWikipedia/bijar)](https://github.com/KurdishWikipedia/bijar/issues)
[![Repo size](https://img.shields.io/github/repo-size/KurdishWikipedia/bijar)](https://github.com/KurdishWikipedia/bijar)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Powered by Flask](https://img.shields.io/badge/powered%20by-Flask-blue.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/database-MariaDB-blue.svg)](https://mariadb.org/)
[![Toolforge](https://img.shields.io/badge/Tool-Toolforge-blue.svg)](https://toolforge.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!IMPORTANT]
> This project is under development. The dictionary is incomplete, features are subject to change, and occasional bugs are expected.

**Bijar** is a spellchecking tool for the [Central Kurdish Wikipedia](https://ckb.wikipedia.org/), delivered as an open-source Flask webservice and a MediaWiki gadget. It is designed to help editors improve article quality by identifying and correcting spelling errors.

The name "Bijar" (بژار) is a Kurdish word for "weeding," reflecting the tool's purpose of cleaning mistakes from text.

<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Screenshot_of_a_new_spellchecker_gadget_for_CKB_Wikipedia_-_community_consultation.png/800px-Screenshot_of_a_new_spellchecker_gadget_for_CKB_Wikipedia_-_community_consultation.png" alt="Screenshot of the Bijar spellchecker gadget in action">
</p>
<p align="center">
  <em>The Bijar gadget integrated with Wikipedia's Wikitext 2010 editor, showing its options and a list of misspelled words with suggestions.</em>
</p>
<p align="center">
  <small>Screenshot by the project author. Licensed under <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a> via <a href="https://commons.wikimedia.org/wiki/File:Screenshot_of_a_new_spellchecker_gadget_for_CKB_Wikipedia_-_community_consultation.png">Wikimedia Commons</a>.</small>
</p>

## Features

*   **Spellcheck Engine:** Identifies potential spelling errors in Central Kurdish text.
*   **Kurdish Morphology:** Recognizes complex verb tenses, conjugations, and affixes to improve accuracy.
*   **Correction Suggestions:** Provides a list of suggestions for each identified error.
*   **Community Dictionary:** Allows users to request new words to be added.
*   **Wikipedia Gadget:** Integrates directly into the ckb.wikipedia.org editing interface for eligible users.
*   **Public Database:** Data can be queried directly using Wikimedia's [Quarry](https://quarry.wmflabs.org/) and [Superset](https://superset.wmflabs.org/) tools. The database name is `s57137__bijar_p`.
*   **Public REST API:** Offers a simple endpoint for use in other applications.

## Usage on Wikipedia

This tool is used as a gadget on the Central Kurdish Wikipedia. To learn how to enable and use it, please read the [official documentation on Wikipedia](https://w.wiki/Ftry).

> [!NOTE]
> The gadget is currently available only in the **[Wikitext 2010 editor](https://www.mediawiki.org/wiki/Extension:WikiEditor)**.

## How It Works (Backend + Gadget)

For eligible users on ckb.wikipedia.org, the tool provides a complete, semi-automatic workflow.

1.  **Activation:** An eligible editor enables the Bijar gadget in their MediaWiki preferences.
2.  **Analysis:** The user clicks a button in the editor, which sends the article's wikitext to the Bijar backend service.
3.  **Response:** The backend analyzes the text, identifies potential errors, and returns a structured list of these errors along with correction suggestions back to the user.
4.  **Review and Correction:** The gadget displays the results in a window below the editor. The user can then interact with this list to make corrections:
    *   Clicking a misspelled word in the list automatically finds and selects it in the main editor.
    *   A dropdown menu next to each word provides a list of correction suggestions to choose from.

### Gadget Options

The official gadget has several features and behaviors:

*   **Positional Awareness:** The gadget identifies words by their start and end positions. If the text is edited manually, these positions can become incorrect. The gadget will show a notification prompting the user to refresh. If the live update option is enabled, it refreshes automatically.
*   **User Settings:** The gadget UI allows users to configure several options:
    *   **Live Update:** If enabled, the spellcheck is triggered automatically after key presses or edits, keeping results constantly updated, but increasing API requests.
    *   **Safe Mode:** Enabled by default, this mode prevents checking text inside templates, link targets, file names and categories to avoid breaking them. It can be disabled by trusted users, but must be used with caution.
    *   **Suggestion Controls:** Users can set the maximum number of suggestions (1-10) and the [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance) (1-3) for finding matches.
    *   **Other Options:** Includes toggles for handling bad words and grouping duplicate errors.

## Public API

The Bijar webservice provides a public API endpoint for getting spelling suggestions, which **carefully** can be used in other projects or custom user scripts

### Get Suggestions

This endpoint returns a JSON object containing a list of suggestions for a given word.

**URL:** `GET https://bijar.toolforge.org/api/get_suggestions`

**Parameters:**

| Parameter  | Type    | Description                                                 |
| :--------- | :------ | :---------------------------------------------------------- |
| `word`     | string  | **Required.** The word to check.                            |
| `limit`    | integer | *Optional.* Max number of suggestions. Range: 1-10. Default: 5. |
| `distance` | integer | *Optional.* [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance). Range: 1-3. Default: 2.       |

**Example Request:**
```
https://bijar.toolforge.org/api/get_suggestions?word=کورشی&limit=10&distance=2
```

**Example Response:**
```json
{
  "distance_used": 2,
  "limit_used": 10,
  "suggestions": [
    "کوردی",
    "کورسی",
    "کورتی",
    "کوشتی",
    "کوێری",
    "کرێشی",
    "کەوشی",
    "کورد",
    "کوردەشی",
    "کورتەشی"
  ],
  "word": "کورشی"
}
```

## Setup

This repository contains the source code for the **webservice (backend)**. Follow the instructions below to set it up for local development or for production on Toolforge.

---

<details>
<summary><b>Local Development</b></summary>

### Prerequisites

Before you begin, ensure you have the following software installed on your local machine:
*   **Git:** A version control system. [Download Git](https://git-scm.com/downloads)
*   **Python:** Version 3.10 or newer. [Download Python](https://www.python.org/downloads/)
*   **MySQL/MariaDB:** A local database server (e.g., XAMPP, WAMP, MAMP, or a direct installation).

### Instructions

**1. Clone the Repository**
```bash
git clone https://github.com/KurdishWikipedia/bijar.git
```

**2. Create Virtual Environment & Install Dependencies**
Open a terminal and create a virtual environment inside the `www/python/` directory.
```bash
python -m venv www/python/venv
```
Next, activate the environment.
*   **Windows (Command Prompt):** `.\www\python\venv\Scripts\activate.bat`
*   **Windows (PowerShell):** `.\www\python\venv\Scripts\Activate.ps1`
*   **macOS & Linux (bash/zsh):** `source www/python/venv/bin/activate`

Now, install the required packages:
```bash
pip install -r requirements.txt
```
Finally, deactivate the environment:
```bash
deactivate
```

**3. Set Up the Database**

*   Start your local MySQL/MariaDB server.
*   Create a new database (e.g., `local_database`). You can do this through your database program's GUI or with a command-line client:
    ```sql
    CREATE DATABASE local_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    ```
*   **Database File:** The database dump (`.sql` file) is required. To obtain it, please contact the project maintainer on [their Wikipedia user talk page](https://w.wiki/4DgW). Once you have the file, import it into the database you just created.

**4. Configure Environment Variables**

Navigate to the application's source directory:
```bash
cd www/python/src
```
Copy the sample environment file:
```bash
# On Windows
copy .env.sample .env

# On macOS & Linux
cp .env.sample .env
```
Open the new `.env` file and edit the variables to match your local database setup, following the instructions within the file.

**5. Generate Word Statistics**

> **Note:** This script pre-caches word statistics in a JSON file for the home page, preventing a startup timeout on Toolforge and ensuring the application runs efficiently in both local and production environments.

Activate the virtual environment:
*   **Windows (Command Prompt):** `.\www\python\venv\Scripts\activate.bat`
*   **Windows (PowerShell):** `.\www\python\venv\Scripts\Activate.ps1`
*   **macOS & Linux (bash/zsh):** `source www/python/venv/bin/activate`

With your local database server running, execute the script:
```bash
python run.py generate_stats.py
```
After it completes, deactivate the environment:
```bash
deactivate
```

**6. Get the Gadget Source Code**

**[Gadget JS/CSS source code](#gadget-source-code)**

To test changes locally, you can use a browser extension like [Tampermonkey](https://www.tampermonkey.net/) to inject your local JS/CSS files into live Wikipedia pages.

**Important Browser Security Note:** When developing locally, the gadget runs on `https://ckb.wikipedia.org` while your Flask server runs on `http://127.0.0.1`. Modern browsers block this cross-origin request by default (CORS policy). You may need to temporarily disable web security features in your browser to allow `flask-cors` to work. **This is for local development only and should be handled with care.**


**7. Run the Application**

From the **root directory** of the project (`bijar/`), use the provided helper scripts, which automatically activate the virtual environment and start the Flask server.

*   **On Windows (cmd/PowerShell):**
    ```bash
    .\run.bat
    ```
*   **On macOS, Linux, or Git Bash:**
    ```bash
    ./run.sh
    ```

The application will be available at `http://127.0.0.1:5000` and `http://localhost:5000`.


</details>

<details>
<summary><b>Toolforge Production</b></summary>

*(Replace `<username>`, `<tool_name>`, and `<database_name>` with your credentials.)*

**1. Connect to Toolforge**
```bash
ssh <username>@login.toolforge.org
become <tool_name>
```

**2. Clone the Repository**
```bash
git clone https://github.com/KurdishWikipedia/bijar.git .
```

**3. Create Virtual Environment & Install Dependencies**

See the official documentation on [Python Virtual Environments and Packages on Toolforge](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Web/Python#Virtual_Environments_and_Packages) for more details.
```bash
toolforge webservice python3.13 shell
mkdir -p $HOME/www/python
python3 -m venv $HOME/www/python/venv
source $HOME/www/python/venv/bin/activate
pip install --upgrade pip wheel
pip install -r $HOME/requirements.txt
exit
```

**4. Set Up the Database on Toolforge**

See the [Toolforge ToolsDB documentation](https://wikitech.wikimedia.org/wiki/Help:Toolforge/ToolsDB) for more information.
```bash
# Connect to MariaDB
sql tools
# Create the database
CREATE DATABASE <database_name>;
# Verify creation
SHOW DATABASES;
# Exit the MariaDB prompt
exit
```

Upload your `local_database.sql` file from your computer to your tool's home directory. In a new local terminal:
```bash
scp local_database.sql <username>@tools-login.wmflabs.org:/data/project/<tool_name>/
```

From your Toolforge shell, verify the upload and import the data:
```bash
# Verify the file exists
ls -l *.sql
# Import the SQL file into your tool's database
mysql --defaults-file=$HOME/replica.my.cnf -h tools.db.svc.wikimedia.cloud <database_name> < /data/project/<tool_name>/local_database.sql
# No output indicates success.
```

Check that the tables were imported successfully:
```bash
sql tools
USE <database_name>;
SHOW TABLES;
# You should see all tables now.
exit
```
(Optional but recommended) Remove the SQL file after import. Toolforge advises against storing backups permanently on the platform.
```bash
cd ~
rm local_database.sql
```

**5. Configure Environment Variables**
```bash
cd www/python/src
cp .env.sample .env
# Edit .env by following it's instructions.
```
After editing, secure the file:
```bash
chmod 600 .env
```

**6. Generate Word Statistics**

> **Note:** To prevent a startup timeout on Toolforge, this script pre-caches word statistics in a JSON file for the home page.

Activate the virtual environment:
```bash
source www/python/venv/bin/activate
```
Run the script manually to generate the statistics. This process can be slow on Toolforge, depending on the size of the database.
```bash
python run.py generate_stats.py
```
After the script finishes, deactivate the environment:
```bash
deactivate
```

> **TIP:** Since this script's execution is slow on Toolforge, it is more efficient to automate it with a scheduled [cron job](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Running_jobs) rather than running it manually.

**7. Start the Webservice**
```bash
toolforge webservice python3.13 start
```

### Backing Up the Database from Toolforge

See the [official documentation about backups](https://wikitech.wikimedia.org/wiki/Help:Toolforge/ToolsDB#Backups) for details.
> **Note:** Toolforge does not recommend storing backups on the platform permanently.

**1. Export:** Run this command to create a private SQL dump. The file will be saved in your tool's home (`$HOME`) directory.
```bash
# use umask to make the dump private (use unless the database is public)
toolforge jobs run --command 'umask o-r; ( mariadb-dump --defaults-file=$TOOL_DATA_DIR/replica.my.cnf --host=tools-readonly.db.svc.wikimedia.cloud <database_name> > $TOOL_DATA_DIR/<database_name>-$(date -I).sql )' --image mariadb backup --wait
```
Verify the file was created using `ls -l *.sql` from the `$HOME` directory.

**2. Download:** From your local PC's terminal, use `scp` to download the file.
```bash
scp <username>@login.toolforge.org:/data/project/<tool_name>/<database_name>-YYYY-MM-DD.sql .
```

</details>

## Gadget Source Code

The source code for the user interface (the **gadget**) is hosted directly on the Central Kurdish Wikipedia.

*   **JavaScript:** [MediaWiki:Gadget-Bijar.js](https://ckb.wikipedia.org/wiki/MediaWiki:Gadget-Bijar.js)
*   **CSS:** [MediaWiki:Gadget-Bijar.css](https://ckb.wikipedia.org/wiki/MediaWiki:Gadget-Bijar.css)
*   **Definition:** [MediaWiki:Gadgets-definition](https://ckb.wikipedia.org/wiki/MediaWiki:Gadgets-definition)


## Contributing

The best place to report bugs, request features, or discuss ideas is the **[project's talk page on ckb.wikipedia.org](https://w.wiki/Fy4N)**.

Alternatively, you can open an issue or submit a pull request on GitHub.

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.