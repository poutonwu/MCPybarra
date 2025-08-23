### 1. **MCP Tools Plan**

#### Tool 1: `search_images`
- **Description**: Searches for images based on user-provided keywords from popular image sources such as Unsplash, Pexels, or Pixabay. Returns structured results containing image URLs and author information.
- **Parameters**:
  - `keywords` (str): A string of keywords separated by spaces to search for relevant images.
- **Return Value**: A list of dictionaries, each containing:
  - `image_url` (str): The URL of the image.
  - `author` (str): The name of the author/photographer.

#### Tool 2: `download_image`
- **Description**: Downloads an image from a provided URL and saves it to a specified directory.
- **Parameters**:
  - `image_url` (str): The URL of the image to download.
  - `file_name` (str): The desired file name for the downloaded image.
  - `save_directory` (str): The directory where the image should be saved.
- **Return Value**: A dictionary containing:
  - `status` (str): Indicates success or failure of the operation (e.g., "success" or "failure").
  - `file_path` (str): The full path to the saved image if successful.

#### Tool 3: `generate_icon`
- **Description**: Generates an icon of a specified size based on a description provided by the user. If no cloud-based generation service is configured, it uses a local sample icon.
- **Parameters**:
  - `description` (str): A textual description of the desired icon.
  - `icon_size` (int): The desired size in pixels (e.g., 64 for a 64x64 icon).
  - `save_directory` (str): The directory where the generated icon will be saved.
- **Return Value**: A dictionary containing:
  - `status` (str): Indicates success or failure of the operation (e.g., "success" or "failure").
  - `file_path` (str): The full path to the generated icon if successful.

---

### 2. **Server Overview**
The purpose of this MCP server is to automate image-related tasks including searching, downloading, and generating icons. It provides an interface through which users can retrieve image search results, download specific images, and generate custom-sized icons either via a cloud-based service or locally using sample icons.

---

### 3. **File to be Generated**
All logic will be contained within a single Python file named `mcp_image_server.py`.

---

### 4. **Dependencies**
The following third-party libraries are required:
- `requests`: For making HTTP requests to fetch images and interact with APIs.
- `Pillow` (PIL fork): For generating or resizing icons locally when no cloud-based service is available.
- `httpx`: For asynchronous HTTP requests, if needed for performance optimization during image fetching.