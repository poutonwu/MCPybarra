### 1. **MCP Tools Plan**

#### a. `git_init`
- **Description**: Initializes a new Git repository in the specified directory.
- **Parameters**:
  - `directory` (str): The path where the Git repository will be initialized.
- **Return Value**: A string indicating the success or failure of the initialization.

#### b. `git_status`
- **Description**: Displays the current state of the Git repository, including untracked, modified, and staged files.
- **Parameters**:
  - `directory` (str): The path to the Git repository.
- **Return Value**: A string containing the status information.

#### c. `git_add`
- **Description**: Adds specified files to the Git staging area.
- **Parameters**:
  - `directory` (str): The path to the Git repository.
  - `files` (List[str]): A list of file paths to add to the staging area.
- **Return Value**: A string confirming the files were added or an error message.

#### d. `git_diff_unstaged`
- **Description**: Shows the differences between the working directory and the last commit (unstaged changes).
- **Parameters**:
  - `directory` (str): The path to the Git repository.
- **Return Value**: A string detailing the unstaged differences.

#### e. `git_diff_staged`
- **Description**: Shows the differences between the staging area and the last commit (staged changes).
- **Parameters**:
  - `directory` (str): The path to the Git repository.
- **Return Value**: A string detailing the staged differences.

#### f. `git_diff`
- **Description**: Compares differences between branches, commits, or files.
- **Parameters**:
  - `directory` (str): The path to the Git repository.
  - `source` (str): The source branch, commit, or file.
  - `target` (str): The target branch, commit, or file.
- **Return Value**: A string detailing the differences.

#### g. `git_commit`
- **Description**: Commits the staged changes to the repository with a message.
- **Parameters**:
  - `directory` (str): The path to the Git repository.
  - `message` (str): The commit message.
- **Return Value**: A string confirming the commit or an error message.

#### h. `git_reset`
- **Description**: Unstages files from the staging area.
- **Parameters**:
  - `directory` (str): The path to the Git repository.
  - `files` (List[str]): A list of file paths to unstage.
- **Return Value**: A string confirming the reset or an error message.

#### i. `git_log`
- **Description**: Displays the commit history of the repository.
- **Parameters**:
  - `directory` (str): The path to the Git repository.
- **Return Value**: A string containing the commit history.

#### j. `git_create_branch`
- **Description**: Creates a new branch in the repository.
- **Parameters**:
  - `directory` (str): The path to the Git repository.
  - `branch_name` (str): The name of the new branch.
- **Return Value**: A string confirming the branch creation or an error message.

#### k. `git_checkout`
- **Description**: Switches to a specified branch or commit.
- **Parameters**:
  - `directory` (str): The path to the Git repository.
  - `target` (str): The branch name or commit hash to switch to.
- **Return Value**: A string confirming the checkout or an error message.

#### l. `git_show`
- **Description**: Displays detailed information about a specific commit.
- **Parameters**:
  - `directory` (str): The path to the Git repository.
  - `commit_hash` (str): The hash of the commit to display.
- **Return Value**: A string containing the commit details.

---

### 2. **Server Overview**
The MCP server will provide automated Git repository management functionalities, including initializing repositories, tracking changes, committing updates, managing branches, and viewing commit histories. This server will strictly adhere to the user's request, ensuring all specified Git operations are supported.

---

### 3. **File to be Generated**
- **Filename**: `git_mcp_server.py`

---

### 4. **Dependencies**
- **Python 3.10+**
- **MCP SDK**: `pip install mcp[cli]`
- **GitPython**: `pip install GitPython` (for Git operations)
- **httpx**: `pip install httpx` (for API interactions if needed)