# 🎁 Return Gift Product Video Generator

Automatically generates 2 promotional videos per day from your product photos
using **Shotstack API** (free tier) + **GitHub Actions** (free).

---

## 📋 One-Time Setup (takes ~20 minutes)

### Step 1 — Create a Shotstack Account (Free)
1. Go to [https://shotstack.io](https://shotstack.io) → Click **Start for Free**
2. Sign up with your email
3. Go to your **Dashboard → API Keys**
4. Copy your **Sandbox API key** (starts with sandbox testing)

### Step 2 — Create a GitHub Repository
1. Go to [https://github.com](https://github.com) → Sign in (or create account)
2. Click **New Repository**
3. Name it: `return-gift-videos`
4. Set it to **Public** ✅ (needed so Shotstack can access your photos via URL)
5. Click **Create repository**

### Step 3 — Upload This Project to GitHub
Upload all files from this folder to your new GitHub repository.
You can use GitHub's web interface:
- Click **Add file → Upload files**
- Drag and drop all files and folders

### Step 4 — Add Your Product Photos
1. In your repo, open the `photos/` folder
2. Upload your product images here
3. File names must match what's in `products.json` (e.g., `diya_set.jpg`)

### Step 5 — Edit products.json
Update `products.json` with your actual product names, taglines, and photo filenames.
Example:
```json
{
  "products": [
    {
      "id": "p001",
      "name": "Your Product Name",
      "tagline": "Your catchy tagline! 🎁",
      "contact": "WhatsApp: +91-XXXXXXXXXX",
      "photo": "your_photo.jpg"
    }
  ]
}
```

### Step 6 — Add GitHub Secrets
1. In your repo → **Settings → Secrets and variables → Actions**
2. Click **New repository secret** and add these two:

| Secret Name | Value |
|---|---|
| `SHOTSTACK_API_KEY` | Your Shotstack sandbox API key |
| `GITHUB_REPO_RAW` | `https://raw.githubusercontent.com/YOUR_USERNAME/return-gift-videos/main` |

> Replace `YOUR_USERNAME` with your actual GitHub username!

### Step 7 — Enable GitHub Actions
1. Go to the **Actions** tab in your repo
2. Click **Enable Actions** if prompted
3. Done! ✅

---

## ⏰ When Does It Run?

| Time | IST | What happens |
|---|---|---|
| 9:00 AM | Morning | Picks a product, generates video, logs the URL |
| 6:00 PM | Evening | Picks a different product, generates another video |

---

## 📺 Where Are My Videos?

After each run:
1. Go to **Actions** tab → Click the latest workflow run
2. Scroll to the **Generate promo video** step
3. Look for: `🎬 Video ready: https://...`
4. Open that URL to download your MP4!

You can also check `video_log.json` in your repo — it keeps a history of all video URLs.

---

## 🔧 Trigger a Video Manually
Go to **Actions → Generate Product Promo Video → Run workflow**
You can even specify a product ID (e.g. `p001`) to generate a video for a specific product.

---

## 📸 Photo Tips for Best Results
- Use JPG or PNG format
- Minimum 800x800 pixels
- Clean background (white or light solid color)
- Good lighting — no shadows
- Keep file size under 5MB

---

## 🆓 Free Tier Limits

| Service | Free Limit |
|---|---|
| Shotstack | Watermark-free sandbox renders; upgrade for production |
| GitHub Actions | 2,000 minutes/month (you'll use ~5 min/day = 150 min/month ✅) |

---

## ❓ Troubleshooting

**Video shows a watermark?**
You're on the sandbox/free tier — this is expected for testing.
To remove it, upgrade to Shotstack's paid plan.

**Workflow fails with "API key not found"?**
Check that your `SHOTSTACK_API_KEY` secret is set correctly in GitHub Settings.

**Photos not loading in video?**
Make sure your repo is **Public** and the photo filenames exactly match `products.json`.
