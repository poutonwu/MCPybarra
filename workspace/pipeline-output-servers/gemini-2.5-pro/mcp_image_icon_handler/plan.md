<thought>The second search confirms that the Pillow library is the standard and most straightforward tool for creating an image with text from scratch in Python. This is perfect for the `generate_icon` fallback functionality.

My research is now complete. I have identified the necessary libraries:
1.  `mcp` (from the boilerplate)
2.  `httpx` (from the boilerplate, useful for Unsplash/Pixabay direct API calls)
3.  `pexels-api-py` (for Pexels API)
4.  `Pillow` (for the local icon generation)

I have a clear path for all three requested tools:
-   `search_images`: Use `httpx` for Unsplash/Pixabay and `pexels-api-py` for Pexels. I will need to remind the user to provide API keys, probably via environment variables. The function will merge and standardize results from these sources.
-   `download_image`: Use `httpx` for asynchronous download. It will save the file to a specified directory or a default one.
-   `generate_icon`: Use `Pillow` to create a new image, draw text (the description) onto it, and save it. This will be the fallback if a cloud service isn't configured.

Now I will structure this information into the final Markdown plan as requested.The second search confirms that the Pillow library is the standard and most straightforward tool for creating an image with text from scratch in Python. This is perfect for the `generate_icon` fallback functionality.

My research is now complete. I have identified the necessary libraries:
1.  `mcp` (from the boilerplate)
2.  `httpx` (from the boilerplate, useful for Unsplash/Pixabay direct API calls)
3.  `pexels-api-py` (for Pexels API)
4.  `Pillow` (for the local icon generation)

I have a clear path for all three requested tools:
-   `search_images`: Use `httpx` for Unsplash/Pixabay and `pexels-api-py` for Pexels. I will need to remind the user to provide API keys, probably via environment variables. The function will merge and standardize results from these sources.
-   `download_image`: Use `httpx` for asynchronous download. It will save the file to a specified directory or a default one.
-   `generate_icon`: Use `Pillow` to create a new image, draw text (the description) onto it, and save it. This will be the fallback if a cloud service isn't configured.

Now I will structure this information into the final Markdown plan as requested.Berikut adalah rencana implementasi terperinci untuk server MCP Anda.

### **Server Overview**

Server ini akan berfungsi sebagai alat otomatisasi pemrosesan gambar, menyediakan antarmuka MCP untuk mencari gambar dari sumber-sumber utama, mengunduh gambar dari URL, dan menghasilkan ikon berdasarkan deskripsi. Fungsionalitas ini dirancang untuk diintegrasikan dengan *Large Language Models* melalui protokol MCP.

### **File to be Generated**

Semua logika server akan terkandung dalam satu file Python:
*   `image_mcp_server.py`

### **Dependencies**

Untuk mengimplementasikan fungsionalitas yang diminta, pustaka Python pihak ketiga berikut akan diperlukan:

*   **`mcp`**: Diperlukan untuk kerangka kerja server MCP.
*   **`httpx`**: Untuk melakukan permintaan API asinkron ke Unsplash dan Pixabay, serta untuk mengunduh gambar.
*   **`pexels-api-py`**: Pustaka klien khusus untuk berinteraksi dengan API Pexels.
*   **`Pillow`**: Untuk membuat gambar ikon placeholder secara lokal ketika layanan *cloud* tidak tersedia.

---

### **MCP Tools Plan**

Berikut adalah rincian untuk setiap alat MCP yang akan diimplementasikan.

#### **1. search\_images**

*   **Function Name**: `search_images`
*   **Description**: Mencari gambar secara asinkron berdasarkan kata kunci di beberapa sumber gambar populer (Unsplash, Pexels, Pixabay). Hasil dari berbagai sumber akan digabungkan dan distandarisasi. Memerlukan kunci API yang dikonfigurasi sebagai variabel lingkungan (`UNSPLASH_API_KEY`, `PEXELS_API_KEY`, `PIXABAY_API_KEY`).
*   **Parameters**:
    *   `query` (str): Kata kunci pencarian untuk gambar.
    *   `sources` (Optional[List[str]], default=`['unsplash', 'pexels', 'pixabay']`): Daftar sumber yang akan dicari.
    *   `per_page` (Optional[int], default=`10`): Jumlah hasil yang diinginkan per sumber.
*   **Return Value**:
    *   (dict): Sebuah kamus yang berisi daftar hasil gambar. Kuncinya adalah `results`, dan nilainya adalah daftar kamus, di mana setiap kamus mewakili satu gambar dan berisi kunci-kunci berikut:
        *   `source` (str): Sumber gambar (misalnya, 'unsplash').
        *   `id` (str): ID unik gambar dari sumbernya.
        *   `url` (str): URL langsung ke gambar.
        *   `photographer` (str): Nama fotografer atau pembuat.
        *   `description` (str): Deskripsi atau judul gambar.

#### **2. download\_image**

*   **Function Name**: `download_image`
*   **Description**: Mengunduh gambar dari URL yang diberikan dan menyimpannya ke direktori lokal. Direktori penyimpanan default adalah `./downloads` jika tidak ditentukan lain.
*   **Parameters**:
    *   `image_url` (str): URL gambar yang akan diunduh.
    *   `filename` (str): Nama file untuk menyimpan gambar (termasuk ekstensi).
    *   `save_dir` (Optional[str], default=`'./downloads'`): Direktori tempat menyimpan gambar.
*   **Return Value**:
    *   (dict): Sebuah kamus yang menunjukkan status operasi.
        *   `status` (str): 'success' atau 'error'.
        *   `file_path` (str): Path lengkap ke file yang disimpan jika berhasil.
        *   `message` (str): Pesan kesalahan jika terjadi kegagalan.

#### **3. generate\_icon**

*   **Function Name**: `generate_icon`
*   **Description**: Menghasilkan file gambar ikon. Jika layanan generasi *cloud* tidak dikonfigurasi, fungsi ini akan membuat ikon placeholder lokal menggunakan pustaka Pillow. Ikon placeholder akan berupa gambar dengan warna latar belakang solid dan teks deskripsi di tengahnya.
*   **Parameters**:
    *   `description` (str): Teks deskripsi singkat untuk ditampilkan pada ikon.
    *   `size` (Optional[Tuple[int, int]], default=`(128, 128)`): Dimensi ikon dalam piksel (lebar, tinggi).
    *   `filename` (Optional[str], default=None): Nama file untuk ikon. Jika `None`, nama file akan dibuat secara otomatis dari deskripsi (misalnya, `team_meeting_icon.png`).
    *   `save_dir` (Optional[str], default=`'./icons'`): Direktori tempat menyimpan ikon yang dihasilkan.
*   **Return Value**:
    *   (dict): Sebuah kamus yang menunjukkan status operasi.
        *   `status` (str): 'success' atau 'error'.
        *   `file_path` (str): Path lengkap ke file ikon yang disimpan jika berhasil.
        *   `message` (str): Pesan kesalahan jika terjadi kegagalan.