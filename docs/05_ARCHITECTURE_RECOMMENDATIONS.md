# Architecture Recommendations for Enriched Forum Stories

Given your new infrastructure (Contabo VPS + Cloudflare R2), you have vastly more resources and flexibility than you did on Render. Here is the recommended architecture to support the new "Text/Background Node" feature specifically for **Forum / Group Stories**.

## 1. The New "Node-Based" Story Structure

Currently, Stories are likely built around simply uploading an Image or Video file. To support Instagram-style "Text Stories" with customizable backgrounds, the `Story` database model needs to become polymorphic.

### Database Schema Evolution

Update your `Story` model to handle different node types:

```python
class Story(models.Model):
    NODE_TYPES = [
        ('media', 'Image/Video Media'),
        ('text', 'Rich Text Block'),
    ]
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='stories')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    node_type = models.CharField(max_choices=NODE_TYPES, default='media')
    
    # Common Fields
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField() # 24h logic
    
    # For Media Stories (Images/Videos)
    media_file = models.FileField(upload_to='forum/stories/', null=True, blank=True)
    
    # For Text Stories
    text_content = models.TextField(null=True, blank=True)
    background_color = models.CharField(max_length=7, default='#000000') # Hex code
    background_image = models.ImageField(upload_to='forum/stories/backgrounds/', null=True, blank=True)
```

**Benefits:**

- **Flexibility:** When a user clicks "Add Story" in the forum, they can choose between uploading a photo OR writing styled text on a colored background (like Facebook/Instagram status backgrounds).
- **Efficiency:** Saving a hex code and a text string in PostgreSQL takes virtually 0 bytes compared to forcing the client's browser to render an image on a canvas and uploading a 2MB PNG.
- **Client-Side Rendering:** The frontend JavaScript Story Carousel simply reads the JSON. `if (story.type === 'text')`, it creates a `<div>` with the background color and centers the text over it natively.

## 2. Optimizing Uploads on the Contabo VPS

Because Group Stories are uploaded by regular users (not just Admins), you need to protect your server from malicious or excessively large uploads, while also ensuring the experience is fast.

### Step A: Magic Bytes Validation

You must not rely on the [.jpg](file:///c:/Users/Usuario/Documents/Developer/Projects/MangaAnimEden/media/covers/cover.jpg) or `.mp4` file extension when users upload Stories. You must use a Python library like `python-magic` to read the first few bytes of the incoming file to verify it is *truly* an image or video before saving it to your Contabo disk.

### Step B: The "Disk-First" Drop Zone

When Django receives a video or large image for a Story:

- Save the raw upload into a temporary folder on the Contabo SSD (e.g., `/tmp/forum_uploads/`).
- Return a `200 OK` to the user's browser immediately: *"Story is processing..."*

### Step C: Background Optimization (Celery + Redis)

Using a task queue like **Celery** (with Redis as a broker, easily installable on your VPS):

- A background worker picks up the file from the SSD.
- **For Images:** It compresses the image to a standardized WebP format (e.g., max 1080x1920 portrait) using `Pillow`.
- **For Videos:** It could potentially use `ffmpeg` (installed on the VPS) to compress or convert it to an efficient `.mp4` format.
- Finally, it uploads the optimized file to Cloudflare R2 and deletes the local temporary file.
- **Why?** Your web server (Gunicorn) is freed up immediately. Users don't experience timeouts while waiting for Cloudflare to respond, and you save massive amounts of R2 storage space by compressing *before* you upload.

## 3. Optimizing Admin Uploads and Content Management (Manga Chapters)

Because your platform heavily relies on distributing large volumes of image data (Manga Scans), the Admin Panel requires a bulletproof, high-performance architecture. You now have a Contabo VPS with fast NVMe storage and full root control, making this the perfect time to optimize how manga is processed.

### Step A: Client-Side Chunked Uploads

Administrators often upload massive `.cbz` or `.zip` archives (e.g., 500MB+) that contain hundreds of high-res images. To handle this flawlessly:

- The Admin frontend should use a library like **Uppy** or **Dropzone.js** to split these files into small 10MB chunks directly in the browser.
- These chunks are sent iteratively to the server. If the admin's internet dips, the upload simply resumes the interrupted chunk rather than failing the whole 500MB file.

### Step B: The "Disk-First" Unpacking Queue

Previously on Render, processing giant `.cbz` files in memory caused Out-Of-Memory (OOM) crashes.

- Upon receiving the completed archive, Django should save the raw `.cbz` file directly to a temporary high-speed SSD folder (e.g., `/tmp/manga_ingestion/`).
- The Admin interface immediately receives a `200 OK` response with a status of *"Chapter is being processed"*.

### Step C: Asynchronous Processing Pipeline (Celery)

We use a **Celery Worker** (running alongside Django on your VPS) to handle the heavy lifting:

1. **Extraction:** The worker unzips the `.cbz` archive onto the SSD.
2. **Standardization:** It iterates through the images, automatically converting them to an optimized WebP format to drastically reduce sizes without losing quality.
3. **Pipelined R2 Upload:** As each image finishes conversion, the worker streams it up to Cloudflare R2.
4. **Cleanup:** It deletes the local files from the Contabo SSD.
5. **Notification:** A WebSocket (or a simple polling mechanism in the Admin panel) notifies the Admin that "Chapter 45 is now live!"

### Step D: Better Admin Management UI

To make content management precise and fast:

- **Draft Status:** Chapters must be created in a `Draft` state so Admins can review the extracted WebP images before publishing.
- **Bulk Action Tools:** Provide UI tools in the Admin Dashboard to easily reorder pages (Drag & Drop), delete corrupt pages, or inject new pages into the middle of an existing chapter without deleting and re-uploading the entire thing.
